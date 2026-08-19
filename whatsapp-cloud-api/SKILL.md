---
name: whatsapp-cloud-api
description: "Use this skill when writing, editing, reviewing, or debugging integrations with Meta WhatsApp Cloud API or WhatsApp Business Platform: Messages API, service messages, templates, media, documents, interactive messages, reactions, locations, webhooks, delivery statuses, errors, phone number IDs, WABA IDs, access tokens, message IDs (wamid), WhatsApp Manager, calling, or Meta Business Manager. Applies to any language or framework."
---

# WhatsApp Cloud API

Framework-agnostic rules for Meta WhatsApp Cloud API integrations. Do not bind this skill to a specific app, product, or business domain. Adapt names, config, logging, and persistence to the current codebase.

## Required Doc Freshness Workflow

Fetch current Meta docs before changing WhatsApp behavior. Graph API versions, payload fields, template rules, media limits, and errors drift.

1. Read `references/doc-map.md`.
2. Fetch exact official Meta page(s) for task. Use `.md` variants when available; if a `.md` endpoint 404s, fetch HTML.
3. Treat primary send reference as canonical for outbound payloads:
   https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/message-api
4. Base endpoint, field, error, media, webhook, and calling decisions on fetched Meta docs, not memory, old snippets, or Postman alone.
5. Mention fetched docs when handing off non-trivial WhatsApp work.

Use bundled references as routing map and durable conventions only. Do not treat them as substitute for fresh docs.

## Reference Routing

- Read `references/doc-map.md` first to pick official Meta links quickly.
- Read `references/messages-api.md` before sending or reviewing outbound messages, phone formats, service windows, status interpretation, or delivery sequencing.
- Read `references/templates-media-calling.md` before implementing templates, template builders, media upload/download, document messages, or WhatsApp Calling.
- Read `references/webhooks-and-errors.md` before implementing webhook verification, signature validation, idempotency, delivery statuses, or Cloud API error handling.

## Integration Shape

Keep layers separate:

- Route/controller: public webhook verification and webhook receipt only.
- Service/client: signs/verifies, builds payloads, calls Graph API, parses responses, emits domain events/logs.
- Business layer: decides why a message/call/template should be sent.

Never scatter raw Graph API POST calls through business code. Centralize outbound requests so auth, timeouts, logging, masking, retries, and error handling stay consistent.

## Config Baseline

Common settings:

- `WHATSAPP_ACCESS_TOKEN`: bearer token. Prefer system-user or business-integration system-user token for server integrations.
- `WHATSAPP_PHONE_NUMBER_ID`: sender phone number ID used in message/media endpoints.
- `WHATSAPP_BUSINESS_ACCOUNT_ID`: WABA ID for management APIs such as templates.
- `WHATSAPP_VERIFY_TOKEN`: your webhook challenge secret.
- `WHATSAPP_APP_SECRET`: app secret for `X-Hub-Signature-256` validation.
- `WHATSAPP_API_VERSION`: Graph API version, for example `v25.0`.

Do not hardcode access tokens, phone number IDs, WABA IDs, or Graph API versions in call sites. Redact tokens and unmasked phone numbers from logs.

## Implementation Checklist

Before code:

- Fetch relevant official docs and note Graph API version.
- Identify message type and exact endpoint.
- Confirm service window vs template requirement.
- Confirm opt-in basis.
- Confirm phone number ID, WABA ID, token permissions, app secret, and webhook subscriptions.

While coding:

- Centralize Graph API request builder.
- Set explicit timeout.
- Mask phone numbers.
- Capture `wamid`, code, details, and `fbtrace_id`.
- Validate media MIME/size before send.
- Validate template name, language, component count, and param format.
- Keep webhook verification and signature validation on raw body.
- Make webhook processing idempotent.

Before saying done:

- Show exact docs fetched.
- Show target endpoint/payload shape used.
- Distinguish request accepted from delivered/read.
- State what was locally validated and what needs Meta sandbox/live validation.

## Anti-Patterns

- Treating HTTP 200 send response as delivery success.
- Sending service messages outside 24-hour customer service window.
- Hardcoding template names, token, phone number ID, WABA ID, or API version.
- Logging unmasked phone numbers, tokens, or full webhook payloads with PII.
- Blocking webhook response on heavy DB/business work.
- Ignoring `statuses[].errors`.
- Retrying `131049` aggressively.
- Implementing calling without checking explicit calling prerequisites and country restrictions.
