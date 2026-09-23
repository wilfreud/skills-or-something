# Behavior-Preserving Refactoring Protocol

Use this when the target has persistence, concurrency, framework lifecycle, external effects, or a large semantic move.

## Phase 0 — establish control

Before editing:

- inspect `git status`;
- identify user changes and avoid them;
- record the exact target scope;
- identify verification commands and current baseline;
- identify externally observable contracts;
- note generated files that must not be edited directly.

Do not begin a broad structural refactor from a dirty mental model.

## Phase 1 — characterize behavior

Write down the target's contracts in concrete terms.

For application/backend code, check:

- inputs and validation;
- returned values/statuses/errors;
- persistence writes and transaction boundaries;
- event/message emission and ordering;
- retry/idempotency behavior;
- time/clock behavior;
- side effects and calls to external systems;
- cache invalidation;
- authorization/tenant boundaries;
- framework lifecycle hooks.

For UI code, check:

- rendered states;
- events/user interactions;
- data fetching/caching;
- URL/navigation behavior;
- loading/error/empty states;
- accessibility semantics where relevant.

If no test protects the behavior crossing the seam, add a focused characterization test when feasible. A characterization test records current observable behavior; it does not bless the internal design.

## Phase 2 — design the seam

Describe the proposed module with four statements:

1. **Owns:** the responsibility/knowledge/invariant it controls.
2. **Receives:** the minimum information it needs.
3. **Returns/emits:** the minimum result or effect needed by callers.
4. **Does not know:** details intentionally hidden from it.

If "Receives" is nearly the entire old object's state or "Does not know" is empty, the extraction is probably shallow.

### Keep invariants with their owner

If a set of fields must change atomically or obey a shared invariant, prefer one owner. Splitting methods while leaving mutable state shared across modules often worsens reasoning.

### Keep transaction semantics explicit

Do not move a DB operation across a transaction boundary without explicit authorization and regression coverage. A prettier service topology is not worth altered atomicity.

### Keep concurrency semantics explicit

Moving code across async tasks, locks, queues, transactions, worker boundaries, or event handlers can change ordering and race behavior even when types compile. Treat this as a behavior change unless proven otherwise.

## Phase 3 — transform incrementally

A safe order is often:

1. Rename nothing unless needed to expose the seam.
2. Add/strengthen behavior-level tests if needed.
3. Extract pure calculations/policy with identical signatures where possible.
4. Move tightly coupled state/invariants together rather than leaving cross-file mutation.
5. Introduce the smallest caller boundary.
6. Redirect one caller path at a time if the framework permits.
7. Verify.
8. Remove obsolete forwarding/duplicate code.
9. Verify again.
10. Only then perform local readability cleanup in touched code.

Avoid a giant "new architecture" branch followed by one final test run.

## Phase 4 — verify dimensions separately

### Behavior

- focused tests green;
- broader relevant tests green;
- externally visible outputs unchanged.

### Type/build integrity

- typecheck/compiler green;
- build/package succeeds;
- framework DI/module graph resolves.

### Structural integrity

- no new dependency cycles;
- interface is narrower or knowledge leakage is lower;
- no duplicated state/invariant;
- no new generic dumping ground;
- no explosion of pass-through layers;
- no unnecessary public exports.

### Diff integrity

Inspect the diff for accidental:

- API changes;
- default changes;
- error-message/status changes that matter to callers;
- reordered side effects;
- altered transaction boundaries;
- unrelated formatting/renaming;
- deleted comments explaining invariants;
- generated-file edits.

## Common extraction patterns

Use patterns only when the evidence matches.

### Policy from orchestration

Good when pure rules/decisions change independently of I/O orchestration. Keep the orchestration at the use-case boundary and make policy inputs explicit.

Bad when the "policy" abstraction simply mirrors every field/dependency from the orchestrator.

### External effect adapter

Good when a provider/API/database detail is a volatile implementation decision and can be hidden behind a stable domain-facing operation.

Bad when an interface is invented with one implementation and no hidden detail or test seam benefit.

### Cohesive sub-domain service/module

Good when a large service contains a cluster with its own vocabulary, invariants, state, dependencies, and change reasons.

Bad when the split is merely CRUD-by-entity or "one service per noun" without an actual ownership boundary.

### Orchestrator/use-case extraction

Good when several existing components need a single directed workflow and bidirectional service dependencies can be replaced by orchestration above them.

Bad when the new orchestrator becomes another god object that absorbs all policy.

### Merge shallow modules

Good when multiple modules leak the same knowledge, co-change, or exist primarily as pass-through wrappers.

## Framework-specific cautions

### Dependency injection frameworks

- preserve provider scope/lifecycle;
- avoid creating cycles to "solve" a large service;
- do not use lazy/forward references as a substitute for dependency-direction design;
- preserve module export visibility unless intentionally changed.

### ORMs / persistence layers

- preserve unit-of-work/transaction behavior;
- avoid accidental N+1 or query-order changes;
- do not relocate lazy-loaded access without checking runtime semantics.

### Frontend frameworks

- avoid splitting a component into tiny components if it causes prop drilling or hides one cohesive interaction model;
- distinguish visual composition seams from state-ownership seams;
- preserve hook lifecycle/order rules.

## Completion criterion

A refactor is complete only when the repository is green *and* the new structure has a defensible semantic boundary. Passing tests can show preserved behavior; they do not prove the design is better. Re-audit the boundary.
