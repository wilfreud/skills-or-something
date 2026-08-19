# Webhooks and Errors

Fetch relevant Meta page first:

- Webhook endpoint setup: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint
- Messages webhook reference: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages
- Status webhook reference: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/status
- Error codes: https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes

## Webhook Endpoint

Endpoint must be public over valid TLS. Self-signed certs are not supported.

GET verification:

- Meta calls callback with `hub.mode=subscribe`, `hub.challenge`, `hub.verify_token`.
- Compare `hub.verify_token` with server-stored verify token.
- On match: respond 200 with raw `hub.challenge`.
- On mismatch: respond non-200 / 4xx.

POST events:

- Validate `X-Hub-Signature-256: sha256=...` with HMAC-SHA256 over raw request body using app secret.
- Use timing-safe comparison where platform supports it.
- Return 200 fast after validation; move expensive work async.
- Subscribe to and handle the `messages` webhook field for incoming messages and outbound statuses.
- Deduplicate: Meta retries failed webhook delivery immediately, then with decreasing frequency for up to 7 days.
- Store raw/enough event data when needed; Meta does not provide historical webhook fetch.

## Payload Interpretation

Incoming user messages:

- `object` should be `whatsapp_business_account`.
- `entry[].changes[].value.messages[]` contains message objects.
- `entry[].changes[].value.contacts[]` may contain profile and `wa_id`.
- `entry[].changes[].value.metadata.phone_number_id` identifies recipient business phone number.

Outgoing delivery updates:

- `entry[].changes[].value.statuses[]` contains status objects.
- Status webhooks describe status, not original outgoing content.
- Each outgoing message can generate multiple status webhooks.
- Status objects can contain `conversation`, `pricing`, and `errors`.

Error locations:

- System/app/account errors: `entry.changes.value.errors`.
- Incoming message errors: `entry.changes.value.messages.errors`.
- Outgoing send errors: `entry.changes.value.statuses.errors`.

## Error Handling

Meta recommends error handling around `code` and `error_data.details`, not HTTP status or error title text. Cloud API errors can be synchronous Graph API responses, asynchronous webhook errors, or both.

Always log:

- Graph `code`.
- `error_data.details`.
- `fbtrace_id`.
- HTTP status.
- provider message ID / correlation ID when available.

Never log bearer token, full user phone, or full PII payload.

## High-Signal Codes

Auth and permissions:

- `0`, `3`, `10`, `190`, `200`: auth/permission/token problem.

Rate and quality:

- `4`: app API call rate limit.
- `80007`: WABA rate limit.
- `130429`: Cloud API throughput limit.
- `131048`: spam/quality sending restriction.
- `131049`: withheld to preserve ecosystem engagement; do not mislabel as template-shape error.
- `131056`: too many messages from same sender to same recipient in short period.
- `131064`: messaging limit due to template classification violations.

Request and recipient:

- `100`: unsupported or misspelled parameter.
- `131008`: missing parameter.
- `131009`: invalid parameter value.
- `131021`: sender and recipient are same.
- `131026`: unable to deliver; can mean non-WhatsApp number, user terms/version issue, or similar recipient problem.
- `131047`: outside 24-hour service window; send template instead.
- `131050`: user stopped receiving marketing messages.
- `131051`: unsupported message type.

Media:

- `131052`: incoming media too large or cannot be downloaded.
- `131053`: media upload/send failed; inspect MIME and supported media type.

Templates:

- `132000`: parameter count mismatch.
- `132001`: template missing in language or not approved.
- `132012`: variable parameter format mismatch.
- `132015`: template paused for low quality.
- `132016`: template disabled after repeated pauses.

Registration:

- `133010`: phone number not registered on WhatsApp Business Platform.

## Retry Stance

- Retry transient platform errors only with bounded backoff and correlation logging.
- Do not aggressively retry rate, quality, opt-out, template disabled, or policy errors.
- For `131049`, wait and review message quality/frequency. Immediate retry can worsen outcome.
