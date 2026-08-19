# Official Meta Doc Map

Fetch these official Meta pages when precision matters. Docs change often; do
not rely on memory for version-sensitive decisions.

## User-Provided Official Links

- WhatsApp Flows overview:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows
- Flow JSON guide:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/flowjson
- Flow JSON reference route:
  https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson
- Components reference route:
  https://developers.facebook.com/docs/whatsapp/flows/reference/components
- Get started:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/gettingstarted
- Guides index:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides
- Sending Flows:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/sendingaflow
- Flows API:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/flowsapi
- Implementing Flow endpoints:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/implementingyourflowendpoint
- Examples:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/examples
- Playground:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/playground
- WhatsApp Flows docs route:
  https://developers.facebook.com/docs/whatsapp/flows

## Additional Official Pages Used By This Skill

- Components guide:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/components
- Media upload components:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/media_upload
- Versioning:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/versioning
- Changelog and supported versions:
  https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/changelogs

## Fetch Notes From Skill Creation

All user-provided URLs were fetched on 2026-08-19 from
`developers.facebook.com`.

Several `.md` variants were clean and useful:

- `guides/flowjson.md`
- `guides/sendingaflow.md`
- `guides/flowsapi.md`
- `guides/implementingyourflowendpoint.md`
- `guides/examples.md`
- `guides/components.md`
- `guides/media_upload.md`
- `guides/versioning.md`

Some `docs/whatsapp/...` reference routes produced app HTML or markdown 404
content instead of clean markdown in this environment. Treat that as a fetch
format issue, not as proof the public route is invalid. Prefer the
`documentation/business-messaging/.../guides/...` route for machine-readable
content when available.

The changelog returned HTTP 500 via `curl` and 429 via browser fetch during
skill creation. Recheck before claiming latest supported Flow JSON version.
