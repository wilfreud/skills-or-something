# NASA/JPL's Power of Ten

Written by Gerard J. Holzmann of NASA's Jet Propulsion Laboratory in 2006, originally for C code
in spacecraft flight software. The rules exist to make code that a human reviewer _and_ a static
analysis tool can both fully verify — nothing in the code should require "trust me, it's fine" to
reason about. A NASA review of Toyota's electronic throttle-control firmware later found hundreds
of violations of these rules in code implicated in unintended-acceleration incidents, which is
often cited as the real-world case for taking them seriously.

Source: Gerard J. Holzmann, "The Power of 10: Rules for Developing Safety-Critical Code," IEEE
Computer 39(6), 2006. See also the Wikipedia summary:
https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code

## The ten rules

1. **Simple control flow only.** No `goto`, no `setjmp`/`longjmp`, no direct or indirect
   recursion. The reason: control flow that a tool can't statically trace is control flow a human
   can't fully verify either.

2. **Every loop has a fixed upper bound.** It must be possible for a checking tool to prove,
   statically, that the loop cannot exceed a preset number of iterations. If a tool can't prove the
   bound, the rule is considered violated — "I'm pretty sure it terminates" doesn't count.

3. **No dynamic memory allocation after initialization.** Allocate everything up front. This
   removes an entire class of bugs (leaks, fragmentation, use-after-free, allocation failure at the
   worst possible moment) from the parts of the program that run continuously.

4. **No function longer than what fits on one printed page** — roughly 60 lines, one statement or
   declaration per line. The point isn't the number; it's that a function you can hold in your head
   (or on one physical page) is one you can actually verify.

5. **Assertion density averages at least two per function.** Assertions check for conditions that
   should never occur in real executions; they must be side-effect-free boolean tests. When one
   fails, the code must take an explicit recovery action (e.g., return an error to the caller) —
   not just note the failure and continue. If a static tool can prove an assertion can never fail
   (or never hold), that assertion is pointless and violates the spirit of the rule.

6. **Declare data objects at the smallest possible scope.** Minimizes the surface area over which a
   variable could be misused or read in an inconsistent state.

7. **Check every return value, and check every argument.** Every caller checks what a non-void
   function returns; every function checks the validity of the parameters it's given. No silent
   assumption that a caller "surely" passed something sane, and no silent assumption that a call
   "surely" succeeded.

8. **Restrict preprocessor use to header inclusion and simple macros.** No token pasting, no
   variadic macros, minimal conditional compilation. The preprocessor operates before the compiler
   can help you, so anything complex done there is invisible to static analysis.

9. **Restrict pointer use.** At most one level of dereference; no hiding a dereference inside a
   macro or typedef; no function pointers. Each of these makes it harder for a human or tool to
   trace what a piece of code actually touches.

10. **Compile with every warning enabled, at the strictest setting, from day one — and keep it
    clean.** Run at least one (preferably more) static analyzers daily and keep those clean too.
    Warnings caught on day one are cheap; warnings that accumulate for a year are a wall no one
    wants to climb.

## How TigerStyle generalizes these

TigerStyle (see `tiger-style-guide.md`) applies the same underlying goals — safety, provable
bounds, reviewability — to a broader class of software than embedded C, and adds performance and
developer-experience concerns that Power of Ten doesn't cover (Power of Ten is deliberately silent
on things like naming or algorithmic performance; it's about eliminating specific classes of
unreviewable code). Where the two diverge (e.g. Power of Ten's ban on function pointers, which
TigerStyle doesn't carry over wholesale into Zig), prefer whichever rule serves the _reason_ behind
it in the language you're actually using, rather than applying the letter of a C-specific rule to a
language where the underlying risk doesn't apply the same way.
