---
name: structural-refactor
description: Audit and refactor structurally degraded codebases by detecting multi-responsibility hotspots, semantic seams, change amplification, coupling, oversized files/classes/functions, god objects, and AI-generated accretion. Use when the user asks to inspect, split, reorganize, simplify, or refactor a codebase without changing behavior, especially when files have grown very large or module boundaries are unclear. Supports a read-only audit mode and a behavior-preserving refactor mode. Do not use for formatting-only cleanup, broad style policing, or ordinary feature work.
compatibility: Requires repository read access. Git history is recommended but optional. Use the repository's own build, lint, typecheck, and test tools when available.
metadata:
  version: "1.0.0"
---

# Structural Refactor

Reduce structural complexity without turning one large mess into many small ones.

The objective is not "clean code" as an aesthetic. The objective is a codebase whose boundaries match its responsibilities, invariants, data ownership, effects, and change patterns while preserving observable behavior.

## Core doctrine

1. **Semantic boundaries beat line counts.** LOC is a triage signal, never a verdict. A 2,000-line cohesive module may be healthier than twenty 100-line pass-through modules.
2. **Prefer cohesion and information hiding.** A useful module owns meaningful knowledge or a design decision behind a narrower interface.
3. **Minimize change amplification.** A small conceptual change should not require edits across unrelated files.
4. **Avoid interface inflation.** Do not create classes, services, interfaces, repositories, factories, helpers, or adapters merely to make files shorter.
5. **Preserve behavior during refactoring.** Structural work and feature work are different modes. Keep them separate unless the user explicitly asks otherwise.
6. **Use multiple signals.** Never diagnose structural debt from a single metric. Combine structural, semantic, evolutionary, and verification evidence.
7. **Prefer explicit reasoning over pattern cargo culting.** Name the responsibility, invariant, dependency, or failure mode that motivates an extraction.
8. **Small steps, always verifiable.** Make one conceptual transformation at a time and verify it before continuing.

This skill borrows process discipline from MISRA, Power of Ten, and TigerStyle, but it does **not** claim MISRA compliance and must not mechanically apply safety-critical rules to ordinary application code.

## Choose the operating mode

### Audit mode — read only

Use when the user asks to inspect, assess, find hotspots, propose segmentation, or decide what should be refactored.

- Do not modify source files.
- Repository-native read-only commands are allowed.
- Produce evidence, natural seams, rejected splits, risk, and a refactoring sequence.
- If the request is ambiguous, default to audit before mutation.

### Refactor mode — behavior preserving

Use only when the user explicitly asks to implement, split, refactor, reorganize, or fix the structure.

- Preserve observable behavior and public contracts unless the user explicitly approves a contract change.
- Do not mix unrelated features, bug fixes, formatting sweeps, dependency upgrades, or stylistic rewrites into the same change.
- Keep the repository working after each conceptual step whenever practical.

## Before analysis or mutation

1. Read repository guidance (`AGENTS.md`, `CONTRIBUTING`, architecture docs, package manifests, build files, lint/test config).
2. Identify language/framework conventions and existing module boundaries before proposing new ones.
3. Inspect `git status` when Git is available. Never discard or overwrite user changes.
4. Discover the repository's verification commands. Prefer declared scripts/configuration over guessed commands.
5. In refactor mode, establish a baseline: run the smallest relevant test/typecheck/build set that demonstrates the current target is green. If the baseline is already failing, record that fact and avoid attributing pre-existing failures to the refactor.

## Audit procedure

### 1. Map the repository

Understand the topology before judging individual files:

- application/domain/infrastructure boundaries;
- entry points and public APIs;
- state owners and persistence boundaries;
- external effects: DB, network, filesystem, queues, clocks, randomness;
- dependency direction;
- test topology;
- generated/vendor/migration files that should not be treated like ordinary hand-maintained code.

For a large repository, `scripts/repo_inventory.py` can rank source files by objective size/control-flow/import signals. Treat its output as triage only.

### 2. Generate hotspot candidates from converging evidence

Read `references/hotspot-signals.md` when auditing more than a single obvious file.

Look for combinations of:

- large or unusually complex files/functions/classes;
- many unrelated dependencies or effect types;
- unrelated domain vocabularies in one unit;
- multiple independent reasons to change;
- state/invariants owned in one place but manipulated from many conceptual areas;
- high fan-out, cycles, pass-through layers, or information leakage;
- repeated edits across supposedly independent modules;
- high churn or temporal coupling in Git history;
- duplication that reflects duplicated knowledge rather than merely similar syntax;
- weak test seams around risky code.

Do **not** turn these into a fake precision score. Evidence should converge before recommending structural change.

### 3. Infer semantic clusters

For each candidate, group functions/types/state by what they actually do and what knowledge they share.

A proposed cluster is a credible extraction only when most of these hold:

- it has one coherent responsibility that can be named without `and`;
- its members share data, invariants, policy, or dependencies more strongly with each other than with the rest;
- it owns a meaningful design decision or domain concept;
- it can expose a narrower, stable interface;
- moving it reduces dependency surface or change amplification;
- it does not require excessive parameter threading or duplicated state;
- its behavior can be verified independently or through existing callers.

### 4. Apply the anti-fragmentation test

Reject or reconsider an extraction if it:

- creates a thin wrapper whose interface is nearly as complex as its implementation;
- simply forwards the same arguments through another layer;
- moves code only because of a line threshold;
- separates code that must share the same invariant or mutable state;
- introduces a dependency cycle;
- produces generic dumping grounds such as `utils`, `helpers`, `common`, or `manager` without a cohesive abstraction;
- decomposes by execution chronology rather than by hidden knowledge/responsibility;
- causes more cross-file navigation and coordination than it removes;
- invents an architecture the current problem does not require.

