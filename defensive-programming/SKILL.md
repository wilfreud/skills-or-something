---
name: tiger-style
description: Defensive, assertion-heavy coding style for code that must not fail quietly — synthesized from TigerBeetle's TigerStyle guide, NASA/JPL's "Power of Ten" rules for safety-critical code, and "negative-space programming" (Hoare logic / design-by-contract). Use whenever the user asks for "TigerStyle," "negative-space," "safety-critical," "NASA style," or "defensive" code; whenever they mention Power of Ten, assertion density, or ask for assertions/preconditions/postconditions/invariants; and proactively for domains where correctness matters a lot (databases, financial/payment logic, distributed systems, embedded/firmware, untrusted-input parsers), even if they don't name the style. Also use to review code for missing bounds checks or assertions, unbounded loops/recursion, or dynamic allocation in hot paths, and to explain what "negative-space programming" really means (it's often confused online with "write less code," a different, weaker idea).
---

# Tiger Style: defensive, assertive coding

A style for code that would rather crash loudly at the first sign of trouble than silently
compute the wrong answer. It comes from three converging traditions:

1. **NASA/JPL's "Power of Ten"** (Gerard Holzmann, 2006) — ten rules for writing C for
   spacecraft, distilled from decades of postmortems on safety-critical failures.
2. **TigerStyle** — the coding style behind [TigerBeetle](https://github.com/tigerbeetle/tigerbeetle),
   a financial-transactions database, which generalizes Power of Ten beyond C and adds
   performance and developer-experience rules.
3. **Negative-space programming** — the practice of asserting what must _never_ happen, not just
   documenting what should. This is the same idea Tony Hoare formalized in 1969 as pre/postcondition
   logic (`{P} C {Q}`), rediscovered and popularized more recently under a new name.

Read `references/power-of-ten.md` and `references/tiger-style-guide.md` before writing
substantial code under this skill — they contain the full rule sets with rationale. This file
is the operating checklist. Read `references/negative-space-programming.md` when the user asks
what the term means or wants the concept explained rather than applied.

## When to reach for this style

Use it fully for: databases, storage/consensus engines, financial or payment logic, parsers of
untrusted input, embedded/firmware code, anything labeled "safety-critical," or any explicit
request for "TigerStyle" / "negative-space" / "defensive" / "Power of Ten" code.

Use it in a lighter, adapted form for ordinary application code: keep the assertion discipline,
bounded loops, and explicit error handling, but don't force zero-dependency or zero-dynamic-allocation
rules onto a typical web app or script — those two rules are about hard real-time / mission-critical
constraints and are usually the wrong trade-off outside that context. Say so if you're relaxing a rule.

## The core mental move: program the negative space

Most code documents what _should_ happen — the happy path. Negative-space programming means also
writing down, as executable checks, everything that must _never_ happen. Where a value crosses the
boundary between "valid" and "invalid" is exactly where interesting bugs live, so assert both sides:

- **Positive space**: assert the conditions you're relying on ("the list is sorted here").
- **Negative space**: assert the conditions that must be impossible ("index never exceeds length").

Do this with `assert()` (or the language's equivalent) directly in the code, not only in comments
or tests. An assertion that runs in production is a check that runs on every real execution, not
just the ones a test author thought to write. A failed assertion means the program is in a state no
one can reason about — the only correct response is to crash (or, in a caller-visible position,
return an explicit error), never to keep going with silently corrupted state.

**Important nuance:** "negative-space programming" gets used online in a second, much weaker sense
— "the code you _don't_ write" (deleting a redundant `else`, avoiding boilerplate). That's a real
and reasonable idea (less code, fewer bugs), but it's not what this skill is about and not what the
term meant originally. If the user is asking about that sense, clarify the distinction — see
`references/negative-space-programming.md`.

## Checklist: writing code under this style

Apply these in order of impact. Explain _why_ a rule applies when you use it non-obviously — don't
just impose it silently, per TigerStyle's own "always motivate, always say why."

### 1. Bound everything

- Every loop has a fixed, statically-checkable upper bound. If a loop genuinely must run forever
  (an event loop), assert that fact explicitly rather than leaving it implicit.
- No recursion (direct or indirect) where the depth isn't trivially bounded — recursion makes stack
  bounds hard to prove statically, which is exactly what Power of Ten rule 1 forbids.
- Control flow stays simple and explicit: no `goto`/`setjmp`-style jumps, no cleverness that a
  reader (or a static analyzer) has to simulate to understand.

### 2. Assert like you mean it

- Aim for a **minimum of two assertions per function** — one is rarely enough to pin down a
  function's contract.
- **Assert function arguments, return values, and pre/postconditions.** A function shouldn't
  operate blindly on data it hasn't checked.
- **Pair assertions across a boundary.** For any property you care about, assert it on both sides
  of a boundary where possible — e.g. assert data is valid right before writing it to disk, and
  again right after reading it back. Two independent checks catch what one alone would miss.
- **Split compound assertions.** Prefer `assert(a); assert(b);` over `assert(a and b)` — if it
  fails, you immediately know which condition broke.
- **Assert implications with `if`, not `or`.** `assert(!a or b)` is logically an implication but
  reads badly. Write `if (a) assert(b);` instead — it says what you mean.
- **Assert compile-time constants and invariants** where the language supports it (static
  assertions, type-level checks). These catch design-integrity bugs before the program ever runs.
- Assertions are a safety net for a mental model you already have, not a substitute for having one.
  Build the model first, then encode it as assertions, then write the code.

### 3. Treat state and memory as scarce and fixed

- Declare variables at the smallest scope that works, and minimize how many are live at once — it
  shrinks the space of ways they can be misused.
- For genuinely mission-critical / hard-real-time code: allocate all memory up front; don't
  allocate or free after initialization. For ordinary application code, relax this, but still avoid
  unbounded allocation driven directly by untrusted input.
- Prefer types that make invalid states unrepresentable (sum types, newtypes/branded types,
  parsing untrusted data into a validated type once at the boundary — "parse, don't validate")
  over re-checking the same invariant with assertions scattered through the codebase. Assertions
  and strong types are complementary: reach for the type system where the language makes it cheap,
  and use runtime assertions for what the type system can't express or for internal invariants.

### 4. Keep functions small and shaped like an hourglass

- A hard-ish limit of ~60–70 lines per function (Power of Ten: "fits on one printed page";
  TigerStyle: 70 lines) — short enough to hold the whole thing in working memory.
- Good shape: a few parameters in, a simple return type out, the substantive logic in between.
- Centralize control flow in the "parent" function; push branching logic up, push repetitive
  non-branchy logic down into small helpers ("push `if`s up and `for`s down"). Keep leaf helpers
  pure where possible.

### 5. Handle every error, check every return value

- Every non-void function's return value gets checked by its caller; every function checks the
  validity of what its caller handed it. Silently ignored errors are one of the largest empirically
  observed causes of catastrophic failures in real distributed systems — treat "the error path is
  untested" as a bug, not an acceptable gap.
- State invariants positively where you can (`if (index < length)` reads more naturally than its
  negation) — negated conditions are a common source of off-by-one and logic-inversion bugs.
- Split compound conditionals into nested `if/else` rather than one large boolean expression, so
  every case is visible and every branch is either handled or explicitly asserted unreachable.

### 6. Compile clean, depend on little

- Treat all compiler warnings, at the strictest setting available, as errors from day one.
- Be wary of adding dependencies to code under this style — each one is a supply-chain and
  correctness liability that compounds. This is a stronger stance than most projects need; apply it
  in proportion to how safety-critical the code actually is.

### 7. Names carry the mental model

- Spend real effort on names — a good name is a compressed explanation of the domain.
- Add units/qualifiers to variable names, least-significant part last (`latency_ms_max`, not
  `max_latency_ms`) — related variables then sort and align naturally.
- Don't let one name mean two different things depending on context.
- Comments explain _why_, not what the code already says; code explains _what_.

## Checklist: reviewing existing code under this style

When asked to review code against this style, scan specifically for:

- Loops or recursion without a provable bound.
- Functions with zero or one assertions where the logic clearly has more than one invariant worth
  naming.
- A value that's validated once and then trusted forever after, with no check at the point it's
  actually used (the gap between "place of check" and "place of use" is where bugs slip in).
- Return values or error results that are ignored or swallowed.
- Negated, compound conditionals that are hard to verify by eye.
- Dynamic allocation inside a hot loop or a hard-real-time path.
- A function long enough that it's doing more than one job — usually the fix is to push branching
  logic up into a parent function and non-branchy logic down into helpers, not to just split
  arbitrarily at the 70-line mark.

Report findings as a short list: what's missing, why it matters (tie it to a concrete failure mode,
not just "the style guide says so"), and a concrete suggested assertion or refactor.

## Adapting assertions to languages without a `assert()` kept in production

Many languages strip `assert()` in optimized/release builds (this is true of Zig's `ReleaseFast`,
C's `NDEBUG`, Python's `-O`, and others). Since the whole point is that assertions run in
production, check what the target language/runtime does and, if needed, write (or ask the user to
adopt) a small `assertPanic`/`invariant`-style helper that cannot be compiled out, reserved for the
checks that must never be skipped. Mention this trade-off explicitly rather than silently emitting
`assert()` calls that will vanish in production.

## Example: applying the checklist

**Input:** "Write a function that reads a batch of transfer records from a buffer and applies them
to account balances."

**Output shape** (illustrative, adapt to the actual language):

```
fn apply_transfers(transfers: []const Transfer, accounts: *AccountMap) !void {
    assert(transfers.len > 0);
    assert(transfers.len <= MAX_BATCH_SIZE); // bounded input, not "however many arrive"

    for (transfers) |transfer| {
        assert(transfer.amount > 0);          // positive space: what must hold
        assert(transfer.debit_id != transfer.credit_id); // negative space: what must not

        const debit_account = accounts.get(transfer.debit_id) orelse return error.UnknownAccount;
        const credit_account = accounts.get(transfer.credit_id) orelse return error.UnknownAccount;

        if (debit_account.balance < transfer.amount) return error.InsufficientFunds;

        debit_account.balance -= transfer.amount;
        credit_account.balance += transfer.amount;
    }

    assert(invariant_total_balance_unchanged(accounts)); // pair assertion: check the property held
}
```

Note what this demonstrates: a bounded loop, arguments asserted on entry, positive and negative
space both checked, every lookup's failure handled explicitly rather than assumed, and a
postcondition assertion that re-verifies the property the whole function exists to preserve.

## Reference files

- `references/power-of-ten.md` — the full NASA/JPL ten rules, verbatim intent and rationale.
- `references/tiger-style-guide.md` — condensed TigerStyle: safety, performance, developer-experience,
  and naming sections, with the reasoning behind each.
- `references/negative-space-programming.md` — where the term came from, what it actually means
  (Hoare logic / design-by-contract), the popular but weaker "code you don't write" sense some
  blogs use instead, and how the two relate to typed "parse, don't validate" designs.
