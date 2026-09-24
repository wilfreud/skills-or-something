# Reading List and Design Sources

This skill is intentionally based on a mixture of canonical TDD literature, large-scale engineering guidance, test-design references, and current research on LLM-driven development.

## Canonical TDD and test design

- Kent Beck — *Test Driven Development: By Example* (Addison-Wesley/Pearson). Canonical Red/Green/Refactor treatment and small-step examples.
- Steve Freeman & Nat Pryce — *Growing Object-Oriented Software, Guided by Tests* (Addison-Wesley/Pearson). Feedback-driven design, acceptance tests, “walking skeleton,” behavior-oriented unit tests, and listening to test pain as design feedback.
- Gerard Meszaros — *xUnit Test Patterns: Refactoring Test Code* (Addison-Wesley). Extensive vocabulary for test smells, fixtures, doubles, and maintainable automated tests.
- Michael Feathers — *Working Effectively with Legacy Code* (Prentice Hall). Characterization tests, seams, and safe change in systems not originally designed for testability.
- Martin Fowler — “Test Driven Development.” https://martinfowler.com/bliki/TestDrivenDevelopment.html
- Martin Fowler — “The Practical Test Pyramid.” https://martinfowler.com/articles/practical-test-pyramid.html

## Google engineering guidance

- *Software Engineering at Google*, Chapter 11 — Testing Overview. https://abseil.io/resources/swe-book/html/ch11.html
- *Software Engineering at Google*, Chapter 12 — Unit Testing. https://abseil.io/resources/swe-book/html/ch12.html
- *Software Engineering at Google*, Chapter 13 — Test Doubles. https://abseil.io/resources/swe-book/html/ch13.html
- *Software Engineering at Google*, Chapter 14 — Larger Testing. https://abseil.io/resources/swe-book/html/ch14.html

Core ideas carried into this skill: tests should enable change with confidence; test observable behavior rather than implementation details; keep tests clear; use doubles cautiously; and use larger tests when the real failure mode lies beyond a unit boundary.

## AWS / Amazon guidance

- AWS Prescriptive Guidance — Test-driven development (TDD) for AWS CDK applications. https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-cdk-typescript-iac/test-driven-development.html
- AWS Well-Architected Framework — REL08-BP02 Integrate functional testing as part of deployment. https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_tracking_change_management_functional_testing.html
- Amazon Builders’ Library — collection of Amazon engineering practices, including automated testing and safe deployment material. https://aws.amazon.com/builders-library/

## Test effectiveness

- Stryker Mutator documentation — mutation testing. https://stryker-mutator.io/docs/mutation-testing-elements/mutation-testing/

Mutation testing is included as an optional oracle-strength check, not as a mandatory percentage target.

## LLM + testing research

- *Test-Driven Approaches to Software Engineering with Large Language Models: A Survey of Phases, Tasks, and Agent Skills* (2026, arXiv:2609.12012). Highlights distinctions among test availability, test validity, feedback use, and evaluation independence; test passing alone does not establish correctness or process adherence.
- *A Dissection of Test-Driven Development: Does It Really Matter to Test-First or to Test-Last?* Empirical evidence that process granularity and uniformity can matter as much as strict sequencing, reinforcing this skill’s emphasis on small, steady feedback loops rather than ritual.
- *Test Smells in LLM-Generated Unit Tests* (2024). Useful motivation for explicit quality checks against weak, long, ambiguous, or otherwise low-value generated tests.

## Skill authoring

- OpenAI — Build skills. https://learn.chatgpt.com/docs/build-skills

The skill uses progressive disclosure: `SKILL.md` contains the operational loop, deeper material lives under `references/`, deterministic behavior lives under `scripts/`, and the reusable feature contract lives under `assets/`.

## Companion defensive-programming source

- `wilfreud/skills-or-something` — `defensive-programming/SKILL.md` (“tiger-style”). https://github.com/wilfreud/skills-or-something/tree/main/defensive-programming

This skill does not duplicate Tiger Style. It translates its assertions, strong types, pre/postconditions, bounded behavior, and negative-space reasoning into test-design inputs.
