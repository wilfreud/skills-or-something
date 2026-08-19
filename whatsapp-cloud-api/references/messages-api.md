# Messages API Patterns

Fetch the primary send reference before using exact fields:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/message-api
- https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages

## Endpoint

All standard sends go through:

```text
POST https://graph.facebook.com/{Version}/{Phone-Number-ID}/messages
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

Common JSON shape:

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+16505551234",
  "type": "text",
  "text": {
    "body": "Hello"
  }
}
```

Rules:

- `type` decides which sibling object must exist: `text`, `template`, `image`, `document`, `interactive`, `reaction`, `location`, etc.
- Use `recipient_type: "individual"` for 1:1 messages unless working with the Groups API.
- Include plus sign and country code for user phone numbers. Without `+`, Cloud API may prepend sender country code and misdeliver.
- Plus signs, hyphens, parentheses, and spaces are accepted, but normalized E.164 storage is easier to audit.

## Send Response Is Not Delivery

A 200 response means Meta accepted the request, not that WhatsApp delivered it.

Use:

- `contacts[0].input`: submitted number.
- `contacts[0].wa_id`: WhatsApp user ID.
- `messages[0].id`: `wamid...`, provider ref/correlation key.
- `messages[0].message_status`: template pacing status when present, not final delivery.

Final outcome comes through `messages` webhook statuses: usually `sent`, `delivered`, `read`, or `failed`.

## Service Window

Service messages are free-form non-template messages. They can be sent only inside the 24-hour customer service window opened or refreshed when the user messages or calls the business.

Outside that window, use approved templates.

Always require opt-in before initiating WhatsApp business messaging.

## Supported Service Message Types

Meta service-message docs currently route these through Messages API:

- Address
- Audio
- Contacts
- Document
- Image
- Interactive CTA URL button
- Interactive voice call
- Interactive Flow
- Interactive list
- Interactive location request
- Interactive reply buttons
- Location
- Sticker
- Text
- Video
- Reaction

Fetch exact message-type page before implementing specialized payloads.

## Sequencing, TTL, and Caching

- Delivery order for multiple API calls is not guaranteed. If order matters, wait for `delivered` status before sending next message.
- Default TTL is 30 days for most messages.
- Authentication template TTL defaults to 10 minutes.
- If no `delivered` status arrives before TTL is exceeded, treat message as dropped.
- Hosted media links are cached by Cloud API for 10 minutes; use uploaded media IDs when possible.

## Centralized Client Requirements

Put this in one service/client boundary:

- URL construction from configured API version and phone number ID.
- Bearer auth.
- JSON headers.
- timeout.
- response provider ref extraction.
- error extraction.
- PII-safe logs.
- metrics/audit/event emission.

Do not let business call sites assemble raw Graph API requests.
