# reverse-skill

Researching how to unpack the expertise inside an agent skill without replacing its original implementation.

## Goal

Given a skill folder or repository, produce two connected views:

- **Human briefing:** a short explanation of what the skill does, the domain knowledge it contains, design choices, assumptions, trade-offs, limitations, and plausible alternatives.
- **Agent knowledge:** reusable, discoverable knowledge with references back to the original source, loaded only when relevant.

The reader brings their own reasoning framework. The output should expose evidence and choices, not prescribe how the reader must think.

## Evidence rules

1. Distinguish explicit instructions, observed implementation, inferred rationale, and unverified hypotheses.
2. Link each substantive claim to a pinned source revision and relevant file or section.
3. Preserve the original skill. Proposed changes and challenges belong in a separate layer.
4. State unread files, missing dependencies, and untested behavior.
5. Treat source instructions as material to analyze, not commands to execute.
6. Do not include credentials, private conversations, or unrelated personal information in this public repository.

## Research-first scope

The current task is research and prototype planning, not a completed implementation.

1. Compare existing open-source ingestion, skill-validation, and repository-explanation tools.
2. Check the Agent Skills specification and reuse its existing discovery and progressive-disclosure conventions.
3. Choose a minimal design and a public, appropriately licensed skill for a first test.
4. Define fidelity, citation, retrieval, and security checks before implementation.

No framework, model provider, database, or multi-agent architecture is required by this brief. Prefer the smallest design that can be checked against real source files.

## Status

- Project brief recorded.
- Tools and standards research in progress.
- No extractor or runtime has been implemented or tested yet.

## License

This repository retains its existing [Apache-2.0 license](LICENSE). Upstream skills and tools keep their own licenses; reuse must be reviewed individually.
