# React Flow implementation checklist

Read this before substantial React Flow edits or reviews. Then fetch fresh official docs for exact APIs.

## State model

- Decide controlled vs uncontrolled flow explicitly.
- For controlled flows, keep `nodes`, `edges`, `onNodesChange`, `onEdgesChange`, and `onConnect` together.
- Do not mutate node or edge objects in place.
- Keep React Flow rendering state separate from domain source-of-truth state.
- Persist viewport/layout only as UI preferences.

## TypeScript

- Define node data and edge data types first.
- Use `Node<YourNodeData>` and `Edge<YourEdgeData>`.
- Type custom node components with `NodeProps<Node<YourNodeData>>` or the currently documented equivalent from fetched docs.
- Type custom edge components with `EdgeProps<Edge<YourEdgeData>>` or the currently documented equivalent from fetched docs.
- Avoid index signatures unless the node truly accepts arbitrary fields.

## Custom nodes

- Keep custom nodes presentational when possible.
- Put heavy panels, modals, and forms outside the node renderer.
- Render `<Handle />` only where connections are valid.
- If handles change dynamically, fetch and use the current `useUpdateNodeInternals()` guidance.
- Use utility classes or event handling to prevent drag/pan conflicts inside interactive node controls.

## Edges and connections

- Validate connection endpoints and domain rules before `addEdge`.
- Use stable edge IDs derived from domain relationship IDs when persisted.
- Avoid duplicate edges unless multiedges are a deliberate feature.
- For edge labels with HTML controls, fetch `EdgeLabelRenderer` docs and matching example.
- For custom edge paths, fetch custom edge and `BaseEdge` docs.

## Layout

- React Flow does not provide layout algorithms by default. Fetch layouting docs before adding Dagre, Elkjs, d3-force, or custom layout.
- Treat auto-layout output as visual coordinates, not domain facts.
- Re-run layout only when graph topology or selected filter requires it; avoid relayouting on every drag.

## Performance

- Fetch performance docs for large graphs.
- Memoize `nodeTypes`, `edgeTypes`, expensive derived nodes/edges, and custom node internals where appropriate.
- Avoid subscribing every node to full graph state.
- Avoid expensive filtering or graph traversal during render.
- Keep node data small and serializable.

## Accessibility and testing

- Fetch accessibility docs for keyboard/screen-reader requirements.
- Fetch testing docs before Cypress, Playwright, or Jest work.
- Test domain invariants at the mutation layer separately from canvas rendering.
- For UI tests, prefer stable selectors and deterministic graph fixture data.

## Next.js constraints

- React Flow canvases are client-side React UI. Components using React Flow usually need `"use client"` in Next.js App Router.
- Do not expose server-only data through node data objects sent to Client Components.
- Persist graph mutations through route handlers or Server Actions with server-side validation.
