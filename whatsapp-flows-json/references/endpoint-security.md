# Endpoint Security And Data Exchange

Official source:
https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/implementingyourflowendpoint

## When Endpoint Is Needed

Use a Flow Data Endpoint when the server must:

- Provide dynamic screen data.
- Validate user input before moving on.
- Decide next screen.
- Complete the Flow from server logic.
- Handle media uploaded through Flow components.

Avoid endpoint calls when:

- First screen data is known when sending the message.
- Next screen and data are already known.
- Back navigation does not need custom refresh.

## Endpoint Setup

Endpoint requirements from fetched docs:

- Receive `POST` requests.
- Use HTTPS.
- Use valid TLS/SSL certificate.
- Configure URL on the Flow through `endpoint_uri`.
- Upload a public key; keep private key server-side.
- Use a dedicated endpoint and encryption key pair per WABA when operating as a
  Solution Partner.

## Request Envelope

Incoming encrypted request body contains:

- `encrypted_flow_data`: encrypted payload.
- `encrypted_aes_key`: encrypted 128-bit AES key.
- `initial_vector`: 128-bit initialization vector.

If request cannot be decrypted, return HTTP 421 so client can refresh public key
and retry, per fetched endpoint guide.

## Data API 3.0 Crypto

Request decryption:

1. Base64-decode `encrypted_aes_key`.
2. Decrypt AES key with private key corresponding to uploaded public key using
   RSA OAEP with SHA-256 and MGF1 SHA-256.
3. Base64-decode `encrypted_flow_data` and `initial_vector`.
4. Split encrypted flow data: ciphertext body plus final 16-byte AES-GCM auth
   tag.
5. Decrypt with AES-GCM, AES key, IV, and auth tag.
6. Parse UTF-8 JSON.

Response encryption:

1. Serialize response JSON to UTF-8.
2. Invert every bit of the request IV (`byte ^ 0xFF`) for response IV.
3. Encrypt with AES-GCM using same AES key and response IV.
4. Append auth tag to ciphertext.
5. Base64-encode full output.
6. Return encrypted string as plain text HTTP body.

## Signature Validation

Meta signs endpoint requests with SHA256 and sends signature in
`X-Hub-Signature-256` prefixed with `sha256=`.

Validate signature using the app secret before trusting decrypted payloads.

If validation fails, return an appropriate HTTP error from Meta endpoint error
guidance.

## Data Exchange Request

Decrypted payload fields:

- `version`: required, value `3.0`.
- `screen`: required except it may be absent/empty for `INIT` or `BACK`.
- `action`: required; `INIT`, `BACK`, or `data_exchange`.
- `flow_token`: required; business-generated session identifier.
- `data`: submitted payload.

Intermediate response:

```json
{
  "screen": "NEXT_SCREEN",
  "data": {
    "some_key": "some_value"
  }
}
```

Bad input:

- Return same or next screen with `data.error_message` to show snackbar error.
- Do not throw generic server errors for user-correctable validation.

Completion response:

```json
{
  "screen": "SUCCESS",
  "data": {
    "extension_message_response": {
      "params": {
        "flow_token": "FLOW_TOKEN"
      }
    }
  }
}
```

`SUCCESS` is reserved; do not name a normal screen `SUCCESS`.

## Error Notification Request

If endpoint previously returned invalid content, WhatsApp can send an async
error notification.

Payload includes:

- `version`
- `screen`
- `action`
- `data.error`
- `data.error_message`

Acknowledge with the documented success response. Log only redacted metadata.

## Health Check

WhatsApp may send:

```json
{
  "version": "3.0",
  "action": "ping"
}
```

Return the documented active health response. Keep health path fast and
dependency-light.

## Production Checklist

- Raw body available for signature verification.
- Constant-time signature compare.
- Private key loaded from secret manager/env, not code.
- Decryption errors return HTTP 421.
- Endpoint returns encrypted plain text, not JSON content.
- Routing responses match `routing_model`.
- `flow_token` validated and expired.
- Logs redact PII, tokens, AES keys, private keys, media IDs, decrypted request
  bodies, and encrypted envelopes.
- Timeouts and retries considered; endpoint-powered Flows must meet Meta health
  and performance requirements.
