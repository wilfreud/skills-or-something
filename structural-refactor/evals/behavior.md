# Behavioral Evals

These scenarios define the skill's intended behavior. They are not an automated benchmark by themselves; turn them into repository-specific eval prompts as the skill evolves.

## Case 1 — giant but cohesive parser

**Input:** a 3,500-line parser/state machine with one grammar, one state model, minimal public API, strong tests, and tightly shared invariants.

**Expected:** flag size as a triage signal but do not recommend arbitrary file splitting. Explain why shared invariants and a narrow interface may make the module deep/cohesive. Look for internal clean seams only if they reduce dependency/cognitive cost. A valid result can be `LEAVE` with a deviation note.

**Failure:** "3,500 lines is too large; split every 500 lines."

## Case 2 — AI-accreted god service

**Input:** a 2,800-line `OrderService` mixing order transitions, pricing, payment reconciliation, PDF generation, persistence queries, email/WhatsApp, and reporting.

**Expected:** identify semantic clusters, state/invariant ownership, and dependency clusters. Recommend a directed target topology only for seams that reduce knowledge leakage. Keep use-case orchestration coherent. Avoid one-file-per-method and generic helpers.

**Failure:** create 20 services/interfaces solely to reduce file length.

## Case 3 — fragmented codebase

**Input:** 40 classes under 100 LOC, many forwarding calls, interfaces with one implementation, shared DTOs leaking everywhere, and deep call stacks.

**Expected:** detect classitis/pass-through structure and consider merging/deepening modules. The skill must not equate more files with cleanliness.

**Failure:** recommend more extraction because some methods exceed a preferred size.

## Case 4 — unclear seam

**Input:** a 1,200-line component with mixed concerns but heavy shared mutable state and no reliable tests.

**Expected:** `WATCH` or high-risk `REFACTOR` with characterization tests and a staged plan; do not mutate aggressively until behavior and invariant ownership are understood.

**Failure:** shotgun refactor followed only by a compile check.

## Case 5 — transaction boundary

**Input:** a service method performs validation, writes three tables in one transaction, emits an outbox event, and returns a DTO. Proposed extraction would move one write outside the transaction.

**Expected:** stop or redesign the seam to preserve atomicity. Treat transaction semantics as observable behavior.

**Failure:** accept the split because responsibilities look cleaner.

## Case 6 — circular dependency

**Input:** `AService -> BService -> AService` currently resolved with framework lazy/forward references.

**Expected:** analyze responsibility direction. Consider an application-level orchestrator, shared responsibility extraction, or dependency inversion only where a real abstraction exists. Do not treat the framework workaround as the architectural solution.

**Failure:** preserve the cycle and merely move code into more files.

## Case 7 — large refactor mixed with feature

**Input:** user asks to add a feature and "while there" split a 2,000-line service.

**Expected:** separate conceptual changes when practical: preparatory/structural refactor with green behavior, then feature change. If user explicitly needs one patch, keep phases distinct and verify after each.

**Failure:** mix renames, architecture changes, dependency updates, and feature logic into one opaque diff.

## Case 8 — metric false positive

**Input:** inventory flags a generated client, migration bundle, or large static mapping.

**Expected:** classify generated/declarative bulk separately and avoid normal semantic refactoring unless the source generator/design is in scope.

**Failure:** hand-edit generated files to satisfy thresholds.

## Case 9 — co-change signal

**Input:** two modules are statically separate but change together in most commits because they encode opposite halves of the same invariant.

**Expected:** investigate whether they should share one owner or a deeper module. Temporal coupling is evidence, not proof.

**Failure:** automatically merge every high co-change pair.

## Case 10 — behavior-preserving completion

**Input:** a valid refactor is implemented.

**Expected:** run formatter/lint/typecheck/tests/build as applicable, inspect diff, check dependency direction/cycles, and summarize what changed structurally and what behavior was explicitly preserved.

**Failure:** report success because the code compiles.
