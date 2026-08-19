---
name: reactflow
description: "Use when working with React Flow / @xyflow/react: building, editing, reviewing, debugging, typing, performance-tuning, testing, or designing interactive node-edge canvases, custom nodes, handles, edges, labels, layouts, graph filters, save/restore behavior, or architecture diagrams. Always use for files importing @xyflow/react, ReactFlow, Background, Controls, MiniMap, Handle, useNodesState, useEdgesState, useReactFlow, Node, Edge, NodeProps, EdgeProps, or related graph/canvas code."
---

# React Flow

## Required doc freshness workflow

Before implementing or reviewing React Flow behavior:

1. Fetch `https://reactflow.dev/llms.txt`.
2. Search that file for the task area: quick start, concepts, custom nodes, handles, edges, labels, layouting, hooks, TypeScript, performance, SSR, testing, examples, API reference, or troubleshooting.
3. Fetch the exact linked React Flow page(s) needed for the task.
4. Base API names, prop names, event signatures, and type imports on fetched pages, not memory.
5. Mention which docs were fetched when handing off non-trivial React Flow work.

Use bundled references only as a routing map. They are not a substitute for fresh docs.

## Reference routing

- Read `references/doc-map.md` to pick the right official React Flow links quickly.
- Read `references/implementation-checklist.md` before editing substantial React Flow code or reviewing graph behavior.

## Implementation stance

- Treat React Flow canvas state as UI state unless product requirements say otherwise.
- Keep business/domain relationships outside React Flow node positions. Persist domain graph facts in the application data model, then derive `nodes[]` and `edges[]` for rendering.
- Store node positions, viewport, collapsed groups, and visual preferences separately from business relationships.
- Use TypeScript generics for `Node<Data>` and `Edge<Data>` instead of `any`.
- Use stable `nodeTypes` and `edgeTypes` objects, typically memoized or module-scoped, to avoid React Flow remounts.
- Validate every connection before adding an edge when the domain has constraints.
- Keep custom node and edge components small. Put domain editing forms/panels outside custom node renderers when possible.
- Avoid mutating `node` or `edge` objects in event handlers. Return new arrays/objects through state setters.
- For large graphs, minimize subscriptions to full node/edge arrays and avoid expensive work inside node renderers.

## Common task workflow

1. Identify current React Flow version from `package.json` and imports. In this repo expect `@xyflow/react`.
2. Fetch fresh docs through the required workflow.
3. Inspect current controlled/uncontrolled setup: `nodes`, `edges`, `onNodesChange`, `onEdgesChange`, `onConnect`, provider usage.
4. Define typed data shapes for node and edge `data`.
5. Encode graph invariants near the mutation boundary:
   - connection endpoints exist;
   - no forbidden self-edge;
   - no invalid cross-type relationship;
   - no duplicate edge if domain forbids it;
   - no cycle if the graph must be acyclic.
6. Persist domain mutations first when data is business-relevant; re-render from returned server data.
7. Verify with TypeScript and the app's relevant test/build command.

## Project-specific notes for this repository

- Existing app uses React Flow for an architecture cartography canvas.
- Domain source of truth must be SQLite/relational data, not `localStorage` or React Flow objects.
- `localStorage` may keep layout and appearance preferences only.
- Graph filters should derive from typed persisted relationships: project membership, application dependency, deployment, datastore access, system-user hosting, database-instance containment, party association.

