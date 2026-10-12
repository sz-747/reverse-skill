# Minimal reverse-skill pilot

A working, read-only evidence pipeline plus an Agent Skills procedure. The Python helper does **not** infer author intent. An agent reads its bundle, synthesizes labeled claims, and reviews semantic support. The helper checks exact paths, original lines/quotes, file hashes, and current input identity before rendering two views.

## Run

Requirements: Python 3.10+ on POSIX with `O_NOFOLLOW`, directory file descriptors, and `scandir(fd)` (tested on Linux). No dependencies, network, API keys, target imports, or subprocesses.

```sh
python3 scripts/reverse_skill.py bundle /absolute/input-skill /tmp/bundle.json
python3 scripts/reverse_skill.py template /tmp/bundle.json /tmp/claims.json
# Agent fills claims.json following SKILL.md and references/claim-contract.md.
python3 scripts/reverse_skill.py validate /tmp/bundle.json /tmp/claims.json --root /absolute/input-skill
python3 scripts/reverse_skill.py render /tmp/bundle.json /tmp/claims.json /tmp/new-analysis --root /absolute/input-skill
python3 -m unittest discover -s tests -v
```

Outputs must be new paths outside the input tree; existing files are not overwritten. A populated, valid claims file is required. `validate` exits 0 on mechanical success, 1 on citation/contract failure, and 2 on invocation/read errors. The renderer produces brief.md, knowledge.md, claims.json and sources.json. Local citations carry path, inclusive lines, and full hash; preserve the input/provenance when distributing a report. No publish/install operation is included.

## Safety and bounds

- At most 500 directory entries, depth 8, 256 KiB per included file, 2 MiB total included source bytes. Directory enumeration is streamed. Omitted directories report the subtree omission, not a fictitious inventory.
- Symlink components in the input path are rejected; target symlinks, hard links, special files, hidden paths, credential-like names, unsupported extensions, binary/control characters and recognizable secrets are omitted. UTF-8 only. A file replaced during reading is rejected when its stat changes.
- No source script or repository configuration is executed. Source text can contain prompt injection; the agent must treat it as evidence.
- Secret detection is deliberately conservative and heuristic, can overexclude harmless examples, and cannot guarantee no sensitive content. Review before giving a bundle to a third party. File names in omissions may themselves be sensitive.
- Run against a quiescent, authorized snapshot, with output storage under your control. This is a small static-analysis utility, not a hostile multi-user filesystem sandbox or production secret scanner. It does not protect against all concurrent directory renames, malicious mounts, resource exhaustion in adversarial caller-supplied JSON, or concurrent attacks on output directories.
- Validation checks every captured file, but not new additions or omitted bytes. Rebundle after inventory changes. It rejects stale/fabricated evidence but cannot prove that an interpretation logically follows. Source hash authenticity, authorship, legal reuse rights, completeness and model quality require review.

## Basis and license

Original implementation of the minimal design researched for https://github.com/sz-747/reverse-skill. The repository was research/design, not a converter; this pilot does not imply a pre-existing reverse-skill executable. Packaging/integration into that Apache-2.0 repository is left to the maintainer. No target skill code is copied into this implementation and no target licenses are changed. Captured sources retain their own license obligations; review before redistributing sources.json.
