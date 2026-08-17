# Negative-space programming: where it comes from, what it means, what it doesn't

The term borrows from visual art, where "negative space" is the empty area _around_ a subject —
sometimes what defines the subject's shape more than the subject itself does. Applied to code, the
idea is that a program is defined not only by what it does, but by what it explicitly refuses to
do or allow.

## Two different lineages, both called "negative space"

**1. The architectural sense (older, broader).** The earliest widely-cited coding use of the term
argues that a good design states its _limitations_ as deliberately as its capabilities — deciding
what a service will _not_ do (and pushing that responsibility elsewhere, e.g. into a separate
service) is itself a design decision, not just a gap. This is a system-design-level idea: negative
space as scope discipline.

**2. The assertion sense (the one this skill is mostly about).** More recently popularized in talks
by TigerBeetle's Joran Dirk Greef and picked up by other developers, this usage is concrete and
code-level: put runtime assertions in your code for everything that must _never_ happen, not only
comments/docs for what should happen. "Now you're showing the reader the positive space — your
logic — and the negative space — what shouldn't happen." NASA's Power of Ten rule 5 (minimum two
assertions per function) is treated as the canonical instance of this practice.

Concretely, this looks like asserting function arguments, invariants, and the boundaries where
valid data could become invalid — and crucially, _keeping those assertions live in production_,
not stripping them in release builds, because production is exactly where the unexpected states you
didn't think to write a test for will actually occur.

## This is not a new idea — it's Hoare logic with a new name

Tony Hoare formalized exactly this practice in 1969, decades before the term "negative-space
programming" existed, in what's now called Hoare logic. The core object is a triple `{P} C {Q}`:
given precondition `P` holds, and command `C` runs, then postcondition `Q` is guaranteed to hold
afterward. Chain enough of these triples together and you can reason about a whole function: if the
caller guarantees the precondition before calling, the function guarantees the postcondition after
it returns. That combination of "what I require of you" and "what I guarantee to you" is a
_contract_ — the same concept underlying design-by-contract languages and libraries (Eiffel being
the canonical example).

Reasoning this way only works cleanly if control flow is simple and predictable enough that "the
state at this point in the program" has one well-defined answer — which is also, not coincidentally,
exactly what Power of Ten's ban on `goto`/recursion/unbounded loops is protecting. Assertions,
simple control flow, and provable bounds aren't three separate rules that happen to appear
together; they're the same underlying discipline (be able to state and verify what's true at each
point in the program) approached from different angles.

So: "negative-space programming" is a good, memorable name for an old and well-founded practice.
Treat it as a friendlier on-ramp to precondition/postcondition thinking, not as a genuinely new
technique — and feel free to use whichever framing (Hoare triples, design-by-contract, or "assert
the negative space") lands best for the person you're talking to.

## A third, weaker sense you'll also see online

Some articles use "negative space programming" to mean something much more general and much less
specific: "the code you _don't_ write matters" — deleting a redundant `else` branch, avoiding
boilerplate, preferring less code over more. That's a reasonable minimalism principle, but it isn't
about assertions, contracts, or safety at all, and conflating it with the assertion-based sense
above muddies both ideas. If a user's question is really about "should I write less code here,"
that's a simplicity/YAGNI conversation, not this skill's territory. If in doubt, ask which sense
they mean, or address both briefly and let context disambiguate.

## Relationship to types: "parse, don't validate"

Runtime assertions aren't the only way to carve out negative space — a static type system can do
the same job at compile time, for free, on every call site, instead of at runtime, on every
execution. If a function takes a `Width` type that can only be constructed by validating a raw
number once, every other function that takes a `Width` gets that validation for free without
re-asserting it. This is the "parse, don't validate" pattern: convert untrusted data into a
narrower, validated type at the boundary, once, rather than re-checking the same invariant with
scattered assertions every time the value is used ("shotgun parsing" is the pejorative term for the
latter, scattered version).

In practice these two techniques — types and runtime assertions — are complementary rather than
competing:

- Push what the type system can express cheaply into types (this value is never negative, this
  reference is never null, this enum has no invalid variant).
- Use runtime assertions for what the type system in your language can't express, for internal
  invariants that span multiple values or that only make sense mid-computation, and as a second,
  independent check even where a type _should_ already guarantee something (pairing assertions
  across a trust boundary — e.g. checking data both before writing to disk and after reading it
  back — catches bugs that a type alone wouldn't, because it also protects against bugs in your own
  reasoning about the type, storage corruption, or a change made elsewhere in the code that a
  type-checker didn't catch).

Neither replaces the other. A language with a weak type system (or untyped) leans harder on runtime
assertions; a language with a strong type system can push more of the negative space into types and
reserve assertions for what's left over.

## Sources consulted for this skill

- TigerBeetle, _TigerStyle_: https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md
- Wikipedia, _The Power of 10: Rules for Developing Safety-Critical Code_
- Gerard Holzmann's original Power of Ten paper (IEEE Computer, 2006)
- TigerBeetle blog, _Asserting Implications_ (matklad, 2025) — the `if (a) assert(b);` pattern
- Joran Dirk Greef, _TigerStyle! (Or How To Design Safer Systems in Less Time)_ (talk), and
  ThePrimeagen's reaction video, which popularized "negative-space programming" as a term
- Dave Gauer (ratfactor.com), notes on Greef's talk
- Graham Lee (sicpers.info), _Tony Hoare and negative space_ — the Hoare-logic framing
- Igor Loskutoff, _Negative Space Programming: it's not bad, it's just misunderstood_ — the
  types/"parse, don't validate" critique and complement
- Alex Alfasin, _Negative Space, and How Does it Apply to Coding_ — the original architectural framing
- Double Trouble blog, _Exploring the Power of Negative Space Programming_
- Prabhat Kashyap (prabhat.dev), _Negative Space Programming_ — an example of the weaker
  "code you don't write" sense of the term
