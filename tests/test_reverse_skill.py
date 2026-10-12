import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/reverse_skill.py'
spec = importlib.util.spec_from_file_location('reverse_skill', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base/'input'
        self.root.mkdir()
        (self.root/'SKILL.md').write_bytes(b'---\r\nname: sample\r\n---\r\nRead first.\r\nThen inspect.\n')
        self.evidence = r.bundle(self.root)
        self.rec = self.evidence['files'][0]
        self.claims = {'version': 1, 'title': 'Sample', 'claims': [
            {'id': 'read-first', 'label': 'documented', 'text': 'The procedure says to read first.',
             'citations': [{'path': 'SKILL.md', 'start_line': 4, 'end_line': 4,
                            'sha256': self.rec['sha256'], 'quote': 'Read first.\r\n'}]}],
             'brief_claim_ids': ['read-first']}

    def tearDown(self):
        self.tmp.cleanup()

    def errors(self, evidence=None, claims=None):
        return r.validate(evidence or self.evidence, claims or self.claims, self.root)

    def test_end_to_end_preserves_bytes(self):
        before = (self.root/'SKILL.md').read_bytes()
        self.assertEqual(self.errors(), [])
        r.render(self.evidence, self.claims, self.base/'output', self.root)
        self.assertEqual(before, (self.root/'SKILL.md').read_bytes())
        self.assertEqual(''.join(self.rec['lines']).encode(), before)
        self.assertIn('read-first', (self.base/'output/brief.md').read_text())
        self.assertIn(self.rec['sha256'], (self.base/'output/knowledge.md').read_text())

    def test_fabricated_citations_rejected(self):
        for field, value in [('path','missing.md'), ('path','../outside.md'), ('path','/etc/passwd'),
                             ('path','a\\b.md'), ('start_line',0), ('start_line',True),
                             ('end_line',999), ('quote','Read first.\n'), ('sha256','0'*64)]:
            with self.subTest(field=field, value=value):
                claims = copy.deepcopy(self.claims)
                claims['claims'][0]['citations'][0][field] = value
                self.assertTrue(self.errors(claims=claims))

    def test_stale_source_detected(self):
        (self.root/'SKILL.md').write_text('changed')
        self.assertIn('stale source hash', ';'.join(self.errors()))

    def test_tampered_bundle_detected(self):
        b = copy.deepcopy(self.evidence)
        b['files'][0]['lines'][3] = 'Invented\r\n'
        self.assertTrue(self.errors(evidence=b))

    def test_bogus_line_boundaries_detected(self):
        b = copy.deepcopy(self.evidence)
        b['files'][0]['lines'] = [''.join(self.rec['lines'])]
        self.assertTrue(self.errors(evidence=b))

    def test_inferred_requires_uncertainty(self):
        self.claims['claims'][0]['label'] = 'inferred'
        self.assertTrue(self.errors())
        self.claims['claims'][0]['uncertainty'] = 'The author did not state this reason.'
        self.assertEqual(self.errors(), [])

    def test_malformed_records_and_uncertainty(self):
        for value in (None, {}, 4, []):
            with self.subTest(value=value):
                c = copy.deepcopy(self.claims)
                c['claims'][0]['uncertainty'] = value
                self.assertTrue(self.errors(claims=c))
        for value in (None, 'not an object', 4, []):
            c = copy.deepcopy(self.claims)
            c['claims'] = [value]
            self.assertTrue(self.errors(claims=c))
            b = copy.deepcopy(self.evidence)
            b['files'] = [value]
            self.assertTrue(self.errors(evidence=b))
        b = copy.deepcopy(self.evidence)
        b['files'] = None
        self.assertTrue(self.errors(evidence=b))

    def test_unknown_may_record_gap(self):
        self.claims['claims'][0].update(label='unknown', uncertainty='No rationale was found.', citations=[])
        self.assertEqual(self.errors(), [])

    def test_empty_template_is_not_success(self):
        self.assertTrue(self.errors(claims={'version':1,'title':'Sample','claims':[],'brief_claim_ids':[]}))

    def test_symlinks_and_hardlinks_excluded(self):
        outside = self.base/'outside.md'
        outside.write_text('must not capture')
        (self.root/'link.md').symlink_to(outside)
        (self.root/'linked-dir').symlink_to(self.base, target_is_directory=True)
        os.link(outside, self.root/'hard.md')
        result = r.bundle(self.root)
        self.assertEqual([x['path'] for x in result['files']], ['SKILL.md'])
        self.assertEqual(len(result['omissions']), 3)
        linkroot = self.base/'alias'
        linkroot.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError):
            r.bundle(linkroot)

    def test_replaced_source_with_symlink_rejected(self):
        outside = self.base/'outside.md'
        outside.write_bytes((self.root/'SKILL.md').read_bytes())
        (self.root/'SKILL.md').unlink()
        (self.root/'SKILL.md').symlink_to(outside)
        self.assertTrue(self.errors())

    def test_secret_binary_and_size_omissions(self):
        (self.root/'.env').write_text('password=hidden')
        (self.root/'credentials.json').write_text('{}')
        (self.root/'data.md').write_bytes(b'hello\x00world')
        (self.root/'huge.md').write_bytes(b'a'*1000)
        (self.root/'settings.py').write_text('api_key = "abcdefghijklmnop"')
        (self.root/'picture.png').write_bytes(b'PNG')
        (self.root/'foreign.md').write_bytes(b'\xff\xfe')
        result = r.bundle(self.root, max_file_bytes=100)
        self.assertEqual(len(result['files']), 1)
        self.assertEqual(len(result['omissions']), 7)
        self.assertNotIn('abcdefghijklmnop', json.dumps(result))

    def test_tree_and_total_limits(self):
        for i in range(10):
            (self.root/f'{i}.md').write_text('a'*20)
        limited = r.bundle(self.root, max_entries=3)
        self.assertFalse(limited['coverage']['tree_enumeration_complete'])
        self.assertEqual(limited['coverage']['enumerated_entries'], 3)
        limited = r.bundle(self.root, max_total_bytes=10)
        self.assertEqual(limited['files'], [])
        folder = self.root/'a'/'b'
        folder.mkdir(parents=True)
        (folder/'deep.md').write_text('x')
        limited = r.bundle(self.root, max_depth=1)
        self.assertIn('depth limit; subtree omitted', [x['reason'] for x in limited['omissions']])

    def test_special_file_does_not_block(self):
        os.mkfifo(self.root/'pipe.md')
        result = r.bundle(self.root)
        self.assertIn('non-regular file or hard link', [x['reason'] for x in result['omissions']])

    def test_target_code_not_executed(self):
        marker = self.base/'executed'
        (self.root/'run.py').write_text(f'open({str(marker)!r}, "w").write("executed")')
        result = r.bundle(self.root)
        self.assertFalse(marker.exists())
        self.assertIn('run.py', [x['path'] for x in result['files']])

    def test_outputs_do_not_overwrite_or_enter_input(self):
        with self.assertRaises(ValueError):
            r.write_new(self.root/'output.json', '{}', self.root)
        with self.assertRaises(FileExistsError):
            r.write_new(self.root/'SKILL.md', 'bad')
        with self.assertRaises(ValueError):
            r.render(self.evidence, self.claims, self.root/'output', self.root)

    def test_cli_pipeline(self):
        bundle = self.base/'bundle.json'
        claims = self.base/'claims.json'
        def run(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *map(str,args)], capture_output=True, text=True)
        self.assertEqual(run('bundle',self.root,bundle).returncode,0)
        self.assertEqual(run('template',bundle,claims).returncode,0)
        self.assertEqual(run('validate',bundle,claims,'--root',self.root).returncode,1)
        claims.write_text(json.dumps(self.claims))
        self.assertEqual(run('validate',bundle,claims,'--root',self.root).returncode,0)
        self.assertEqual(run('render',bundle,claims,self.base/'rendered','--root',self.root).returncode,0)
        self.assertEqual(run('bundle',self.root,bundle).returncode,2)

if __name__ == '__main__':
    unittest.main()
