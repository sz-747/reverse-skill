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

## Scope

Research is complete and a minimal agent-assisted pilot is now implemented.

1. Compare existing open-source ingestion, skill-validation, and repository-explanation tools.
2. Check the Agent Skills specification and reuse its existing discovery and progressive-disclosure conventions.
3. Choose a minimal design and a public, appropriately licensed skill for a first test.
4. Define fidelity, citation, retrieval, and security checks before implementation.

No framework, model provider, database, or multi-agent architecture is required by this brief. Prefer the smallest design that can be checked against real source files.

## Status

- Project brief recorded.
- Initial tools and standards research completed by source inspection.
- A pinned public skill has been examined as a partial worked example.
- Runnable static evidence capture, citation validation, and rendering are implemented.
- Agent-assisted synthesis is defined in [SKILL.md](SKILL.md); the Python helper does not infer author intent.
- 17 automated tests pass locally on Linux; this is not a quality benchmark or proof of semantic correctness.
- [Run the pilot](docs/pilot.md).

## Research results

- [Open-source tools and reuse options](docs/research/tools.md)
- [Standards, minimal design, worked example, and evaluation plan](docs/research/standards-and-design.md)

**Recommendation:** keep the existing Agent Skills format. Use a small read-only inventory and original-file reader, then a human- or model-assisted evidence-grounded synthesis step. Render a human brief and agent reference from the same claims. Static parsing can verify paths and source spans; it cannot determine author intent or prove that an explanation is true.

Start with Markdown and a source manifest. Optional Repomix ingestion and a skill validator may help; a wiki server, vector database, and Tree-sitter integration are not necessary until a real pilot demonstrates a need.

**Illustrative finding:** the sampled webapp-testing skill prescribes networkidle, while current Playwright documentation discourages it for testing. A trustworthy explanation must retain the original instruction and show the conflict, rather than silently rewrite the skill.

## Evaluation checkpoint

The first real-skill forward test completed: 7 captured files, 19 source-cited claims, successful capture/validation/rendering, and no source changes. Citation corruption was rejected; an unrelated statement with valid quotations still passed mechanical validation, confirming that semantic review is essential. The source was instruction-rich, so this is a favorable single case rather than a general benchmark. Measure citation fidelity, preserved conditions, source immutability, and whether the author recognises the proposed explanations. Mechanical tests cannot verify recovered intent. Keep unconfirmed personal interpretations out of public fixtures.

## License

This repository retains its existing [Apache-2.0 license](LICENSE). Upstream skills and tools keep their own licenses; reuse must be reviewed individually.
