# Structural Hotspot Signals

Use this reference for repository-wide audits. The goal is to *prioritize reading*, not to automate architecture decisions.

## Signal families

### A. Structural signals

Candidate-generating signals include:

- file LOC / nonblank LOC;
- function or method length;
- branch/nesting/cyclomatic or cognitive complexity from language-native tools;
- number of public exports/methods;
- number and diversity of imports/dependencies;
- fan-out and fan-in;
- dependency cycles;
- count of effectful dependencies (DB, HTTP, queue, filesystem, clock, cache, email, payment provider, etc.);
- deep call chains dominated by pass-through forwarding;
- duplicate or near-duplicate logic.

Do not equate import count with coupling or LOC with poor design. They are screening signals.

### B. Semantic signals

These are usually more important than raw metrics:

- multiple distinct domain vocabularies in one unit;
- methods partition cleanly into clusters with different fields/dependencies;
- orchestration mixed with business policy and infrastructure details;
- one file owns unrelated state machines;
- unrelated failure modes are handled together;
- a change in one concept repeatedly risks another concept;
- generic names (`manager`, `helper`, `utils`) hide several unrelated reasons to change;
- a unit's public API cannot be summarized as one coherent capability.

Ask whether the code has one responsibility with many cases, or many responsibilities. Those are different.

### C. Evolutionary signals

Version history can reveal coupling that static structure misses:

- high churn / repeated edits;
- files that change together unusually often;
- a supposedly independent module that almost always changes with another;
- repeated bug-fix clusters across the same group of files;
- one hotspot that attracts unrelated feature additions over time.

`scripts/git_coupling.py` can surface file pairs that co-change. Treat results as hypotheses: test files, generated artifacts, schema+client pairs, migrations, and lockfiles can co-change for legitimate reasons.

### D. Verification signals

Refactoring risk increases when:

- behavior is weakly tested;
- tests assert implementation details rather than externally meaningful behavior;
- transactional/concurrent behavior has no regression coverage;
- public contracts are undocumented;
- framework lifecycle/DI behavior is implicit;
- the target has pre-existing failing tests or type errors.

Coverage percentage alone is not a verdict. The question is whether the behavior crossing the proposed seam has a trustworthy oracle.

## Candidate prioritization without fake scoring

Prefer an evidence matrix instead of one aggregate "cleanliness score":

| Candidate | Structural | Semantic | Evolutionary | Verification risk | Interpretation |
|---|---|---|---|---|---|
| A | high | high | high | medium | inspect first |
| B | high | low | low | low | probably large but cohesive |
| C | medium | high | high | high | likely structural debt; refactor carefully |

Confidence comes from independent signals agreeing.

## Relative metrics beat universal thresholds

When possible, compare a candidate to its own repository:

- top-N largest source files;
- outliers relative to median/percentiles;
- highest churn files;
- highest dependency fan-out;
- longest functions in the same language/module type.

Universal thresholds can be useful as triage defaults, but never as architecture rules. A generated parser, schema, protocol table, or cohesive state machine may legitimately be an outlier.

## Semantic clustering checklist

For a large class/service/file, make a scratch table:

| Member/region | Reads/writes state | Dependencies | Domain concept | Effects | Changes with |
|---|---|---|---|---|---|

Then look for blocks with stronger internal relationships than external relationships.

High-quality seam indicators:

- shared invariant;
- shared owned data;
- shared policy vocabulary;
- shared effect boundary;
- shared change reason;
- stable narrow input/output.

Weak seam indicators:

- adjacent source lines;
- same prefix in function names;
- same lifecycle phase only;
- same framework decorator;
- similar syntax;
- arbitrary target LOC.

## Large-file triage categories

Classify *why* a file is large before acting:

1. **Cohesive depth** — one concept, substantial implementation, simple interface. Usually LEAVE.
2. **Responsibility accretion** — unrelated concepts appended over time. Usually REFACTOR.
3. **Generated/declarative bulk** — schemas, mappings, generated clients, fixtures. Usually exclude or treat separately.
4. **Duplicated knowledge** — repeated logic/cases. Consider consolidation before splitting.
5. **God object/service** — broad state + broad dependencies + broad public API. Strong candidate, but plan carefully.
6. **Orchestrator with many collaborators** — may be legitimate if it contains little policy and has a simple use-case-level responsibility. Do not split merely for dependency count.
7. **Fragmentation already present** — many tiny pass-through modules. Consider merging or deepening modules.

## Tool strategy

Prefer language-aware tools already present in the repository. Examples of useful categories:

- compiler/typechecker;
- lint/static analysis;
- cyclomatic/cognitive complexity analyzer;
- dependency/cycle analyzer;
- duplication detector;
- coverage/test runner;
- Git history.

If no suitable tool exists, use simple inventory scripts only to narrow the reading set. Never pretend a regex approximation is a semantic analyzer.
