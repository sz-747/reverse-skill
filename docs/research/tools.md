# Open-source tooling for reverse-skill analysis

Research date: 2026-10-12. Scope: public primary repositories, official documentation, selected implementation files, and release/commit history. No candidate was installed, executed, benchmarked, or authenticated during this review. Findings are source inspection, not a security audit or performance certification. Links to `main` are moving references; adoption should pin and recheck a release/commit.

## Conclusion

The strongest fit is a small, modular combination: a static skill inventory/reference check, selective source ingestion, and a custom evidence-backed synthesis layer. No inspected tool supplies the complete combination of a 3–5-minute human briefing and discoverable agent knowledge while reliably distinguishing documented rationale from analyst inference.

Start research/design around **skill-validator + a minimal original-file reader**, with **Repomix as an optional ingestion adapter**. Borrow the citation-checking ideas from DeepWiki-Open. Add Tree-sitter only when real scripts make syntax-aware extraction necessary. A wiki server, vector database, and repository-wide agent are not prerequisites for testing the idea on one real skill.

These are analytical recommendations, not implementation commitments.

## Six candidates

### 1. Repomix: strongest general-purpose ingestion adapter

- **What is verified:** Selective include/ignore patterns, file paths, token accounting, XML/Markdown/JSON output, Secretlint-based secret screening, and optional Tree-sitter compression are documented. The inspected package is version 1.18.1, MIT-licensed, requiring Node ≥22. [Repository](https://github.com/yamadashy/repomix), [package manifest](https://raw.githubusercontent.com/yamadashy/repomix/main/package.json).
- **Fit:** Convenient adapter for mixed Markdown, scripts, and manifests. Useful for inventory and selected evidence bundles, rather than loading its whole-repository dump into every agent context.
- **Important implementation detail:** `fileProcess.ts` trims content before adding line numbers and suppresses numbering for compressed output. Removing comments/blank lines can also change source coordinates. Consequently, its displayed numbers should not automatically become original-file citations. Anchor claims against untouched files and preserve hashes/commit IDs. [Inspected transformation code](https://raw.githubusercontent.com/yamadashy/repomix/main/src/core/file/fileProcess.ts).
- **Maturity/security:** Current release notes show active fixes. Version 1.18.1 fixes command execution through crafted local `.git/config`; older local-directory workflows need particular caution. Ordinary clones and its remote workflow were not affected by that specific issue. [Release](https://github.com/yamadashy/repomix/releases/tag/v1.18.1), [security advisory](https://github.com/yamadashy/repomix/security/advisories/GHSA-4p5g-gh74-q524).
- **Burden:** Low-to-moderate Node dependency footprint; no LLM or embedding service is needed merely to pack files. It does not explain design rationale or validate whether a generated explanation is true.

### 2. agent-ecosystem/skill-validator: best directly relevant analyzer

- **What is verified:** MIT Go CLI/library; structure/frontmatter, broken internal links, orphan references, token counts, Markdown checks, and JSON/Markdown reports. Installation options include Go and Homebrew. Stable packages have a semantic-versioning commitment; the LLM judge is explicitly experimental. [Repository and stability policy](https://github.com/agent-ecosystem/skill-validator).
- **Fit:** Especially useful for discovering the skill's referenced-file graph before summarization. The inspected orphan checker uses a breadth-first traversal, path-string matching, and Python-import matching. This is actual static implementation, not merely a prompt. [Orphan analysis source](https://github.com/agent-ecosystem/skill-validator/blob/main/structure/orphans.go).
- **Limits:** Textual reachability does not establish runtime behavior or complete dependencies. Dynamic imports, generated paths, and non-Python module systems need separate treatment. Density and LLM-quality scores do not prove expertise or correctness. Documented thresholds also embody the validator's preferences, not the skill author's intent.
- **Maturity:** Release page lists v1.6.2, including bounded 8 MiB skill-package reads. The browser's source-code snapshot was older than this release, so source-level details of the latest limit were not independently validated. [Releases](https://github.com/agent-ecosystem/skill-validator/releases).
- **Burden/security:** Low for static CLI checks. External-link validation performs HTTP requests; optional scoring sends content to a configured model/CLI. Those should be separate opt-in capabilities for untrusted inputs.

### 3. skills-ref: specification baseline, not production foundation

- **What is verified:** The Agent Skills specification repository contains an Apache-2.0 reference library with `validate`, `read-properties`, and `to-prompt`. Its README explicitly limits it to demonstration use and says it is not intended for production. Python virtual-environment installation is documented. [README](https://raw.githubusercontent.com/agentskills/agentskills/main/skills-ref/README.md).
- **Actual scope:** The inspected validator locates SKILL.md, parses its frontmatter, checks name/directory consistency, description/compatibility lengths, and allowed fields. It does not inspect the operating logic of scripts or recover rationale. [Validator implementation](https://raw.githubusercontent.com/agentskills/agentskills/main/skills-ref/src/skills_ref/validator.py).
- **Fit:** A useful minimal format oracle and example of discoverability through name, description, and location. Do not equate a passing check with a safe, effective, or well-explained skill.
- **Maturity:** Official reference provenance, but a deliberately limited project. The visible subtree history shows 2026 documentation/guidance changes, not evidence of a production robustness program. [History](https://github.com/agentskills/agentskills/commits/main/skills-ref).
- **Burden:** Low Python setup; no semantic index or hosted model needed for format validation. Prefer a spec-compatible small parser or a maintained checker over importing its entire demonstration library uncritically.

### 4. DeepWiki-Open: closest complete human-facing application

- **What is verified:** MIT repository with a Python backend, web frontend, RAG, wiki output, and code-guided tours. Its current README promotes Grok-Wiki; the open code remains in the repository. Backend setup requires Python dependencies plus configured model/embedding providers; Ollama is documented as a local option. [Repository](https://github.com/AsyncFuncAI/deepwiki-open), [API documentation](https://github.com/AsyncFuncAI/deepwiki-open/tree/main/api).
- **Actual citation behavior:** The codemap pipeline retrieves chunks, generates a structured skeleton, then enriches explanations/diagrams. It searches original files to correct citation line ranges. However, it falls back to matching only the snippet's first nonblank line, and unmatched citations are not rejected in the inspected function. Treat that as partial grounding, not proof that a claim is supported. [Codemap implementation](https://raw.githubusercontent.com/AsyncFuncAI/deepwiki-open/main/api/services/codemap.py).
- **Fit:** Good design reference for human navigation and source-linked steps. Its prompt explicitly asks for file paths, line ranges, and verbatim snippets, but does not provide the requested documented-versus-inferred rationale taxonomy. [Prompt source](https://raw.githubusercontent.com/AsyncFuncAI/deepwiki-open/main/api/prompts.py).
- **Maturity/burden:** Visible commits through September 2026 include citation, RAG, and logging changes. Substantial full-stack and model-runtime burden compared with a single-skill prototype. Local storage does not mean local inference when a cloud provider is configured. [Commit history](https://github.com/AsyncFuncAI/deepwiki-open/commits/main/).

### 5. Tree-sitter: optional precise script extraction

- **What is verified:** MIT incremental parsing library with language grammars, syntax-tree node positions, native bindings, and a WebAssembly route. Official parsing documentation exposes byte and row/column coordinates. [Repository](https://github.com/tree-sitter/tree-sitter), [parsing documentation](https://tree-sitter.github.io/tree-sitter/using-parsers/2-basic-parsing.html).
- **Fit:** Extract imports, functions, CLI entry points, and source spans from scripts without running the scripts. This can make evidence chunks more meaningful than arbitrary token windows.
- **Limits:** A syntax tree is not a semantic dependency graph, execution trace, or explanation of why an author chose something. Markdown headings and file paths may suffice for the first skill; adding grammars for every language too early adds avoidable complexity.
- **Maturity:** Release 0.27.1 has published assets dated 2026-10-08, plus a subsequent nightly build. This is active parser infrastructure, not a skill-analysis product. [Releases](https://github.com/tree-sitter/tree-sitter/releases).
- **Burden/security:** Moderate integration work: select bindings and trusted grammar packages, convert zero-based positions correctly, and keep original file bytes for citation verification. Parsing hostile text is still an input-processing attack surface; run with resource limits and do not load arbitrary repository-supplied plugins or native grammar code.

### 6. Gitingest: simple Python alternative, weaker maintenance evidence

- **What is verified:** MIT Python CLI/library. `ingest` returns summary, tree, and content from local paths or repository URLs; synchronous and asynchronous APIs exist. The library need not write a digest unless requested. [Repository](https://github.com/coderamp-labs/gitingest), [entry point implementation](https://raw.githubusercontent.com/coderamp-labs/gitingest/main/src/gitingest/entrypoint.py).
- **Fit:** Potentially simpler than a Node adapter if the surrounding analyzer is Python. It remains ingestion, not a source-grounded briefing or retrieval product.
- **Maturity caveat:** The inspected release page lists v0.3.1 dated 2025-07-31, and the visible main history tops out in August 2025. Thus current maintenance could not be established to the same standard as Repomix; do not describe it as recently maintained merely because the page was freshly crawled. [Releases](https://github.com/coderamp-labs/gitingest/releases), [history](https://github.com/coderamp-labs/gitingest/commits/main/).
- **Burden/security:** Low Python-library burden relative to hosting its complete web service. Evaluate local extraction separately from the hosted site. Retain original-file coordinates and explicitly check secret handling rather than assuming that a prompt-friendly digest is safe to transmit.

## Additional code-mapping reference

Aider's repository map is a useful pattern, rather than a proposed additional runtime: a compact, relevance-ranked map of classes/functions. The inspected `RepoMap` implementation retains filename/line/name/kind tags and uses Tree-sitter and cache infrastructure. It is coupled to the broader assistant, including a model token counter, so extracting the pattern may be simpler than adopting the application. Apache-2.0 license. [Design documentation](https://aider.chat/docs/repomap.html), [implementation](https://raw.githubusercontent.com/Aider-AI/aider/main/aider/repomap.py), [license](https://raw.githubusercontent.com/Aider-AI/aider/main/LICENSE.txt).

## What the missing synthesis layer must do

The following is a proposed research contract, not a claim about any existing tool:

1. Preserve originals; derive an inventory from SKILL.md, scripts, references, assets, manifests, and relevant dependency declarations. Record unread, excluded, oversized, binary, and unresolved inputs explicitly.
2. Link every factual claim to an original file span and content hash or immutable repository commit. Keep comments and documentation because these are often the only direct evidence of intent.
3. Label claims by evidence type: observed implementation; explicitly documented rationale; inferred rationale; externally established fact; unknown. An implementation choice alone does not establish its author's motive.
4. Produce a 3–5-minute human briefing: operation, relevant domain knowledge, design choices, assumptions, tradeoffs, limitations, and alternatives. Alternatives invented by analysis must be labeled as proposals; rejected alternatives count as historical facts only when documented.
5. Produce a small discoverable index plus individually retrievable source-linked chunks. Begin with headings, names, paths, keywords, and links; measure missed retrievals before introducing embeddings.
6. Leave the user's own reasoning framework undefined. A neutral evidence structure can support comparison without pretending to supply that framework.
7. Validate citations mechanically against originals and test whether the cited text actually supports the sentence. Exact text matches establish location, not logical entailment.

## Security and evaluation boundaries

- Read target content as untrusted data. Do not activate its SKILL.md instructions, source its shell files, import its Python modules, run package installation hooks, or execute its tests merely to explain it.
- Use a separate output directory, safe path resolution, symlink/traversal controls, file-size/time limits, and a fixed allowlist of parsers. Do not inherit target-repository executable configuration.
- Keep link discovery separate from link fetching. External URLs can reveal private paths/query data or target internal services; use a controlled fetcher if link verification is later added.
- A secret scanner is a useful filter, not authorization to upload a repository or proof that no sensitive data remains. Explicitly distinguish local parsing, hosted ingestion, cloud inference, and local inference.
- The smallest meaningful later evaluation is one real skill: check inventory completeness, source-span validity, documented/inferred separation, human reading time, and whether an agent retrieves the right chunk for concrete questions. No runtime-quality claim should be made until such evaluation occurs.

## Decision summary

| Need | Preferred research direction | Why defer alternatives |
|---|---|---|
| Skill inventory and reference checks | skill-validator or a small compatible static reader | skills-ref is explicitly a demonstration |
| Selected source bundles | Optional patched Repomix adapter | Full-repository context dumps conflict with selective loading |
| Original-file citations | Dedicated immutable span/hash handling | Transformed line numbers and LLM-produced citations are insufficient |
| Script-aware chunks | Tree-sitter only when needed | Adds grammars/integration complexity |
| Human briefing and rationale distinctions | Custom evidence-backed synthesis | None of the inspected tools completes this contract |
| Agent discoverability | Small index plus linked chunks first | Embeddings and a wiki service are not yet justified |
| Full navigable wiki | DeepWiki-Open as a later comparison | More deployment/model complexity than the initial question requires |

