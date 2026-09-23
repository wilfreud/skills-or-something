# Evidence and Sources

This is a research synthesis, not a standards-compliance claim. Sources are grouped by what they contribute to the skill.

## Module decomposition and information hiding

### D. L. Parnas — “On the Criteria To Be Used in Decomposing Systems into Modules” (CACM, 1972)

DOI: https://doi.org/10.1145/361598.361623

Contribution: modularity depends on the *criterion* used to decompose a system; information hiding and design-decision ownership are more important than arbitrary procedural segmentation.

### John Ousterhout — Stanford CS 190, “Modular Design”

https://web.stanford.edu/~ouster/cgi-bin/cs190-spring16/lecture.php?topic=modularDesign

Contribution: minimize dependencies; prefer modules with substantial functionality behind simple interfaces; warns about thin classes/classitis; size is secondary to functionality/interface complexity; decompose long methods only when it can be done cleanly.

## Refactoring discipline

### Martin Fowler — Definition and Workflows of Refactoring

https://martinfowler.com/bliki/DefinitionOfRefactoring.html
https://martinfowler.com/articles/workflowsOfRefactoring/

Contribution: refactoring preserves observable behavior and proceeds through small transformations; “two hats” separates structural refactoring from adding functionality.

### Google Engineering Practices — Small CLs

https://google.github.io/eng-practices/review/developer/small-cls.html

Contribution: one self-contained conceptual change, separate significant refactoring from feature/bug changes, keep related tests with refactors, and use smaller changes to improve reviewability and reduce bug/rollback risk.

### Miryung Kim, Thomas Zimmermann, Nachi Nagappan — Microsoft refactoring field studies (FSE 2012; IEEE TSE 2014)

https://www.microsoft.com/en-us/research/publication/a-field-study-of-refactoring-challenges-and-benefits/
https://www.microsoft.com/en-us/research/publication/an-empirical-study-of-refactoring-challenges-and-benefits-at-microsoft/

Contribution: practitioners perceive real costs and risks in refactoring; targeted refactoring can reduce inter-module dependencies and defects; impact should be assessed multidimensionally rather than through size alone.

## Metrics and evolutionary coupling

### Radu Marinescu — “Detection Strategies: Metrics-Based Rules for Detecting Design Flaws” (ICSM 2004)

DOI: https://doi.org/10.1109/ICSM.2004.1357820

Contribution: metrics used in isolation are often too fine-grained; combine metrics into detection strategies to identify design problems. This supports the skill's multi-signal hotspot approach.

### Harald Gall, Karin Hajek, Mehdi Jazayeri — “Detection of Logical Coupling Based on Product Release History” (ICSM 1998)

DOI: https://doi.org/10.1109/ICSM.1998.738508

Contribution: release/version history can expose change patterns and logical dependencies not obvious from static code, motivating temporal-coupling analysis.

### Thomas J. McCabe — Cyclomatic Complexity (IEEE TSE, 1976) and later literature

Contribution: control-flow complexity is useful as one structural signal. This skill intentionally does not use it as a standalone architecture verdict.

## Defensive/analyzable-code traditions

### Gerard J. Holzmann — “The Power of Ten — Rules for Developing Safety Critical Code” (IEEE Computer, 2006)

https://spinroot.com/gerard/pdf/P10.pdf

Contribution: small, memorable, mechanically checkable rules aimed at analyzability; bounds, simple control flow, assertions, strict checking, constrained function size. Relevant here primarily as process/verification discipline, not as a universal application architecture guide.

### TigerBeetle — TigerStyle

https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md

Contribution: explicit bounds/invariants, simple control flow, strong reasoning about state, and an important nuance: size constraints should force meaningful decomposition rather than arbitrary slicing; centralize control/state where useful and keep leaf computations simple.

### User's earlier `tiger-style` / defensive-programming skill

https://github.com/wilfreud/skills-or-something/tree/main/defensive-programming

Contribution: already adapts Power of Ten/TigerStyle to general software pragmatically rather than dogmatically. This structural-refactor skill follows the same pattern: strong rules with explicit applicability boundaries and rationale.

## MISRA process discipline

### MISRA Compliance:2020 — “Achieving compliance with MISRA Coding Guidelines”

User-provided reference; not bundled because it is copyrighted.

Relevant contributions:

- documented development process and integrated verification;
- warning that late compliance/refactoring can introduce defects;
- metrics as a means to identify code needing extra review/testing, with thresholds determined by project context;
- distinction between local and system-wide analysis;
- enforcement plans combining tools and manual review;
- diagnostic categories that include false positives/possible violations;
- explicit deviation records with rationale, scope, risk, and precautions;
- maintainability framed in terms including modularity, analysability, modifiability, and testability;
- adopted/generated code must not be assumed benign merely because it passes a guideline set.

This skill borrows those process ideas only; it does not enforce MISRA C/C++ rules or claim compliance.

## Current evidence on LLM-generated code

### “Quality assurance of LLM-generated code: Addressing non-functional quality characteristics” — Journal of Systems and Software, 2026

https://doi.org/10.1016/j.jss.2026.112885

Contribution: a 2026 multi-method study (literature review, industry workshops, empirical patch analysis) explicitly treats maintainability, security, and performance as important non-functional QA dimensions for generated code. It supports evaluating generated code beyond functional correctness.

### Important caveat

Current studies of AI-generated code are still heterogeneous and evolving. They do **not** justify a rule such as “AI code is structurally bad” or “large files are caused by AI.” This skill is intentionally source-agnostic: it detects observable structural evidence whether code was written by a person, generated by an LLM, produced by a generator, or inherited as legacy code.

## Skill construction guidance

### OpenAI — Build Skills / Testing Agent Skills with Evals / Using Skills to Accelerate OSS Maintenance

https://developers.openai.com/plugins/build/skills
https://developers.openai.com/blog/eval-skills
https://developers.openai.com/blog/skills-agents-sdk

Contribution: keep `SKILL.md` focused; make `name`/`description` strong routing signals; use progressive disclosure with `references/` and `scripts/`; put deterministic mechanics in scripts and interpretation in the model; test direct, indirect, negative, and edge-case prompts.

### Agent Skills specification

https://agentskills.io/specification

Contribution: portable directory structure and frontmatter conventions used by this bundle.
