---
name: whatsapp-flows-json
description: >
  Use this skill when designing, reviewing, validating, or integrating Meta
  WhatsApp Flows and Flow JSON. Covers Flow JSON structure, components,
  sending Flow messages, Flows API operations, endpoint encryption, and
  production readiness against official Meta documentation.
---

# WhatsApp Flows JSON

Use this skill for WhatsApp Flows work: writing Flow JSON, reviewing Flow JSON,
building dynamic endpoint contracts, sending a Flow through Cloud API, managing
Flows through Graph API, or debugging validation/runtime issues.

This skill is provider-specific and product-agnostic. Do not assume any local
business domain, subscription model, brand, or repository convention unless the
current task explicitly provides it.

## Mandatory Source Policy

Before production-affecting advice or code:

1. Fetch or inspect the official Meta pages listed in
   `references/doc-map.md`.
2. Confirm current supported Flow JSON versions from Meta changelog/versioning.
3. Do not invent a latest version. If the changelog cannot be reached, say so
   and keep version claims limited to what the fetched docs prove.
4. Prefer the `documentation/business-messaging/whatsapp/flows/...` pages when
   both `docs/whatsapp/...` and `documentation/...` routes exist.
5. Keep links to the exact Meta pages used in the final answer or generated doc.

Known fetched-doc facts from 2026-08-19:

- Flow endpoint Data API current value in the Flow JSON guide: `3.0`.
- Cloud API Flow interactive message parameter `flow_message_version`: `3`.
- Flow JSON `data_channel_uri` is not supported as of Flow JSON `3.0`; endpoint
  URL belongs in Flows API `endpoint_uri`.
- The Meta changelog endpoint was unavailable during skill creation. Recheck it
  before claiming the latest supported Flow JSON version.

## Workflow

1. Determine the task shape:
   - Flow JSON design/review -> load `references/flow-json-structure.md`.
   - Component choice or validation -> load `references/components.md`.
   - Sending or managing Flows -> load `references/sending-and-api.md`.
   - Endpoint/data exchange/security -> load `references/endpoint-security.md`.
2. Decide whether the Flow is static or endpoint-powered.
3. For static Flows, prefer `navigate` and `complete`; do not add an endpoint
   only to move known data.
4. For endpoint-powered Flows, require `data_api_version`, `routing_model`, and
   API-level `endpoint_uri`.
5. Validate screen IDs, routing, terminal screens, Footer actions, dynamic data
   schemas, and component limits before discussing API calls.
6. For media uploads, load the media section in `references/components.md` and
   check payload placement rules.

## Hard Rules

- Do not put endpoint URL in `data_channel_uri` for Flow JSON `3.0+`.
- Do not use `navigate` on a terminal screen Footer; terminal screen must finish
  with `complete` or endpoint-driven `SUCCESS`.
- Do not call a Data Endpoint when `navigate` and static/dynamic message payload
  data are enough.
- Do not place `PhotoPicker` or `DocumentPicker` values inside nested payloads
  or `navigate` payloads.
- Do not place both `PhotoPicker` and `DocumentPicker` on one screen.
- Do not claim a published Flow can be edited or deleted; publish is a lifecycle
  boundary. Use new draft/clone/deprecate flow as appropriate.
- Do not log decrypted PII, media IDs, Flow tokens, encrypted AES keys, private
  keys, or raw endpoint payloads in production.

## Review Checklist

- Source links official and current enough for the decision.
- Flow JSON root fields match task: `version`, `screens`, optional
  `routing_model`, optional `data_api_version`.
- Every screen has stable `id`, useful `title`, and valid `layout`.
- Endpoint Flows have routing that matches every server-returned screen.
- At least one terminal screen exists; terminal screens include Footer.
- `data` schemas include `__example__` values for preview where dynamic data is
  used.
- Component limits and version gates are checked.
- Cloud API message uses exactly one of `flow_id` or `flow_name`.
- Endpoint validates Meta signature, decrypts request, returns encrypted plain
  text response, and handles health/error/data exchange actions.

## References

- `references/doc-map.md`
- `references/flow-json-structure.md`
- `references/components.md`
- `references/sending-and-api.md`
- `references/endpoint-security.md`
