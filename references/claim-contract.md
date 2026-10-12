# Claim contract (version 1)

`claims.json` is an object with `version: 1`, a nonempty `title`, `claims` (nonempty array), and `brief_claim_ids` (nonempty ordered subset of claim IDs). The template intentionally fails validation until the agent supplies real claims. Rendering repeats selected claims in the brief and all claims in the knowledge view, avoiding an uncited second summary.

Each claim has:
- `id`: unique lowercase identifier, starting with a letter, up to 64 characters; remaining characters letters, digits, or hyphens
- `label`: `documented` (explicit source statement), `observed` (static implementation reading, not runtime observation), `inferred` (analyst interpretation), or `unknown` (gap, question, conflict, or unavailable evidence)
- `text`: nonempty claim in natural language
- `uncertainty`: required nonempty string for inferred/unknown; describe the uncertainty rather than a generic disclaimer
- `citations`: array of citation objects. Required and nonempty except for unknown claims, which may explicitly record an ungrounded gap.

Each citation has `path` (normalized relative POSIX path captured in bundle), `start_line` and `end_line` (inclusive 1-based integers), `sha256` (the captured file hash), and `quote` (the complete unmodified lines, including original line endings). Obtain the quote with `''.join(record['lines'][start_line-1:end_line])`; do not retype or trim it. The full-file hash covers original UTF-8 bytes, including CRLF and BOM when present. The bundle uses Python `str.splitlines(keepends=True)` line boundaries; unusual Unicode line separators follow Python's definition, so check them before constructing external line links.

Example shape (illustrative, not valid evidence):

```json
{
  "version": 1,
  "title": "Example skill: decision model",
  "claims": [{
    "id": "separate-readiness",
    "label": "inferred",
    "text": "Separating readiness from interaction may keep failure diagnosis focused.",
    "uncertainty": "A plausible interpretation of the two phases; the source does not state this motive.",
    "citations": [{
      "path": "SKILL.md", "start_line": 1, "end_line": 1,
      "sha256": "REPLACE_WITH_CAPTURED_HASH",
      "quote": "REPLACE_WITH_COMPLETE_ORIGINAL_LINE_AND_ENDING"
    }]
  }],
  "brief_claim_ids": ["separate-readiness"]
}
```

Source identity: validate against the same unchanged input folder immediately before delivery. Hashes detect changed captured files; they are not signed provenance and do not establish completeness or authorship. Newly added files and changes in omitted files are not detected; recapture when the source inventory changes. Do not edit `bundle.json` to satisfy validation. Correct citations do not establish entailment, quality, safety, or a motive. Human/agent semantic review remains necessary.

If a claim is contradicted, preserve both source locations, explain the disagreement, and use `unknown` when the evidence cannot resolve it. External guidance requires separately inspected, dated evidence; this minimal validator accepts only captured local files, so keep an external comparison separate rather than inventing local citations.
