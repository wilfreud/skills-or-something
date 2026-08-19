# Anime.js optimization reference

Read before performance-sensitive motion. Fetch official docs for exact APIs.

## First principles

- Prefer CSS transforms and opacity. They usually avoid layout and paint-heavy work.
- Avoid animating width, height, top, left, margin, padding, grid, and DOM order unless using `createLayout()` intentionally.
- Keep animation target counts bounded. Large target arrays multiply style writes and callbacks.
- Scope selectors to a root. Global selectors are slower and fragile.
- Avoid layout reads during animation callbacks. Reads such as `getBoundingClientRect()` can force sync layout.
- Batch setup. Query targets once; do not query repeatedly inside update callbacks.
- Reuse timelines/scopes when lifecycle allows; clean them when component unmounts.
- Prefer `waapi.animate()` for simple, browser-native, lightweight animation if required features fit.

## Import and bundle size

Fetch module imports first:

- https://animejs.com/documentation/getting-started/module-imports/

Guidelines:

- Main import is ergonomic and tree-shaking friendly in modern bundlers.
- Subpath imports reduce risk when tree-shaking is unavailable or uncertain.
- Do not import `* as anime` in app code unless needed; it hides bundle impact.
- Avoid adding Anime.js to server bundles in Next.js. Keep animation code in client modules.

## React/Next.js performance

- Use `createScope()` with a root ref and `scope.revert()` cleanup.
- Do not re-create animations on every render. Use effects with deliberate dependencies.
- Use refs for animation instances. Avoid state updates on every animation tick.
- If responding to rapidly changing values, throttle/debounce or use Anime.js utilities deliberately.
- Use stable class names/data attributes for targets.
- Do not animate hidden/unmounted content.

## Reduced motion

Implement a reduced path:

```ts
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (reduceMotion) {
  // Set final state, skip or shorten motion.
} else {
  // Run Anime.js animation.
}
```

In React, evaluate this on client only. Consider a small hook if used repeatedly.

## Timeline optimization

- Use timelines to coordinate many animations instead of many unrelated animation instances.
- Keep callbacks cheap.
- Prefer labels and relative positions for readability.
- Avoid infinite loops unless required; expose pause/cleanup.
- For repeating decorative loops, pause when component not visible if practical.

## Stagger optimization

- Use `stagger()` for setup-time distribution, not per-frame custom callbacks.
- Bound item count for list animations.
- For huge lists, animate container or visible subset, not every item.
- Prefer deterministic stagger values for SSR/client consistency.

## Layout animation optimization

Fetch layout docs:

- https://animejs.com/documentation/layout/

Guidelines:

- Use `createLayout()` only for meaningful layout transitions.
- Batch DOM/class changes inside `layout.update()` callback.
- Do not run layout animations on every minor state change.
- Avoid nested layout animations unless measured and necessary.
- Keep layout roots small; do not create root at whole app if panel-level root works.

## SVG and text optimization

- SVG path animation can be expensive with complex paths. Simplify SVGs when possible.
- Text splitting increases DOM nodes. Use only for headings/short text, not long documents.
- Revert text splitting when component unmounts or content changes.
- Avoid animating thousands of characters; animate words/lines/container instead.

## Engine-level tuning

Fetch engine docs before touching:

- https://animejs.com/documentation/engine/

Treat engine settings as global risk. Document why changed. Avoid global tuning for one component; prefer local animation parameters.

## Debug checklist

When animation janks:

1. Check target count.
2. Check animated properties for layout/paint triggers.
3. Check callbacks for layout reads or React state writes.
4. Check repeated effect re-runs.
5. Check uncleaned loops/timers after unmount.
6. Check bundle import path.
7. Check reduced-motion branch.
8. Compare JS `animate()` vs WAAPI for simple cases.

## Project-specific optimization

For this repository:

- Use Anime.js for panels, onboarding, subtle graph affordances, and transitions.
- Do not animate persisted React Flow graph state directly.
- Keep animations optional and non-blocking. Architecture cartography usability matters more than decoration.
- If adding Anime.js dependency, ask user first unless task explicitly authorizes dependency changes.
