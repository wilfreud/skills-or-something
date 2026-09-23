# Structural Refactor — Decision Model

This reference explains the design philosophy behind the skill. It is intentionally stricter about *why* to split than common "clean code" advice.

## 1. The unit of design is hidden knowledge, not file length

Parnas's information-hiding argument is the foundation: module decomposition is valuable when modules conceal design decisions likely to change. A module boundary is useful when callers need less knowledge after the boundary exists.

A good extraction therefore answers:

- What knowledge does this module own?
- What could change inside it without forcing unrelated callers to change?
- Which invariant belongs here?
- Which dependencies are implementation details that can disappear behind the interface?

A file can be long and still answer these questions well. A small file can be architecturally bad if it leaks its implementation into every caller.

## 2. Prefer deep modules over classitis

Ousterhout's modular-design framing is a direct warning against decomposition by line count. A useful module provides substantial functionality behind a relatively simple interface. Too many shallow classes/modules create coordination cost and pass-through code.

Practical consequences:

- Do not create `FooService`, `FooManager`, `FooHelper`, and `FooRepository` merely to distribute LOC.
- Do not split a cohesive state machine across files if every file must understand the same state transitions.
- Do not extract a method/class if its callers still need to know nearly all the details it supposedly hides.
- Consider merging units when information leakage or duplicated knowledge is caused by artificial separation.

## 3. Cohesion is semantic, not lexical

Two functions belong together when they participate in the same responsibility, invariant, state ownership, policy, or abstraction. Similar names or adjacent source position are weak evidence.

Useful questions:

- Do these operations need the same domain knowledge?
- Do they change for the same reason?
- Do they share invariants that must remain synchronized?
- Do they use the same dependencies because of a real responsibility, or merely because one file accumulated everything?
- Can one cluster be understood and tested without mentally simulating the others?

Avoid "temporal decomposition": do not create modules just because steps happen in sequence (`read -> parse -> validate -> store`) if this forces shared knowledge to leak through every stage.

## 4. File length is a smoke detector

LOC is cheap and useful for triage, especially in AI-accumulated codebases, but it does not identify the design problem.

Treat size as a question:

> Why is this unit large?

Possible answers include:

- it owns one intrinsically large but coherent table/state machine/protocol;
- it contains several independent domain policies;
- it combines orchestration, policy, persistence, and external effects;
- generated or declarative content inflates the count;
- repeated copy/paste has accumulated;
- the public API is broad because the abstraction itself is incoherent.

Only some of these imply splitting.

## 5. Multi-signal diagnosis

Metrics in isolation are poor design judges. Use them to generate candidates, then combine them with semantic and evolutionary evidence.

Strong evidence for refactoring usually looks like convergence, for example:

- very high churn **and** unrelated domain clusters **and** unrelated dependencies;
- a class with many methods **and** subgroups that share different fields/dependencies **and** change independently;
- two modules that are nominally separate but repeatedly co-change **and** leak the same invariant — perhaps they should be merged;
- a giant service whose orchestration, pure policy, persistence, and messaging each have distinct dependencies and tests.

A single threshold should not decide the action.

## 6. Two hats: refactor vs feature work

Refactoring is a behavior-preserving activity. Keep structural changes conceptually separate from adding or changing functionality.

Why:

- failures become attributable to the structural change;
- reviewers can reason about intent;
- diffs remain small enough to inspect;
- rollback is tractable;
- tests provide a stable oracle.

Tiny local cleanup can coexist with a feature, but a structural decomposition should generally be its own conceptual change.

## 7. Refactoring is risk-bearing work

Empirical work at Microsoft found that developers perceive real cost/risk in refactoring, while targeted refactoring efforts can reduce dependencies and defects. The lesson is not "refactor less" or "refactor more"; it is to make refactoring disciplined, scoped, and verifiable.

Therefore this skill requires:

- baseline verification;
- small transformations;
- explicit preserved behavior;
- review of the resulting dependency graph;
- stop conditions when evidence is weak.

## 8. TigerStyle / Power of Ten contribution

TigerStyle and Holzmann's Power of Ten are not general architecture standards. Their relevant contribution here is the engineering stance:

- constraints should have a reason;
- code should be analyzable;
- control flow and state ownership should be explicit;
- verification should be mechanical where possible;
- a size rule should force a better shape, not arbitrary slicing.

TigerStyle's own function-size guidance explicitly recommends meaningful decomposition rather than cutting code at a numeric boundary. This skill applies that idea at module scale.

## 9. MISRA contribution: process, evidence, deviations

MISRA Compliance is safety-oriented and C/C++-centric, but several process principles generalize well:

- guidelines need an explicit enforcement method;
- metrics identify code deserving extra review, not universal truth;
- some checks are local while others require system-wide analysis;
- tool diagnostics can be true, possible, false-positive, or genuine-but-noncompliance-neutral issues;
- deviations require rationale, scope, and risk consideration;
- late cleanup/refactoring can itself introduce defects.

This skill adopts that discipline for structural refactoring without claiming MISRA compliance.

## 10. Final decision rule

Recommend a split only when you can complete this sentence with concrete evidence:

> Extracting **X** from **Y** is expected to reduce **specific dependency/change/cognitive cost** because **X owns this responsibility/knowledge/invariant**, and the new boundary can be expressed with a **narrower interface** without duplicating state or changing behavior.

If you cannot, keep investigating or leave the code alone.
