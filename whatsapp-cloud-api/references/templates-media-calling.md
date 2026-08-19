# Templates, Media, Documents, Calling

Fetch relevant Meta page first:

- Templates: https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview
- Media: https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/media
- Document messages: https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/document-messages
- Calling: https://developers.facebook.com/documentation/business-messaging/whatsapp/calling

## Templates

Templates are WABA assets and must be approved before sending.

Implementation rules:

- Keep template names in one typed registry or constant map.
- Store language code with each template.
- Prefer typed builder functions for known templates so call sites do not assemble brittle component arrays.
- For positional params, send values in exact placeholder order.
- For named params, include `parameter_name` and match approved lowercase/underscore names.
- Verify status via Template API or WhatsApp Manager when errors mention missing/unapproved templates.
- Treat template `message_status` in send response as pacing info, not final delivery.

Template creation facts from Meta docs:

- Names can repeat across languages.
- Names are lowercase alphanumeric and underscores, max 512 chars.
- Categories are authentication, marketing, or utility.
- Template strings and variables are not translated by Meta.
- Template status must be `APPROVED` before send.
- Status changes can arrive through `message_template_status_update` webhooks.

Common template errors:

- `132000`: parameter count mismatch.
- `132001`: template does not exist in language or is not approved.
- `132012`: variable parameter format mismatch.
- `132015`: template paused for low quality.
- `132016`: template disabled after repeated pauses.

## Media

Prefer uploaded media `id` over hosted `link` for repeat sends and larger assets.

Media endpoints:

- Upload: `POST /{Phone-Number-ID}/media` with multipart `messaging_product=whatsapp`, `file`, and MIME `type`.
- Get media URL: `GET /{Media-ID}`.
- Download media: `GET {Media-URL}` with bearer token.
- Delete media: `DELETE /{Media-ID}`.

Lifetimes and caching:

- Uploaded media persists up to 30 days unless deleted.
- Media IDs from incoming webhooks are available for download for 7 days.
- Media URLs expire after 5 minutes.
- Hosted media `link` sends are cached by Cloud API for 10 minutes.

Validate MIME type and size before sending. Common supported limits from Meta docs:

- Images: JPEG/PNG, 5 MB.
- Audio: AAC/AMR/MP3/M4A/OGG OPUS mono, 16 MB.
- Video: 3GPP/MP4 H.264 + AAC, 16 MB.
- Documents: TXT, XLS/XLSX, DOC/DOCX, PPT/PPTX, PDF, 100 MB.
- Stickers: WebP, static 100 KB, animated 500 KB.

For video compatibility, Meta recommends H.264 Main without B-frames or Baseline, AAC audio, and fast-start moov box placement.

## Document Messages

Document payload:

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "+16505551234",
  "type": "document",
  "document": {
    "id": "1376223850470843",
    "filename": "invoice.pdf",
    "caption": "Your invoice"
  }
}
```

Rules:

- Use `document.id` for uploaded media, or `document.link` for public hosted media.
- `filename` should include extension so client can display correct file icon.
- `caption` max is 1024 chars per document docs.
- Supported document types are the official list only; other file types may send but are not guaranteed to render correctly.

## Calling

Do not treat WhatsApp Calling as automatically available with messaging.

Before implementing calling:

- Confirm business number is using Cloud API, not WhatsApp Business app.
- Subscribe app to `calls` webhook field unless using SIP.
- Ensure same app is subscribed to the WABA for that phone number.
- Ensure `whatsapp_business_messaging` permission.
- Enable calling features on business phone number.
- Check country availability and production limits.

As of fetched Meta docs, business-initiated calling is unavailable for sender business phone numbers in the United States, Canada, Egypt, Vietnam, and Nigeria. Re-fetch before coding because availability changes.

Calling architecture can use Graph APIs + webhooks by default, or SIP with explicit enablement. Do not implement SIP assumptions without fetching SIP docs.
