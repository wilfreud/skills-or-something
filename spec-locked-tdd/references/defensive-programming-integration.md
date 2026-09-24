# Integrating TDD with Defensive Programming / Tiger Style

TDD and defensive programming solve different failure classes and reinforce each other.

- **TDD** asks: what observable behavior must the system provide, and what evidence would detect its absence?
- **Defensive programming** asks: what assumptions, bounds, invalid states, and failure conditions must the implementation make explicit at runtime and in types?

Use them together without collapsing them into one mechanism.

## Translation table

| Defensive-design concept | TDD expression |
| --- | --- |
| Preconditions | invalid-input tests; type-level impossibility where feasible |
| Postconditions | observable result/state assertions |
| Invariants | example tests + property/fuzz tests + runtime assertions |
| Negative space | tests for forbidden transitions/states and explicit errors |
| Pair assertions across boundary | contract/integration tests at both sides of the boundary |
| Bounded work | boundary tests for maximum sizes/counts/time/retries |
| Every error checked | failure-path tests and explicit error assertions |
| Strong types | compile-time constraints plus runtime tests at untyped boundaries |
| Small functions | focused tests around public behavior; avoid testing private helpers merely because they are small |

## Recommended design sequence

1. Build the mental model of the feature.
2. Enumerate positive behavior and negative space.
3. Encode domain impossibilities with types where practical.
4. Decide which assumptions deserve runtime assertions.
5. Convert observable contracts into tests.
6. Prove RED.
7. Implement with explicit assertions/errors/types.
8. Keep tests focused on externally meaningful behavior rather than asserting that defensive checks happen to be written a particular way.

## Avoid duplicate assurance theater

Do not add a unit test for every individual assertion simply to increase count. Test the domain behavior that makes the assertion meaningful.

Conversely, do not remove production assertions merely because a test covers the same case. Tests protect development/change; runtime assertions protect execution assumptions in deployed code.
