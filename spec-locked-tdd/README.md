# Spec-Locked TDD Skill

An agent skill for feature development and bug fixing with a protected test oracle.

It is designed for coding agents that are otherwise tempted to “solve” a failing test by weakening the test, broadening a fallback, updating a snapshot blindly, or over-mocking the system.

## Core protocol

```text
Shape behavior
  -> choose next observable behavior
  -> write test
  -> prove RED
  -> lock spec/test oracle
  -> implement minimum GREEN change
  -> refactor while green
  -> verify at broader boundaries
  -> repeat
```

The important addition to ordinary TDD is **LOCK**: once the failing behavior is established, semantic changes to the specification/test require an explicit Spec Revision Protocol.

## Install for Codex

Repository-local:

```bash
mkdir -p .agents/skills
cp -R spec-locked-tdd .agents/skills/spec-locked-tdd
```

User-level:

```bash
mkdir -p ~/.agents/skills
cp -R spec-locked-tdd ~/.agents/skills/spec-locked-tdd
```

Codex discovers repository skills under `.agents/skills` and user skills under `$HOME/.agents/skills`.

## Suggested companion skill

Keep `tiger-style` / defensive programming as a separate skill. Let this skill turn its invariants, preconditions, postconditions, forbidden states, and bounds into test cases and properties.

## Example prompts

```text
Implement subscription cancellation using spec-locked TDD. Shape the behavior and invariants first. Do not modify the locked test oracle during GREEN.
```

```text
Fix this billing regression using the TDD skill. Reproduce the bug as a failing test first, then implement the minimum fix and run broader billing integration tests.
```

```text
Before changing the authorization flow, use the TDD skill to derive the permission invariants, forbidden states, and the smallest faithful unit/integration test portfolio. Stop if the policy itself is ambiguous.
```

## What it does not guarantee

The lock script is not a security sandbox. An agent with filesystem access can edit the manifest, delete the script, or otherwise cheat. Its purpose is to make oracle changes explicit, detectable, and reviewable.

A green test suite is also not mathematical proof of correctness. Requirements can be wrong, mocks can drift, and tests can omit important states. The skill therefore requires risk-based integration/contract/E2E evidence and supports property/mutation testing where appropriate.
