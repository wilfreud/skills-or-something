---
name: animejs
description: "Use when working with Anime.js / animejs: building, editing, reviewing, debugging, optimizing, or designing JavaScript/TypeScript animations, timelines, timers, stagger effects, easings, WAAPI animations, SVG motion, text splitting, draggable interactions, layout transitions, React/Next.js animation integration, or performance-sensitive UI motion. Always use for files importing animejs, animejs/animation, animejs/timeline, animejs/utils, animejs/svg, animejs/text, animejs/waapi, animejs/scope, animate, createTimeline, createTimer, createScope, createDraggable, createLayout, stagger, spring, splitText, svg, waapi, or engine."
---

# Anime.js

## Required doc freshness workflow

Before implementing or reviewing Anime.js behavior:

1. Fetch `https://animejs.com/documentation/`.
2. Search documentation sections for task area: installation, module imports, React, animation, timeline, timer, animatable, draggable, layout, scope, events, SVG, text, utilities, easings, WAAPI, engine, or adapters.
3. Fetch exact linked Anime.js page(s) needed for task.
4. Base imports, method names, parameter names, callbacks, return types, cleanup methods, and module subpaths on fetched pages, not memory.
5. Mention fetched docs when handing off non-trivial animation work.

Use bundled references as routing map only. Do not treat them as substitute for fresh docs.

## Reference routing

- Read `references/doc-map.md` to pick official links quickly.
- Read `references/api-patterns.md` before implementing timelines, staggered sequences, SVG/text effects, draggable/layout interactions, WAAPI, or engine-level behavior.
- Read `references/react-nextjs.md` before using Anime.js in React or Next.js.
- Read `references/optimization.md` before performance-sensitive animation, large lists, frequent events, React Flow/canvas overlays, or reduced-motion work.

## Implementation stance

- Prefer module/subpath imports when bundle size matters.
- In React/Next.js, use `createScope()` inside effects and `scope.revert()` cleanup.
- Keep animations scoped to owned DOM roots. Avoid global selectors unless deliberate.
- Animate compositor-friendly properties first: `transform`, `opacity`, filter sparingly.
- Avoid animating layout-heavy properties unless using Anime.js layout APIs deliberately.
- Respect `prefers-reduced-motion`; provide reduced or disabled motion path.
- Do not leave infinite loops, timers, draggables, or event callbacks alive after component unmount.
- Do not hide business state in animation instances. UI motion follows state, not inverse.

## Common task workflow

1. Identify environment: vanilla JS, React, Next.js Client Component, SVG, text, WAAPI, or layout transition.
2. Fetch fresh docs through required workflow.
3. Choose primitive:
   - `animate()` for direct property animation.
   - `createTimeline()` for coordinated sequence.
   - `createTimer()` for timer/callback timing.
   - `createScope()` for React/component scoping and cleanup.
   - `createDraggable()` for pointer drag interactions.
   - `createLayout()` for animating layout state changes.
   - `waapi.animate()` for lightweight WAAPI-backed animations when feature set fits.
4. Define lifecycle and cleanup before coding.
5. Keep target selection deterministic and scoped.
6. Tune duration/easing/stagger with intent, not decoration.
7. Verify TypeScript/build and manually inspect motion behavior when UI changes.

## Project-specific notes

- This repo is Next.js App Router. Anime.js UI components must be Client Components.
- Use Anime.js for interface polish only. Domain source of truth remains SQLite/relational data.
- If animating React Flow nodes or panels, do not mutate React Flow node objects for animation state. Animate DOM presentation or store UI preference separately.
- Do not add `animejs` dependency without user approval if not already present.
