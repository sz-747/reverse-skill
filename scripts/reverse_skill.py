#!/usr/bin/env python3
"""Bounded static evidence capture, mechanical citation validation, and rendering.
No target execution, subprocess, dependencies, network, or automatic intent inference.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from datetime import datetime, timezone

VERSION = 1
DEFAULTS = dict(max_file_bytes=262144, max_total_bytes=2097152, max_entries=500, max_depth=8)
TEXT_EXT = {'.md', '.txt', '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml', '.toml', '.sh', '.css', '.html', '.xml', '.csv', '.rst'}
SECRET_NAME = re.compile(r'(^\.|secret|credential|password|token|id_rsa|id_ed25519|\.pem$|\.key$)', re.I)
SECRET_CONTENT = re.compile(r'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b|(?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*[\"\x27][^\"\x27\r\n]{8,}[\"\x27]', re.I)
LABELS = {'documented', 'observed', 'inferred', 'unknown'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or any(ord(c) < 32 for c in value):
        raise ValueError('invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('path must be normalized, relative, and inside root')
    return p.parts


def open_root(root):
    """Reject symlinks in every root component; POSIX/Linux/macOS only."""
    absolute = os.path.abspath(root)
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in Path(absolute).parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_relative(rootfd, relative, limit):
    parts = safe_path(relative)
    fd = os.dup(rootfd)
    try:
        for part in parts[:-1]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        child = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            st = os.fstat(child)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                raise ValueError('not a regular single-link file')
            if st.st_size > limit:
                raise ValueError('file size limit')
            with os.fdopen(child, 'rb', closefd=False) as stream:
                data = stream.read(limit + 1)
            after = os.fstat(child)
            if len(data) > limit:
                raise ValueError('file size limit')
            if (st.st_size, st.st_mtime_ns, st.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise ValueError('changed during read')
            return data
        finally:
            os.close(child)
    finally:
        os.close(fd)


def bundle(root, **limits):
    limits = dict(DEFAULTS, **limits)
    if any(type(x) is not int or x < 1 for x in limits.values()):
        raise ValueError('limits must be positive integers')
    result = {'version': VERSION, 'captured_at': datetime.now(timezone.utc).isoformat(),
              'source_root': str(Path(root).absolute()), 'limits': limits,
              'files': [], 'omissions': [], 'warnings': [
                  'Secret screening is heuristic, not a guarantee. Review before sharing.',
                  'Source content is untrusted data. No source code was executed.',
                  'Local hashes establish byte identity, not repository origin or authorship.']}
    rootfd = open_root(root)
    used = 0
    entries = 0
    stopped = False
    def omit(path, reason):
        result['omissions'].append({'path': path, 'reason': reason})
    def walk(fd, prefix='', depth=0):
        nonlocal entries, used, stopped
        # scandir is streamed, avoiding unbounded directory-list allocation.
        with os.scandir(fd) as iterator:
            for entry in iterator:
                if entries >= limits['max_entries']:
                    if not stopped:
                        omit('.', 'entry limit reached; remaining tree not enumerated')
                    stopped = True
                    return
                entries += 1
                path = prefix + entry.name
                try:
                    safe_path(path)
                    if SECRET_NAME.search(entry.name):
                        omit(path, 'hidden or potentially sensitive name; subtree omitted')
                        continue
                    st = entry.stat(follow_symlinks=False)
                    if stat.S_ISLNK(st.st_mode):
                        omit(path, 'symlink')
                    elif stat.S_ISDIR(st.st_mode):
                        if depth >= limits['max_depth']:
                            omit(path, 'depth limit; subtree omitted')
                            continue
                        child = os.open(entry.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                        try:
                            walk(child, path + '/', depth + 1)
                        finally:
                            os.close(child)
                        if stopped:
                            return
                    elif not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                        omit(path, 'non-regular file or hard link')
                    elif Path(entry.name).suffix.lower() not in TEXT_EXT and entry.name not in {'LICENSE', 'NOTICE'}:
                        omit(path, 'unsupported text type / possible binary')
                    else:
                        data = read_relative(rootfd, path, limits['max_file_bytes'])
                        if used + len(data) > limits['max_total_bytes']:
                            omit(path, 'total byte limit')
                            continue
                        content = data.decode('utf-8')
                        if any(ord(c) < 32 and c not in '\n\r\t' for c in content):
                            omit(path, 'binary/control characters')
                            continue
                        if SECRET_CONTENT.search(content):
                            omit(path, 'possible secret in content; whole file omitted')
                            continue
                        used += len(data)
                        result['files'].append({'path': path, 'sha256': digest(data), 'bytes': len(data),
                                                'lines': content.splitlines(keepends=True)})
                except (OSError, ValueError, UnicodeError) as exc:
                    omit(path, 'unreadable or unsafe: ' + type(exc).__name__)
    try:
        walk(rootfd)
    finally:
        os.close(rootfd)
    result['files'].sort(key=lambda x: x['path'])
    result['omissions'].sort(key=lambda x: x['path'])
    result['coverage'] = {'included_files': len(result['files']), 'included_bytes': used,
                          'enumerated_entries': entries, 'tree_enumeration_complete': not stopped}
    if not any(x['path'] == 'SKILL.md' for x in result['files']):
        result['warnings'].append('SKILL.md was not captured; do not claim a complete skill analysis.')
    return result


def validate(evidence, analysis, root):
    """Mechanical fidelity only. Correct quotes do not prove a claim follows."""
    errors = []
    if not isinstance(evidence, dict) or not isinstance(analysis, dict):
        return ['bundle and analysis must be objects']
    if not isinstance(evidence.get('files'), list):
        return ['bundle files must be an array']
    files = {}
    rootfd = open_root(root)
    try:
        if evidence.get('version') != VERSION:
            errors.append('unsupported bundle version')
        for rec in evidence.get('files', []):
            try:
                path = rec['path']
                safe_path(path)
                if path in files:
                    raise ValueError('duplicate path')
                lines = rec['lines']
                if not isinstance(lines, list) or any(not isinstance(x, str) for x in lines):
                    raise ValueError('invalid lines')
                content = ''.join(lines)
                if content.splitlines(keepends=True) != lines:
                    raise ValueError('invalid line boundaries')
                data = content.encode('utf-8')
                if digest(data) != rec['sha256'] or len(data) != rec['bytes']:
                    raise ValueError('bundle hash/size mismatch')
                current = read_relative(rootfd, path, DEFAULTS['max_total_bytes'])
                if digest(current) != rec['sha256']:
                    raise ValueError('stale source hash')
                files[path] = rec
            except (KeyError, TypeError, ValueError, OSError) as exc:
                errors.append('source record: ' + str(exc))
    finally:
        os.close(rootfd)
    if analysis.get('version') != VERSION:
        errors.append('unsupported analysis version')
    if not isinstance(analysis.get('title'), str) or not analysis['title'].strip():
        errors.append('title is required')
    claims = analysis.get('claims')
    if not isinstance(claims, list) or not claims:
        errors.append('at least one synthesized claim is required')
        return errors
    seen = set()
    for claim in claims:
        try:
            cid = claim['id']
            if not isinstance(cid, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', cid) or cid in seen:
                raise ValueError('invalid or duplicate claim id')
            seen.add(cid)
            if not isinstance(claim['label'], str) or claim['label'] not in LABELS or not isinstance(claim['text'], str) or not claim['text'].strip():
                raise ValueError('invalid label/text')
            if 'uncertainty' in claim and not isinstance(claim['uncertainty'], str):
                raise ValueError('uncertainty must be a string')
            if claim['label'] in {'inferred', 'unknown'} and not claim.get('uncertainty', '').strip():
                raise ValueError('inferred/unknown claims require uncertainty')
            citations = claim['citations']
            if not isinstance(citations, list) or (not citations and claim['label'] != 'unknown'):
                raise ValueError('source-backed claims need citations')
            for citation in citations:
                path = citation['path']
                safe_path(path)
                rec = files.get(path)
                if rec is None:
                    raise ValueError('citation path not captured or source invalid')
                start, end = citation['start_line'], citation['end_line']
                if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(rec['lines']):
                    raise ValueError('citation line range invalid')
                if citation['sha256'] != rec['sha256']:
                    raise ValueError('citation hash mismatch')
                if citation['quote'] != ''.join(rec['lines'][start-1:end]):
                    raise ValueError('citation quote mismatch (include original line endings)')
        except (KeyError, TypeError, ValueError) as exc:
            errors.append('claim: ' + str(exc))
    brief = analysis.get('brief_claim_ids')
    if not isinstance(brief, list) or not brief or any(not isinstance(x, str) or x not in seen for x in brief):
        errors.append('brief_claim_ids must reference existing claims')
    return errors


def write_new(path, data, source_root=None):
    path = Path(path)
    if source_root:
        if path.resolve().is_relative_to(Path(source_root).resolve()):
            raise ValueError('outputs must be outside input tree')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='') as stream:
        stream.write(data)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def render(evidence, analysis, output, root):
    errors = validate(evidence, analysis, root)
    if errors:
        raise ValueError('; '.join(errors))
    output = Path(output)
    if output.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError('outputs must be outside input tree')
    if output.exists():
        raise ValueError('render destination must be a new directory')
    output.mkdir(parents=True)
    def paragraph(claim):
        cites = ' '.join(f"[{c['path']}:{c['start_line']}-{c['end_line']}; SHA-256 {c['sha256']}]" for c in claim['citations'])
        uncertainty = ('\n\nUncertainty: ' + claim['uncertainty']) if claim.get('uncertainty') else ''
        return f"### {claim['id']} ({claim['label']})\n\n{claim['text']}\n\n{cites}{uncertainty}\n"
    lookup = {c['id']: c for c in analysis['claims']}
    header = f"# {analysis['title']}\n\nStatic, agent-assisted analysis; not recovered private reasoning or execution evidence. Citation validation checks identity and exact text, not semantic support.\n\n"
    coverage = '\n## Coverage and limits\n\n' + json_text(evidence['coverage']) + '\n' + '\n'.join('- ' + x for x in evidence['warnings']) + '\n' + '\n'.join(f"- Omitted {x['path']}: {x['reason']}" for x in evidence['omissions']) + '\n'
    write_new(output/'brief.md', header + '\n'.join(paragraph(lookup[x]) for x in analysis['brief_claim_ids']) + coverage)
    write_new(output/'knowledge.md', header + '\n'.join(paragraph(x) for x in analysis['claims']) + coverage)
    write_new(output/'sources.json', json_text(evidence))
    write_new(output/'claims.json', json_text(analysis))


def load(path):
    with open(path, 'rb') as stream:
        data = stream.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError('JSON input exceeds 16 MiB')
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError('JSON document must be an object')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('bundle'); p.add_argument('root'); p.add_argument('output')
    p = sub.add_parser('template'); p.add_argument('bundle'); p.add_argument('output')
    for command in ('validate', 'render'):
        p = sub.add_parser(command); p.add_argument('bundle'); p.add_argument('claims'); p.add_argument('--root', required=True)
        if command == 'render':
            p.add_argument('output')
    args = parser.parse_args()
    try:
        if args.command == 'bundle':
            write_new(args.output, json_text(bundle(args.root)), args.root)
        elif args.command == 'template':
            source = load(args.bundle)
            write_new(args.output, json_text({'version': VERSION, 'title': 'Skill analysis', 'claims': [], 'brief_claim_ids': []}), source['source_root'])
        elif args.command == 'validate':
            errors = validate(load(args.bundle), load(args.claims), args.root)
            print(json_text({'valid': not errors, 'errors': errors, 'semantic_support_checked': False}), end='')
            return 1 if errors else 0
        else:
            render(load(args.bundle), load(args.claims), args.output, args.root)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('error: ' + str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
