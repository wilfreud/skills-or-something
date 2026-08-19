# Sending And Flows API

Official sources:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/sendingaflow
- https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/flowsapi
- https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/versioning

## Sending A Flow Message

Cloud API sends a Flow as an interactive message:

- `interactive.type`: `flow`
- `interactive.action.name`: `flow`
- `interactive.action.parameters.flow_message_version`: `3`
- exactly one of `flow_id` or `flow_name`
- `flow_cta`: CTA text, Meta advises 30 characters or less and no emoji
- `mode`: `published` by default; use `draft` only for testing draft version
- `flow_token`: business-generated session identifier
- `flow_action`: `navigate` or `data_exchange`; default is `navigate`
- `flow_action_payload.screen`: first screen ID
- `flow_action_payload.data`: optional non-empty object for first screen data

Use `flow_id` when possible. `flow_name` breaks if the Flow is renamed.

Use `mode=draft` only when intentionally testing a draft. Production sends
should target `published`.

## Flow Token

Treat `flow_token` like a session identifier:

- Generate unpredictably.
- Bind it to the expected user/session/server state.
- Expire it.
- Do not log it raw.
- Validate it on endpoint requests and webhook processing.

## Flows API Base

Flows API is a Graph API.

Base pattern:

- `POST /{WABA-ID}/flows`: create Flow.
- `POST /{FLOW-ID}`: update Flow metadata.
- `POST /{FLOW-ID}/assets`: update Flow JSON asset as form-data.
- `GET /{FLOW-ID}?fields=preview.invalidate(false)`: retrieve preview URL.
- `DELETE /{FLOW-ID}`: delete draft Flow.
- `GET /{WABA-ID}/flows`: list Flows.
- `GET /{FLOW-ID}`: retrieve Flow details.
- `GET /{FLOW-ID}/assets`: list Flow assets.
- `POST /{FLOW-ID}/publish`: publish Flow.
- `POST /{FLOW-ID}/deprecate`: deprecate Flow.

## Create And Update

Create Flow can include:

- `name`
- `categories`
- `flow_json`
- `publish`
- `clone_flow_id`
- `endpoint_uri`

For Flow JSON `3.0+`, specify endpoint with API `endpoint_uri`, not
`data_channel_uri`.

Updating Flow JSON uses `/assets` and file upload/form-data. Every update can
return validation errors.

## Lifecycle

Fetched docs list statuses:

- `DRAFT`: still under development; only send with `mode=draft`.
- `PUBLISHED`: can be sent to customers; cannot be deleted or updated.
- `DEPRECATED`: retired; cannot be sent/opened/restored.
- `BLOCKED`: endpoint unhealthy; cannot be sent/opened until fixed.
- `THROTTLED`: endpoint unhealthy; limited sending/opening behavior until fixed.

Publishing requires:

- No validation errors.
- Publishing checks resolved.
- Compliance with WhatsApp Flows design principles.

Once published, a Flow cannot be modified or deleted. Deprecate instead.

## Permissions

Flows API troubleshooting docs mention:

- Access token scopes should include `whatsapp_business_management` and
  `whatsapp_business_messaging`.
- Granular scopes must include the WABA under both scopes.
- Business permissions needed include Message templates view/manage and Phone
  Numbers view/manage.

Verify permissions using official Meta tooling, not guesswork.

## Versioning

Meta distinguishes:

- Flow JSON version: controls components/layout behavior.
- Message version: controls message payload version.
- Data API version: controls endpoint encryption and payload format.

Version numbers are strings for Flow JSON/Data API and integer-like for message
version. `1.10` is later than `1.9`; do not compare as decimals.

Version lifecycle states:

- Frozen: cannot create/update/publish new Flows targeting version, but existing
  Flows may still send/open.
- Expired: Flows targeting version can no longer send or open.

Always check Meta changelog for supported versions, freeze dates, and expiry
dates before production publishing.
