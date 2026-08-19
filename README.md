# Skills Collection

A personal collection of agent skills I needed and formalized the way I wanted.

> **Token Optimization**: I always use [caveman](https://github.com/JuliusBrussee/caveman) to cut token consumption.

Free to use, free to contribute.

---

## Skills Overview

| Skill | Technical Name | Domain | Description |
|---|---|---|---|
| [Anime.js](./animejs/) | `animejs` | UI Animation & Frontend | Building, optimizing, and debugging animations, timelines, timers, layout transitions, and WAAPI with Anime.js in React/Next.js. |
| [Defensive Programming](./defensive-programming/) | `tiger-style` | Reliability & Systems | Assertion-heavy defensive coding style based on TigerBeetle's TigerStyle, NASA/JPL Power of Ten, and negative-space programming. |
| [Next.js Security Review](./nextjs-security-review/) | `nextjs-security-review` | Web Security | Auditing Next.js (App & Pages Router) for RSC data exposure, Server Actions authorization/IDOR, proxy/middleware bypasses, SSRF, and CVE tracking. |
| [React Security Review](./react-security-review/) | `react-security-review` | Frontend Security | Auditing React code against OWASP Top 10:2025: XSS prevention (HTML, attributes, URLs), dangerous sinks, SSR/hydration, and CSP. |
| [React Flow](./reactflow/) | `reactflow` | Graph & Canvas Visualization | Architecture, typing, and manipulation of interactive node-edge diagrams with `@xyflow/react`. |

---

## Structure

Each skill directory follows a consistent layout:

```text
<skill-name>/
├── SKILL.md                 # Main instructions, operational workflows, and YAML metadata
├── references/              # In-depth technical guides, cheat sheets, and documentation maps
└── agents/                  # (Optional) Agent interface and prompt configurations
```

- **`SKILL.md`**: Defines activation triggers, implementation guidelines, step-by-step workflows, and operational constraints.
- **`references/`**: Topic-specific reference documents loaded on demand to prevent context bloat.
- **`agents/`**: Optional UI/agent metadata and default prompts.

---

## Skills Summary

### 1. [Anime.js](./animejs/)
- **Focus**: Performant and accessible UI animations for modern web stacks (React, Next.js Client Components).
- **Key points**:
  - `prefers-reduced-motion` compliance and compositor-first properties (`transform`, `opacity`).
  - Strict lifecycle cleanup with `createScope()` and `scope.revert()`.
  - Fresh documentation verification workflow against official Anime.js docs.
- **References**: `doc-map.md`, `api-patterns.md`, `react-nextjs.md`, `optimization.md`.

### 2. [Defensive Programming (TigerStyle)](./defensive-programming/)
- **Focus**: Safety-critical, assertion-dense code that fails loudly at the first sign of corruption rather than continuing silently.
- **Key points**:
  - **Negative-space programming**: Explicitly assert conditions that must *never* happen.
  - **Bounded execution**: Fixed bounds on loops, no unbounded recursion.
  - **Assertion density**: Minimum of 2 assertions per function (preconditions, postconditions, invariants).
  - Short functions (< 70 lines) and explicit error handling on all return values.
- **References**: `power-of-ten.md` (NASA/JPL), `tiger-style-guide.md` (TigerBeetle), `negative-space-programming.md`.

### 3. [Next.js Security Review](./nextjs-security-review/)
- **Focus**: Security review and auditing for Next.js App Router and Pages Router.
- **Key points**:
  - Prevent accidental data leaks across RSC / `"use client"` prop boundaries.
  - Mandatory authentication and authorization (IDOR) checks inside every Server Action.
  - Hardening `proxy.ts` / `middleware.ts` matchers and preventing SSRF in `rewrites()`/`redirects()`.
  - Tracking known CVEs (RCE, RSC DoS, middleware bypasses).
- **References**: `data-exposure-rsc.md`, `server-actions-security.md`, `known-cves-and-middleware.md`, `nodejs-hardening.md`, `sources.md`.

### 4. [React Security Review](./react-security-review/)
- **Focus**: Frontend security auditing aligned with OWASP Top 10:2025.
- **Key points**:
  - Detection of dangerous sinks: `dangerouslySetInnerHTML`, `innerHTML`, `javascript:` URLs, `eval`.
  - Client-side access control issues, exposed secrets, and third-party script integrity.
  - Sanitization practices (DOMPurify), SSR/hydration safety, and Content Security Policy (CSP).
- **References**: `xss-prevention.md`, `owasp-top10-2025-react.md`, `sources.md`.

### 5. [React Flow](./reactflow/)
- **Focus**: Building and maintaining node-edge canvases using `@xyflow/react`.
- **Key points**:
  - Separation of business domain truth from canvas visual state.
  - Strict generic typing (`Node<Data>`, `Edge<Data>`).
  - Graph invariant validation (preventing cycles, invalid connections, self-edges).
  - Performance optimization for large-scale graphs.
- **References**: `doc-map.md`, `implementation-checklist.md`.

---

## Usage

### Antigravity
- **Project-level**: Place the skill directory in `.agents/skills/<skill-name>/` in your repository root.
- **Global-level**: Place the skill directory in `~/.gemini/config/skills/<skill-name>/`.

### Other AI Assistants (Claude Code, Cursor, Copilot, etc.)
- Reference the relevant `SKILL.md` directly or include the skill folder in your project's custom rules (`.cursorrules`, `CLAUDE.md`, system prompts).

---

## Contributing & License

Free to use, free to contribute. Feel free to open issues, submit pull requests, or adapt these skills to your own workflow.