Sometimes the right structural refactor is to **merge** tiny leaking modules, not split a large one.

### 5. Classify the candidate

Use one of these actions, with evidence and confidence:

- **LEAVE** — large or unusual, but cohesive; splitting would increase interface/dependency complexity.
- **WATCH** — suspicious, but the semantic boundary is not yet strong enough to justify mutation.
- **REFACTOR** — multiple responsibilities or hidden dependencies have a credible, lower-coupling seam.

Also classify mutation risk as **LOW / MEDIUM / HIGH** based on affected public APIs, shared mutable state, persistence/transactions, concurrency, framework lifecycle, and external effects.

### 6. Produce an audit report

Use this shape:

```text
# Structural Audit

Scope:
Verification baseline:
Repository notes:

## Hotspots
| Target | Evidence | Semantic clusters | Action | Risk | Confidence |

## Target: <path>
Current responsibility:
Observed hidden responsibilities:
Natural seams:
Rejected splits:
Dependency/invariant concerns:
Suggested target topology:
Refactor sequence:
Verification needed:
Deviation note (if intentionally left large):
```

For every recommendation, explain **why the boundary is semantically useful**, not merely how many lines it removes.

## Refactor procedure

Read `references/refactoring-protocol.md` before modifying a high-risk hotspot.

### 1. Freeze the behavioral contract

Identify observable behavior that must remain stable:

- public function/API signatures;
- HTTP/GraphQL/RPC contracts;
- persistence semantics and transaction boundaries;
- emitted events/messages;
- ordering, idempotency, retries, time behavior where relevant;
- error behavior;
- framework lifecycle/DI behavior.

If relevant behavior lacks tests and the proposed move is risky, add focused characterization/regression tests **before** structural mutation when feasible. Do not rewrite behavior to make tests easier.

### 2. State the intended seam before editing

Write down:

- responsibility being extracted or consolidated;
- knowledge/invariant it owns;
- dependencies it should own;
- dependencies that must remain outside;
- minimal interface between old and new structures;
- alternatives rejected and why.

If this cannot be stated clearly, do not extract yet.

### 3. Refactor in microsteps

Prefer a sequence such as:

1. isolate or characterize current behavior;
2. move pure/low-effect logic first when that reveals the seam;
3. move the data/invariants with the behavior that owns them when safe;
4. redirect existing callers without redesigning their contracts unnecessarily;
5. remove transitional forwarding code once no longer needed;
6. simplify imports/dependencies exposed by the move;
7. only then consider local naming/readability cleanup inside the changed area.

Do not perform speculative abstraction. Do not create an interface simply because a concrete class exists. Do not introduce a design pattern unless it solves an observed dependency or variation problem.

### 4. Verify after each conceptual change

Use the repository's own tools. The expected stack, when available, is:

1. formatter/check formatting for touched files;
2. lint/static analysis;
3. typecheck/compile;
4. focused tests;
5. broader relevant tests;
6. build/package verification;
7. inspect `git diff` and dependency direction.

A compile success alone is not behavioral verification.

If a step fails, diagnose before continuing. Do not pile more refactors on top of an unverified state.

### 5. Re-audit the result

After the change, verify that the new structure actually improved the system:

- fewer unrelated reasons to change per module;
- narrower interfaces;
- no new cycle;
- no duplicated state or invariant;
- less parameter plumbing/pass-through code;
- dependencies align with ownership;
- tests still express behavior rather than implementation details;
- total navigation/cognitive overhead did not increase merely because file count increased.

If the extraction made the system shallower, more coupled, or harder to understand, revert that extraction rather than defending it because it looks "clean".

## Deviation notes

Borrow MISRA's discipline of explicit deviations without claiming MISRA compliance.

When a suspicious structure is intentionally retained, record:

```text
Deviation: <target>
Trigger: <which heuristic/signals fired>
Decision: leave as-is
Rationale: <why the current structure is more cohesive / lower risk>
Risks considered: <coupling, state, tests, public API, etc.>
Revisit when: <specific future condition, if any>
```

This prevents "large file = bad" from becoming a blind rule while keeping the decision reviewable.

## Hard stop conditions

Stop and report rather than forcing a refactor when:

- the baseline is red and the failure materially obscures verification;
- the behavior or public contract cannot be determined with reasonable confidence;
- the proposed seam would split one invariant across owners;
- a move changes transaction/concurrency semantics that the user did not authorize;
- the only justification is file length, a metric threshold, or stylistic preference;
- the change would overwrite unrelated user work;
- the refactor would require a broad architecture migration outside the requested scope.

## Supporting material

Load supporting files only as needed:

- `references/decision-model.md` — theory and decision criteria: Parnas, Ousterhout, Fowler, TigerStyle, MISRA-inspired process discipline.
- `references/hotspot-signals.md` — structural, semantic, evolutionary, and verification signals; how to avoid metric cargo culting.
- `references/refactoring-protocol.md` — detailed behavior-preserving mutation protocol and high-risk cases.
- `references/evidence.md` — research and practitioner sources behind this skill, including current AI-generated-code evidence and caveats.
- `evals/behavior.md` — adversarial scenarios that define what this skill should and should not do.
- `evals/triggers.csv` — routing cases for skill selection.

Use scripts only for deterministic mechanics. Semantic interpretation belongs to the model.
