---
name: spec-locked-tdd
description: Drive feature additions, behavior changes, and bug fixes through a specification-locked TDD workflow. Use when the user asks for TDD, red-green-refactor, tests before implementation, behavior/invariant-driven development, regression-first bug fixing, or when coding agents must be prevented from weakening tests merely to make a change pass. Shape observable behavior, derive invariants and a risk-based test portfolio, prove RED, lock the test oracle, implement the minimum GREEN change, refactor only while green, and verify at broader boundaries. Pairs well with defensive/assertion-heavy skills such as tiger-style. Do not use for pure research, docs-only edits, or throwaway spikes unless explicitly requested.
---

# Spec-Locked TDD

Use tests as an executable specification and feedback mechanism, not as a post-hoc ceremony or a coverage game.

The governing loop is:

**Shape -> Select behavior -> RED -> LOCK -> GREEN -> REFACTOR -> VERIFY -> repeat.**

A green suite is evidence, not proof. Never treat “all tests pass” as sufficient if the tests can be weak, stale, over-mocked, or edited to match the implementation.

## 0. Establish the working context

Before changing behavior:

1. Read repository instructions (`AGENTS.md`, `CONTRIBUTING`, test docs, package scripts, CI config) and inspect nearby production code and tests.
2. Identify the existing test framework, naming/layout conventions, fixtures, factories, fakes, and integration-test infrastructure. Reuse them unless there is a concrete reason not to.
3. Run the narrowest relevant existing tests, or the project’s normal baseline test command when practical. Record pre-existing failures separately; do not “fix” unrelated failures as part of the feature.
4. Determine whether a companion defensive-programming skill is active. If `tiger-style` or equivalent guidance is available, use its preconditions, postconditions, assertions, bounded behavior, strong typing, and negative-space reasoning as inputs to the feature contract and test design. Do not duplicate or weaken that skill.

## 1. Shape the feature before coding

TDD requires a crisp **next observable behavior**, not a complete architecture designed upfront.

For any non-trivial behavior change, establish a compact feature contract before implementation. Use `assets/feature-contract-template.md` when a persistent artifact is useful.

Define:

- **Goal:** user/system outcome.
- **Public surface:** API, command, event, UI behavior, domain operation, or other observable interface.
- **Acceptance behaviors:** concrete Given/When/Then examples.
- **Invariants:** conditions that must always hold.
- **Forbidden states / negative space:** states, transitions, outputs, or side effects that must never occur.
- **Failure semantics:** expected errors, rejection rules, retries, idempotency, rollback/atomicity, and partial-failure behavior where relevant.
- **Boundaries:** database, filesystem, network, queue, clock, randomness, third-party API, process, or service boundary.
- **Risk notes:** money, auth, authorization, destructive operations, concurrency, privacy, security, migration compatibility, latency, or other feature-specific risks.

### Shaping gate

If a material product or domain choice is unresolved and no repository convention resolves it, do not invent an oracle and then encode it as a test. Surface the smallest decision set needed to continue.

If the task is sufficiently specified, proceed without unnecessary approval. Make assumptions explicit when they matter.

For exploratory or uncertain work, run a **spike outside the TDD loop**, discard or quarantine spike code, then convert what was learned into a feature contract before production implementation.

## 2. Build a risk-based test portfolio

Do not mechanically write every kind of test. Choose the cheapest test level that can faithfully observe each behavior.

Use `references/test-strategy.md` for selection guidance.

Default preferences:

- **Behavior-focused unit tests** for deterministic domain/application logic.
- **Property-based or fuzz tests** when stable invariants span many inputs.
- **Integration tests** when correctness depends on a real database, serialization layer, filesystem, framework configuration, transaction behavior, or infrastructure component.
- **Contract tests** at service/client/provider boundaries where mocks can drift from reality.
- **Acceptance/E2E tests** for a small number of critical user-visible journeys or cross-component behaviors.
- **Smoke tests** only as coarse “is the integrated system alive?” checks; never as a substitute for focused behavior tests.
- **Mutation testing** selectively for critical pure/domain logic or whenever ordinary coverage looks reassuring but oracle strength is uncertain.

Do not chase a fixed test pyramid ratio. Prefer small, deterministic tests, but add larger tests wherever the failure mode exists only at a real boundary.

## 3. Write tests as behavioral contracts

Tests should describe **what** the system guarantees through public/observable interfaces, not how the current implementation happens to work.

Rules:

1. Prefer one coherent behavior per test.
2. Use descriptive names that state the scenario and expected outcome.
3. Keep setup readable. In tests, clarity is usually more valuable than aggressive DRY abstraction.
4. Prefer real collaborators when they are fast, deterministic, and easy to instantiate; otherwise prefer faithful fakes. Use mocks/stubs narrowly.
5. Do not assert incidental internal calls, private methods, temporary data structures, or ordering unless they are part of the contract.
6. Test failure behavior and forbidden states, not only the happy path.
7. For a bug fix, first encode the reported bug as a regression test that fails on the current behavior.
8. Do not use snapshots as the only oracle for important behavior. Review any snapshot intentionally.
9. Never write tautological tests that reproduce the production algorithm in the test.
10. Never create an oracle solely from the implementation being written.

## 4. RED — prove the test can detect missing behavior

For the next smallest behavior:

1. Write the smallest test or test slice that expresses it.
2. Run that test immediately.
3. Confirm it **fails for the expected semantic reason**.

A compile/import failure can be a legitimate first RED when the new public API does not exist yet, but reach a behavioral failure as soon as possible.

If the test unexpectedly passes, stop and investigate. Possible explanations:

