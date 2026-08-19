# Anime.js with React and Next.js

Fetch official docs before using exact APIs:

- React guide: https://animejs.com/documentation/getting-started/using-with-react/
- Scope: https://animejs.com/documentation/scope/
- Module imports: https://animejs.com/documentation/getting-started/module-imports/

## Next.js App Router rules

- Components touching Anime.js must be Client Components: add `"use client"` at file top.
- Do not call Anime.js during Server Component render.
- Do not read `window`, `document`, DOM refs, or layout measurements outside client lifecycle.
- Import Anime.js only in client-only modules unless using pure utilities that are safe server-side.
- Avoid hydration mismatch: initial HTML/CSS must be valid before animation starts.

## React lifecycle pattern

Preferred shape:

```tsx
"use client";

import { createScope, animate } from "animejs";
import { useEffect, useRef } from "react";

export function MotionPanel() {
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!rootRef.current) return;

    const scope = createScope({ root: rootRef }).add(() => {
      animate(".panel", {
        opacity: [0, 1],
        y: [12, 0],
        duration: 240,
        ease: "out(3)",
      });
    });

    return () => scope.revert();
  }, []);

  return <div ref={rootRef}><div className="panel" /></div>;
}
```

Before copying this pattern, fetch current React guide and Scope docs. Adjust types/signatures to docs.

## State-driven animation

- React state owns semantic state.
- Anime.js owns transition between visual states.
- Do not store domain state inside animation instance.
- Use refs for animation handles, not state, unless UI must re-render.
- For event-triggered scoped methods, register methods inside scope and call through scope ref only after initialization.

## Cleanup checklist

On unmount or dependency change:

- Revert scope.
- Pause/cancel/remove standalone animations if not scoped.
- Remove event listeners if manually added.
- Revert DOM splitting or inline styles when needed.
- Avoid stale closures by passing current values deliberately.

## React Flow integration

If using Anime.js around React Flow:

- Do not mutate React Flow `nodes`/`edges` for visual-only animation.
- Animate DOM presentation only after React Flow rendered node elements.
- Be careful with pointer events: draggable interactions can conflict with React Flow pan/drag/connect.
- Prefer CSS transitions for simple hover/focus states; reserve Anime.js for sequenced or physics-like motion.
- Keep graph data source relational; animation state is visual only.

## Accessibility

- Honor `prefers-reduced-motion`.
- Never depend on motion alone to communicate state.
- Keep focus order stable during layout/text animations.
- Avoid long entrance animations that delay user interaction.
