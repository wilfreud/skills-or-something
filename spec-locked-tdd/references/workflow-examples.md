# Workflow Examples

## Example A — New deterministic feature

Task: add proration to subscription cancellation.

1. Shape the contract: effective date, money rounding, forbidden negative refund, idempotency, already-cancelled behavior.
2. Create a test list.
3. Pick the smallest behavior: cancellation on the billing boundary yields zero prorated refund.
4. Write the test and prove RED.
5. Lock spec + test.
6. Implement minimum behavior.
7. Prove GREEN and check lock.
8. Refactor.
9. Repeat for mid-cycle refund, repeated cancellation, invalid dates, currency rounding.
10. Run DB/payment integration tests because unit mocks cannot validate persistence/transaction assumptions.

## Example B — Regression bug

Task: duplicate webhook deliveries create duplicate invoices.

1. Reproduce the duplicate delivery in a regression test. It must fail before the fix.
2. State the invariant: one external event identity may create at most one invoice.
3. Lock the regression test.
4. Implement idempotency at the correct boundary, not a fixture-specific special case.
5. Add a real persistence integration test for the unique/idempotency mechanism.
6. Consider concurrent-delivery coverage if races are plausible.

## Example C — Requirement discovered to be wrong during GREEN

The original test says `404` for an inaccessible resource, but project policy requires `403`.

Do not simply change the test.

1. Stop GREEN.
2. Point to the authoritative project policy.
3. Revise the feature contract.
4. Unlock with reason.
5. Change the expected behavior.
6. Demonstrate RED against current implementation.
7. Re-lock and resume.

## Example D — UI-heavy exploratory work

For an interaction with unclear UX, a short prototype may be faster than forcing exact tests before the desired behavior is understood.

1. Spike the interaction separately.
2. Decide the stable observable behaviors: disabled states, keyboard behavior, submission semantics, loading/error transitions.
3. Discard/quarantine spike code.
4. Enter the normal TDD workflow for production implementation.

## Example E — LLM/non-deterministic output feature

Do not write brittle exact-string assertions for open-ended model output.

Instead TDD the deterministic shell:
- schema validation;
- prompt/input construction;
- tool permission rules;
- retries/timeouts;
- redaction;
- caching/idempotency;
- model routing.

For semantic quality, use a stable eval dataset/rubric or bounded properties and report that evidence separately from ordinary unit tests.
