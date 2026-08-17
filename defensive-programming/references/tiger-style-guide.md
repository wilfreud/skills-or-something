# TigerStyle, condensed

TigerStyle is the coding style used on [TigerBeetle](https://github.com/tigerbeetle/tigerbeetle),
a financial-transactions database, documented in full at
https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md. It orders its design
goals explicitly: **safety, then performance, then developer experience** — in that order, because
style choices are judged by whether they advance those three, not by readability alone.

TigerStyle treats simplicity as the _hardest_ revision of a design, not the first attempt — the
elegant version of a solution is usually found after several passes, not before. It also runs a
strict "zero technical debt" policy: known showstoppers get fixed before they ship, not tracked as
future work, on the theory that a problem caught in design or implementation is far cheaper than
the same problem caught in production.

## Safety

This section is TigerStyle's expansion of NASA's Power of Ten (see `power-of-ten.md`) beyond C.
Highlights not already covered in SKILL.md's checklist:

- **Explicitly sized types.** Use fixed-width integer types (`u32`, `u64`, ...) rather than
  platform-dependent ones (`usize`) so behavior doesn't shift across architectures.
- **The golden rule of assertions:** assert the positive space you _do_ expect, and the negative
  space you _do not_ expect. Bugs cluster at the boundary where data crosses from valid to invalid,
  so tests must exercise that boundary too — not just valid inputs, but invalid ones, and the
  moment valid data becomes invalid.
- **Assertions are a safety net for understanding, not a replacement for it.** A fuzzer can prove
  bugs exist; it can't prove they don't. The intended order is: build a precise mental model of
  what the code should do → encode that model as assertions → write the code and comments that
  explain the model to a reviewer → use fuzzing/simulation as a last line of defense against gaps
  in that shared understanding.
- **Reacting to external events:** don't let external input directly drive your program's control
  flow tick-by-tick. Run at your own pace and process input in batches. This keeps control flow
  under the program's own control (safer) and enables batching (faster) at the same time — one of
  TigerStyle's recurring moves, finding a design that satisfies more than one goal simultaneously.
- **All errors handled, always.** A widely cited study of real production failures in distributed
  data-intensive systems found that the overwhelming majority of catastrophic failures traced back
  to _incorrectly handled_ non-fatal errors that were already being signaled by the software — not
  to exotic, undetectable failure modes. The fix was usually available; it just wasn't wired up.
- **Explicitly pass options instead of relying on defaults** at call sites for library functions,
  so a future change to a library's default can't silently change your program's behavior.
- **Always motivate, always say why.** A rule stated with its rationale is a rule people can apply
  correctly to new situations; a rule stated as a bare imperative is not.

## Performance

- Think about performance _at design time_, not after profiling — the 1000x wins are available in
  the design phase and mostly gone by the time you're optimizing a shipped implementation.
- Do back-of-the-envelope sketches across the four resources (network, disk, memory, CPU) and their
  two characteristics (bandwidth, latency) to land within shouting distance of optimal, cheaply,
  before writing real code.
- Optimize the slowest resources first, adjusted for how often each is actually hit — a cheap
  operation performed constantly can cost more in aggregate than an expensive one performed rarely.
- Batch access to amortize fixed costs across network, disk, memory, and CPU.
- Be explicit rather than trusting the compiler to infer the fast path — e.g. pulling a hot loop
  into a standalone function with plain arguments makes it obvious to both the compiler and a human
  reader that there's no hidden state to reason about.

## Developer experience

### Naming

- Get the nouns and verbs exactly right — a name is a compressed claim about what a thing is or
  does, and a well-chosen one shows the author understood the domain.
- Put units and qualifiers at the _end_ of a name, most-significant word first
  (`latency_ms_max`, not `max_latency_ms`) so related variables sort and line up together.
- Give related variables the same length where possible (`source`/`target` rather than
  `src`/`dest`) so derived variables and calculations line up visually too.
- Don't let one name carry two different meanings depending on context — rename rather than
  overload.
- Prefer a noun over an adjective or present participle where the name might get used outside the
  code (in docs, in conversation) — nouns compose more naturally.

### Reducing the chance of state bugs

- Shrink variable scope and lifetime; don't introduce a variable before it's needed or leave it
  around after it stops being needed. This shrinks the "place-of-check to place-of-use" gap, a
  cousin of the classic time-of-check-to-time-of-use bug class.
- Don't duplicate variables or keep aliases to the same value in two places — it's an easy way for
  state to silently drift out of sync.
- Prefer simpler function signatures and return types (`void` over `bool`, `bool` over an integer,
  a plain value over an optional, an optional over a value-or-error) because complexity in a return
  type propagates to every caller.

### Mechanical style

- Hard function-length limit: 70 lines. The reasoning is physical — a function you can see on one
  screen without scrolling is one you can hold in working memory while reading it.
- Line length capped (TigerBeetle uses 100 columns) so two files can sit side-by-side on a screen.
- Braces on every `if`, even single-line ones, partly as defense against the classic
  "goto fail;"-style bug where a missing brace silently changes which statement is conditional.

### Dependencies and tooling

- TigerBeetle runs a "zero dependencies" policy beyond its language toolchain, on the reasoning
  that every dependency is a supply-chain and correctness risk that compounds across a whole stack.
  This is an extreme stance suited to foundational infrastructure; apply it in proportion to how
  critical the code actually is, not as a blanket rule for all software.
- Prefer a small, standardized toolchain over a sprawl of specialized tools — each additional tool
  is something the whole team has to learn and maintain.
