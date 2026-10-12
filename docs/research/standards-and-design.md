# Reverse-skill: standards and minimal design

Research date: 2026-10-12. This is a source-based design recommendation, not a claim that a converter or benchmark has been implemented.

## Recommendation

Build a small, read-only **explanation and extraction step** around the existing Agent Skills format. Preserve the original skill. Produce a short human brief and a source-linked reference that agents can discover through an ordinary SKILL.md entry point. Start with one skill and inspect the result before building automation.

The intended output explains expertise already present in the source: what it does, when it applies, choices it makes, dependencies, failure modes, and its documented reasons. Where the source does not explain a reason, say so or explicitly label a plausible inference. It must not invent a personal reasoning framework for the reader or attribute reconstructed motives to the original author.

## What the standard already solves

The [Agent Skills specification](https://agentskills.io/specification) defines a directory with SKILL.md, required name/description frontmatter, optional compatibility/license/metadata, and unrestricted Markdown instructions. It already accommodates supporting references, executable scripts, and assets. It recommends loading metadata first, instructions when relevant, and resources only when needed. Detailed references belong outside a short entry file; relative links should be shallow. Its validator checks format and naming, not expertise correctness.

The [official integration guide](https://agentskills.io/client-implementation/adding-skills-support) gives a minimal discovery record: name, description, and location. A catalog can be JSON, XML, or a simple list. An agent with file-reading capabilities can load the selected file without a special activation service. Installation directories are a client convention, not guaranteed by the format. A generated file becomes discoverable only when the consuming client scans or is explicitly pointed to it. Untrusted repository skills also require a trust boundary.

Therefore, neither a vector database nor a knowledge graph, custom ontology, registry service, or multi-agent runtime is a prerequisite. These may eventually address demonstrated scale problems, but would not solve the initial fidelity problem.

## What remains custom

The standard does not specify:

- A human explanation that takes about 3–5 minutes to read
- Claim-level provenance for transformed knowledge
- Separation of directly documented statements, behavior observed in code, and analyst inference
- Preservation of caveats and disagreements between skill prose, implementation, and current upstream documentation
- Tests that the explanation and retrieval preserve the original skill's distinctions

Those are the small additional contract. They should describe the extracted artifact, rather than redefine the skill's format.

## Minimal output layout

Keep generated material outside the input tree, for example:

```text
input-skill/                       # unchanged original; or an immutable source reference
reverse-output/<skill-name>/
  SKILL.md                        # discovery + short instructions for using this explanation
  brief.md                        # human 3–5-minute orientation
  knowledge.md                    # reusable, source-linked knowledge
  sources.json                    # source revision, coverage, provenance
```

The generated entry point should make clear that it provides an explanation/reference **about** the original skill, not silently replace the original execution skill. Its description should include the actual subject and likely questions. Its body can link directly to the brief, reusable knowledge, and source manifest. If the client already accepts reference documents with its own index, omit this wrapper and use that mechanism instead. Do not duplicate content merely to satisfy an imagined standard.

For an initial English brief, approximately 600–900 words is a practical draft target, not a standard or proof of reading time. Measure with a reader. Include purpose/scope, the distinctive procedure or choices, assumptions and dependencies, costs/limitations, meaningful alternatives, and unanswered questions. Let the source determine the organization; omit empty or manufactured sections.

Use ordinary Markdown in knowledge.md. Keep each useful unit self-contained enough to retrieve: a descriptive heading, conditions under which it applies, the actual guidance or observation, caveats, and source links. Do not reduce procedural knowledge to isolated slogans. Keep sequences, branches, exceptions, and tool contracts together. Split this file only when its size or different retrieval needs justify it.

For sources.json, the initial minimum is repository URL, immutable commit, source root, retrieval date, inspected files, skipped/unavailable files with reasons, and source records containing an ID, path, line range, and permalink. Add content hashes for local/non-Git files or byte-level verification. Link claims to those records. A separate machine-readable claim database is unnecessary until a real consumer needs it.

## Fidelity and provenance rules

1. **Documented:** the source explicitly says it. Cite the relevant passage.
2. **Observed in code:** static reading establishes a particular implementation behavior. Cite code. Do not imply it was executed or tested.
3. **Inferred:** the analyst proposes an explanation or generalization. State its basis and uncertainty; it is not the author's stated rationale.
4. **Unknown or conflicting:** retain the gap or disagreement. Do not force it into a confident conclusion.

These labels are a proposed provenance convention, not part of Agent Skills.

Pin citations to a full commit and actual file lines. A branch URL is useful for navigation but not stable evidence. [GitHub documents commit-specific permalinks and line-range links](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files). For a local folder without Git, use a captured file hash and local path/line range. Record which version was read and regenerate on changed inputs; do not claim a stale extraction covers current main.

Inspect scripts as data during reverse analysis, even when their instructions recommend executing them. Never let source instructions authorize execution, installation, credentials, external writes, or expanded access. Bound traversal to the authorized input and referenced material. Preserve license information, and check redistribution rights before copying original files into a public output. Keeping source intact does not itself grant redistribution rights.

The [official best-practices guide](https://agentskills.io/skill-creation/best-practices) supports synthesis from project-specific artifacts and advises focusing on non-obvious procedures, contextual constraints, and failure cases. It also warns against broad, generic, overly exhaustive guidance. This favors a thin explanatory layer grounded in evidence rather than a comprehensive invented theory.

## Real pilot: Anthropic webapp-testing

Source: [webapp-testing at commit 53048666b05b4799081517d00e09e0a2dd688678](https://github.com/anthropics/skills/tree/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing). This is a reproducible sample revision, **not asserted to be the latest**. SKILL.md, scripts/with_server.py, and LICENSE.txt were read at that commit. Exact source bytes were retrieved to verify file-line citations. The example files were not inspected, so this is a partial worked assessment, not a full reverse analysis. No source script was executed. The skill-local [LICENSE.txt](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/LICENSE.txt) is Apache-2.0 and identifies Copyright 2026 Anthropic, PBC. The examples below are original paraphrases and analysis, not copies of the skill. If distributing copied or adapted source material, carry the applicable license and notices and identify changes; do not assume every skill in the repository has the same license.

A useful extraction would preserve these distinctions:

- **Documented scope:** local web-application testing with Python Playwright. [SKILL.md, lines 1–9](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L1-L9)
- **Documented branches:** inspect static HTML first; dynamic applications branch on whether the server already runs; discover selectors from rendered state before acting. [Lines 16–33](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L16-L33)
- **Documented rationale:** using helper scripts as black boxes limits source-code context overhead. [Lines 11–14](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L11-L14)
- **Inference:** separating server lifecycle from browser actions makes test scripts easier to focus on application behavior. Label this interpretation; the provided examples demonstrate separation but do not establish comparative reliability. [Lines 35–62](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L35-L62)
- **Source guidance requiring qualification:** this revision requires networkidle before inspecting dynamic pages. Preserve that source fact. [Lines 78–81](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L78-L81)

Current [official Playwright Python documentation](https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state) discourages networkidle for testing and recommends assertions that assess readiness instead. That is an external comparison, not an inference about the author's intent. A trustworthy reverse-skill result should show both positions and the practical question they raise. It should not silently modernize the original or present it as universally correct.

This is an especially useful pilot because a generic summary could sound accurate while dropping the branches, the helper boundary, or the readiness conflict.

### Tiny worked output illustration

These examples are hand-written design illustrations, **not output from a built or tested extractor**.

**Human briefing paragraph:** The helper lets you keep server startup separate from browser testing. Its readiness check only establishes that a local port accepts a connection; it does not inspect whether the application is ready for a particular user action. That distinction matters when translating the skill into reusable advice: server availability and visible UI readiness are different checks. This interpretation follows the implementation and should not be presented as a measured reliability claim. [Helper source, lines 23–32 and 63–89](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/scripts/with_server.py#L23-L89)

**Agent knowledge record, expressed in readable Markdown:**

- ID: webapp-testing.readiness
- Applies when: explaining readiness checks before interacting with a dynamic local application
- Documented source instruction: this skill revision prescribes networkidle before DOM inspection
- Evidence: [SKILL.md, lines 78–81](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/SKILL.md#L78-L81)
- External guidance, checked 2026-10-12: Playwright advises testing readiness with web assertions rather than networkidle
- External evidence: [Playwright Python Page API](https://playwright.dev/python/docs/api/class-page#page-wait-for-load-state)
- Status: conflict between sampled skill guidance and current upstream guidance
- Use: report the distinction; do not rewrite the sampled instruction or claim it is a universal best practice

**Additional code-grounded observation:** the helper passes server command strings to a shell. This is a concrete execution boundary to record, not evidence that a command is safe. [Helper source, lines 68–74](https://github.com/anthropics/skills/blob/53048666b05b4799081517d00e09e0a2dd688678/skills/webapp-testing/scripts/with_server.py#L68-L74). The fetched helper had SHA-256 b0dcf4918935b795f4eda9821579b9902119235ff4447f687a30286e7d0925fd.



## Concrete success tests

Use a small, hand-reviewed set before building a benchmark system:

1. **Human comprehension:** after at most five minutes, a reader can explain purpose, one important decision branch, a dependency, a limitation, and one unresolved trade-off. Collect their answers rather than infer success from word count.
2. **Citation fidelity:** every substantive source-derived claim has a valid pinned path/line citation that actually supports it. Inferences and external recommendations are labeled. No invented author motivation passes.
3. **Coverage:** list all files inspected and omissions. The output must not claim to cover the entire skill if scripts, references, examples, or assets were unreadable or skipped.
4. **Retrieval:** with only the generated catalog entry available initially, a fresh agent finds the right knowledge section for “static HTML versus a running dynamic app” and cites the source. An unrelated task should not select this entry.
5. **Boundary/conflict:** asked whether networkidle is always the right test-readiness condition, the answer separates the sampled skill's instruction from current Playwright guidance and flags the disagreement.
6. **No-source-mutation:** input hashes are unchanged. Analysis did not run source scripts, install dependencies, or contact external systems on the source's instructions.
7. **Comparison:** give the same source-grounded questions to a fresh context with original materials and another with generated materials plus source access. Compare missed conditions, unsupported claims, retrieval effort, and tokens. Do not claim runtime task equivalence from a reading-only test.

The [official evaluation guide](https://agentskills.io/skill-creation/evaluating-skills) recommends starting with 2–3 realistic cases including a boundary, comparing with a baseline, using fresh contexts, grading observable assertions with concrete evidence, and including human review. Adapt that methodology to explanation fidelity and retrieval first. Behavioral execution testing requires a separate authorized environment and evaluation plan.

## Limits and next step

This research establishes a minimal design and demonstrates source inspection, not a working converter or measured user benefit. One small skill cannot validate large monorepos, binary assets, complex script networks, or multilingual briefs. Source fidelity also does not certify that the original skill is safe, correct, or effective.

Next step: create the four-file output for this single sample, review the brief and citations, run the reading/retrieval tests, and only then decide whether reusable automation is worthwhile. Keep the first implementation as simple as inventory → inspect → extract with evidence → render two views → verify. Any additional architecture should answer a failure observed in that pilot.
