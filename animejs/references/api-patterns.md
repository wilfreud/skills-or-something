# Anime.js API patterns

Fetch official docs before using exact signatures. This file only routes decisions.

## Imports

Prefer one of two import styles:

```ts
import { animate, createTimeline, stagger } from "animejs";
```

or subpaths when tree-shaking is uncertain:

```ts
import { animate } from "animejs/animation";
import { createTimeline } from "animejs/timeline";
import { stagger } from "animejs/utils";
```

Fetch module-import docs before changing import strategy.

## `animate()`

Use for direct target animation:

- CSS selectors or DOM elements as targets.
- object parameters containing animatable properties, tween parameters, playback settings, callbacks.
- property keyframes for per-property sequencing.
- `stagger()` for distributed delays/values.

Fetch:

- https://animejs.com/documentation/animation/
- https://animejs.com/documentation/animation/targets/
- https://animejs.com/documentation/animation/animatable-properties/
- https://animejs.com/documentation/animation/tween-parameters/
- https://animejs.com/documentation/animation/keyframes/

## Timelines

Use `createTimeline()` when animation order matters or multiple targets must coordinate.

Common operations to verify in docs:

- `timeline.add(target, animationParameters, position)`
- `timeline.add(timerParameters, position)`
- `timeline.sync(...)`
- `timeline.call(...)`
- `timeline.label(...)`
- relative positions such as labels and offsets

Fetch:

- https://animejs.com/documentation/timeline/
- https://animejs.com/documentation/timeline/time-position/
- https://animejs.com/documentation/timeline/methods/

## Scope

Use `createScope()` for component-scoped selectors, lifecycle cleanup, and externally callable methods registered from inside the scope.

Use scope when:

- React component owns DOM subtree.
- Same CSS selectors appear multiple times on page.
- Need cleanup of animations/draggables/timers on unmount.
- Need methods callable from event handlers after setup.

Fetch:

- https://animejs.com/documentation/scope/
- https://animejs.com/documentation/getting-started/using-with-react/

## Draggable

Use `createDraggable()` for pointer interactions. Validate if interaction conflicts with native drag, scroll, React Flow pan/drag, or form controls.

Fetch:

- https://animejs.com/documentation/draggable/
- axes/settings/callbacks/methods/properties pages under draggable.

## Layout

Use `createLayout()` for animating between layout states. It is specifically for state changes normally hard to animate, such as display, flex/grid, and DOM order.

Prefer `layout.update(cb, params)` when state mutation and animation should be coupled. Avoid using layout animations as data source.

Fetch:

- https://animejs.com/documentation/layout/

## SVG

Use SVG helpers for path drawing, motion paths, morphing, or geometry-driven effects. Fetch exact SVG helper page before use.

Fetch:

- https://animejs.com/documentation/svg/

## Text

Use `splitText()` for character/word/line animation. Cleanup matters: split text changes DOM structure. Fetch docs before implementing reversible text effects.

Fetch:

- https://animejs.com/documentation/text/

## WAAPI

Use `waapi.animate()` for lightweight basic animations when supported feature set is enough. JS `animate()` is larger but has full Anime.js feature set.

Fetch:

- https://animejs.com/documentation/web-animation-api/
- https://animejs.com/documentation/animation/

## Engine

Only tune engine when needed. Fetch docs before touching global timing, FPS, precision, pause-on-document-hidden, speed, or defaults.

Fetch:

- https://animejs.com/documentation/engine/
