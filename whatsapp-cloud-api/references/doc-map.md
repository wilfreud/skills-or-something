# WhatsApp Cloud API Documentation Map

Use this file as route map. Always fetch exact official Meta page before relying on details. Prefer `.md` variants when available, but preserve original user-facing URLs in notes.

## Primary Send Reference

- Messages API: https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/message-api

Use this before touching any outbound send payload. It defines `POST /{Version}/{Phone-Number-ID}/messages`, shared message properties, message-specific sibling objects, and response shape.

## Required Official Sources

- Cloud API root: https://developers.facebook.com/docs/whatsapp/cloud-api/
- WhatsApp docs root: https://developers.facebook.com/docs/whatsapp/
- Get started: https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started
- Overview: https://developers.facebook.com/documentation/business-messaging/whatsapp/overview
- About the platform: https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform
- Service messages / send messages: https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/send-messages
- Document messages: https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/document-messages
- Calling: https://developers.facebook.com/documentation/business-messaging/whatsapp/calling

## High-Value Supporting Sources

- Templates overview: https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/overview
- Template components: https://developers.facebook.com/documentation/business-messaging/whatsapp/templates/components
- Message Template API: https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-account/message-template-api
- Webhook endpoint setup: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/create-webhook-endpoint
- Messages webhook reference: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages
- Status webhook reference: https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/status
- Error codes: https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes
- Media: https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/media
- Media Upload API: https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/whatsapp-business-phone-number/media-upload-api
- Media API: https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/media/media-api
- Media Download API: https://developers.facebook.com/documentation/business-messaging/whatsapp/reference/media/media-download-api
- Access tokens: https://developers.facebook.com/documentation/business-messaging/whatsapp/access-tokens
- Phone numbers: https://developers.facebook.com/documentation/business-messaging/whatsapp/business-phone-numbers/phone-numbers
- Messaging limits: https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits
- Throughput: https://developers.facebook.com/documentation/business-messaging/whatsapp/throughput
- Platform status: https://metastatus.com/whatsapp-business-api

## Source Priority

1. Fresh `developers.facebook.com` task-specific page.
2. Fresh linked Meta page from that doc.
3. Existing project code and types.
4. This skill's references.
5. Third-party examples only for contrast, never as authority.

Do not rely on old Postman collections, StackOverflow, blog snippets, or memory when official Meta docs disagree.