- behavior already exists;
- the test does not exercise the intended path;
- the assertion is too weak;
- setup bypasses the behavior;
- the specification is stale or redundant.

Do not implement until the RED signal is understood.

## 5. LOCK — protect the oracle before implementation

Once RED is established, the meaning of the specification and failing test is frozen for the current slice.

When practical, run this skill’s deterministic guard:

```bash
python scripts/spec_lock.py lock \
  --spec path/to/feature-contract.md \
  --tests path/to/relevant-test-file
```

If the skill lives outside the repository, invoke the script using its actual skill path. The command writes `.tdd-spec-lock.json` in the current working directory by default.

During GREEN, **do not**:

- delete the failing test;
- weaken, remove, or invert an assertion;
- broaden accepted outputs merely to include the implementation’s output;
- add `skip`, `xfail`, `.only`, retries, sleeps, or arbitrary timeout/tolerance increases to obtain green;
- blindly update snapshots;
- replace a faithful dependency with a mock that simply returns the desired answer;
- add production fallbacks/defaults that hide an invalid state solely to satisfy a test;
- swallow errors or silently coerce invalid input solely to satisfy a test;
- edit the feature contract so that the current implementation becomes “correct.”

Run:

```bash
python scripts/spec_lock.py check
```

before declaring the slice complete.

The script is a guardrail, not a security boundary. A coding agent can still edit or delete it; process discipline and review remain necessary.

## 6. GREEN — implement the minimum behavior

Write the smallest production change that makes the current RED behavior pass while respecting existing contracts.

- Keep the diff local.
- Re-run the focused test frequently.
- Do not preemptively implement later test cases unless the design naturally covers them.
- Do not perform broad refactors while RED.
- Do not add speculative abstractions “for future flexibility.”
- Preserve strong typing, explicit errors, assertions, bounds, and defensive checks required by the domain or companion defensive-programming skill.

A minimal implementation does **not** mean a hack. It means no behavior or abstraction beyond what current evidence requires.

## 7. REFACTOR — improve design only while green

After focused tests are green:

1. Remove duplication and accidental complexity.
2. Improve names and responsibility boundaries.
3. Extract concepts only when the code now demonstrates the abstraction.
4. Keep public behavior unchanged.
5. Run the focused tests after each meaningful refactor step.
6. Re-run `spec_lock.py check` after refactoring.

If refactoring requires changing a behavior test, determine whether the test was coupled to implementation details. Fix that coupling through the **Spec Revision Protocol** rather than casually editing the test.

## 8. Spec Revision Protocol

Sometimes the test or specification is genuinely wrong. Test immutability is not dogma; **silent oracle mutation is forbidden**.

If new information invalidates a locked expectation:

1. Stop implementation work.
2. State exactly which assumption/requirement is wrong and why.
3. Classify the change:
   - **Harness correction:** import/setup/framework mistake that does not alter behavioral meaning.
   - **Specification revision:** acceptance behavior, invariant, failure semantics, or allowed output changes.
4. For a specification revision, update the feature contract first.
5. Record the reason when unlocking:

```bash
python scripts/spec_lock.py unlock --reason "<why the oracle must change>"
```

6. Update the affected tests.
7. Re-run them and, where possible, demonstrate a meaningful RED against the current implementation.
8. Re-lock and resume GREEN.

A harness correction may be made without product-level approval if behavioral meaning is unchanged, but it must still be called out in the final evidence report.

## 9. VERIFY — broaden confidence by risk

When the focused slice is green and refactored:

1. Check the spec lock.
2. Run all directly related unit tests.
3. Run relevant integration/contract tests for touched boundaries.
4. Run the smallest acceptance/E2E or smoke path needed for cross-component confidence.
5. Run type checking, static analysis, linting, and build checks used by the repository.
6. For critical logic, consider mutation testing or property/fuzz testing.
7. For concurrency, distributed state, retries, idempotency, transactions, or failure recovery, add targeted tests at the level where those properties are observable.

Do not claim correctness from line coverage. Coverage can reveal unexecuted code; it cannot establish that assertions are meaningful.

## 10. Repeat in small, uniform slices

Prefer many short Red/Green/Refactor cycles over a giant batch of tests followed by a giant implementation.

For a larger feature:

- keep a test list / behavior checklist;
- anchor the feature with one acceptance behavior if useful;
- implement one coherent behavior at a time;
- keep every intermediate state buildable and understandable;
- add newly discovered behaviors to the list rather than implementing them invisibly.

## 11. Required completion report

When finishing a TDD-driven change, report concise evidence:

```text
Behavior contract:
- ...

Tests added/changed:
- ...

RED evidence:
- command
- expected failure observed

GREEN evidence:
- command(s)
- result

Spec-lock status:
- unchanged | revised (reason: ...)

Broader verification:
- integration/contract/e2e/typecheck/lint/build/mutation as applicable

Residual risk / intentionally omitted tests:
- ...
```

Never say “fully correct” merely because the suite is green.

## 12. Failure-mode rules for coding agents

Read `references/agent-failure-modes.md` when the change is substantial, flaky, highly mocked, or repeatedly resists GREEN.

Escalate instead of cheating when:

- the desired behavior conflicts with existing public behavior;
- the only path to green appears to require weakening the oracle;
- an external dependency cannot be represented faithfully;
- the suite is flaky or non-hermetic;
- implementation reveals an architecture/boundary problem bigger than the requested feature;
- the contract is not deterministic enough for conventional assertions.

For nondeterministic systems (for example LLM output), replace exact-output assumptions with stable contracts: schemas, invariants, deterministic preprocessing, bounded properties, golden datasets, or explicit eval criteria. Conventional TDD still applies to deterministic surrounding code.
