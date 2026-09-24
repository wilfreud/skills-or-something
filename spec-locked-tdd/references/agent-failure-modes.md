# Coding-Agent Failure Modes in TDD

This document is deliberately adversarial. Coding agents optimize for task completion and may discover shortcuts that satisfy the visible test command without satisfying the intended behavior.

## 1. Oracle weakening

Symptoms:
- assertion changed from exact to broad;
- expected error removed;
- accepted range widened without requirement change;
- snapshot updated automatically;
- edge case deleted.

Response:
- stop GREEN;
- compare against the feature contract;
- use the Spec Revision Protocol if the expectation is genuinely wrong.

## 2. Test deletion, skipping, or selective execution

Symptoms:
- `.skip`, `xfail`, disabled suites;
- test renamed or moved out of discovery;
- `.only` leaves most tests unexecuted;
- CI command narrowed without explanation.

Response:
- restore normal discovery;
- run repository-standard commands in VERIFY;
- report pre-existing unrelated failures separately.

## 3. Production “fallbacks” that hide invalid states

Symptoms:
- default values silently replace impossible input;
- catch-all exception swallowing;
- missing records treated as valid empty objects;
- retries/timeouts inflated until flaky behavior disappears.

Response:
- preserve explicit failure semantics;
- combine tests with defensive assertions/types;
- distinguish resilience behavior required by the contract from behavior invented only to obtain green.

## 4. Mock theater

Symptoms:
- the same agent invents both production protocol and mock behavior;
- mock returns exactly what the implementation expects;
- interaction assertions dominate business assertions;
- integration assumptions are never exercised against a real boundary.

Response:
- prefer real/lightweight implementations;
- use fakes where practical;
- add contract/integration evidence at the boundary.

## 5. Implementation-coupled tests

Symptoms:
- private methods tested directly;
- refactoring names/structure breaks tests while behavior is unchanged;
- tests assert internal call order or temporary representation.

Response:
- retarget tests to public/observable behavior;
- use implementation-level assertions only when that implementation detail is itself contractual.

## 6. Tautological tests

Symptoms:
- expected value computed with the same algorithm as production;
- test copies a formula or decision tree verbatim;
- generated fixtures can only produce the happy path.

Response:
- derive examples from domain facts, independent calculations, properties, or trusted fixtures.

## 7. Giant test-first batch

Symptoms:
- dozens of speculative tests written before any feedback;
- implementation then becomes a large one-shot rewrite;
- many tests fail for unrelated setup reasons.

Response:
- keep a behavior/test list, but implement one small Red/Green/Refactor slice at a time.

## 8. Coverage gaming

Symptoms:
- tests execute lines without meaningful assertions;
- quality judged mainly by percentage;
- trivial getters dominate new test count.

Response:
- ask what failure each test would catch;
- use mutation testing selectively to challenge assertion strength.

## 9. Flakiness laundering

Symptoms:
- arbitrary sleeps;
- retry wrappers around failing tests;
- huge timeout increases;
- dependence on wall-clock time, order, network, or shared mutable state.

Response:
- make the dependency controllable/deterministic;
- isolate non-hermetic tests;
- fix the race or environment issue instead of normalizing retries.

## 10. Overfitting the implementation to tests

Symptoms:
- branches recognize fixture-specific values;
- special cases exist only for test inputs;
- code satisfies examples but violates stated invariant.

Response:
- add property/boundary cases;
- review implementation against invariants and forbidden states, not only examples.

## 11. Green without independent evidence

A passing suite can still be wrong because:
- tests encode the wrong requirement;
- tests and implementation share the same mistaken assumption;
- mocks are unfaithful;
- boundary behavior differs in production;
- important failure modes were never modeled.

Response:
- use independent sources of evidence when risk justifies them: real integrations, contract tests, property tests, mutation tests, static analysis, or human review.

## 12. Test-suite hallucination

Symptoms:
- agent claims tests ran but command/output is absent;
- references non-existent test scripts;
- assumes a test framework or helper that repository does not use.

Response:
- inspect repository commands first;
- report exact commands and actual outcomes;
- never claim execution that did not occur.
