# Flow JSON Structure

Official source:
https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/flowjson

## Root Fields

Core root fields:

- `version`: Flow JSON version used for compilation and validation.
- `screens`: array of screens in the user experience.
- `routing_model`: directed graph of allowed screen transitions. Required when
  a Data Endpoint is used.
- `data_api_version`: version used for communication with the Flow Data
  Endpoint. The fetched Flow JSON guide says current value is `3.0`.

Endpoint URL rule:

- For Flow JSON `3.0+`, do not use `data_channel_uri`.
- Configure endpoint URL with Flows API `endpoint_uri`.

Size rule:

- Flow JSON content string must not exceed 10 MB.

## Screens

Common screen fields:

- `id`: stable screen identifier. Keep it uppercase/snake-like when possible.
- `title`: visible screen title.
- `data`: JSON Schema-like declaration for dynamic values rendered by
  components. Include `__example__` for preview data where needed.
- `terminal`: marks end states.
- `success`: optional on terminal screens; defaults to true.
- `layout`: screen UI layout object.
- `sensitive`: optional for Flow JSON `5.1+`; field names hidden in consumer
  response summaries.

Terminal screen rules:

- At least one terminal route is required.
- Terminal screens require a `Footer`.
- Do not use `navigate` on the Footer of a terminal screen.

Layout:

- Fetched docs list `SingleColumnLayout` as the available layout.
- Layout `children` holds components.

## Routing

Static Flow:

- If no Data Endpoint is used, routes can be inferred from `navigate` actions.
- Entry screen is the screen not targeted by any `navigate` action.

Endpoint Flow:

- Provide explicit `routing_model`.
- Server responses must comply with the declared routing graph.
- Route map keys are screen IDs; values are arrays of screen IDs reachable from
  that screen.
- All routes must end at terminal screen(s).
- Up to 10 branches can exist within the routing model.

Back behavior:

- If `refresh_on_back=true`, WhatsApp sends a Data Endpoint request when user
  goes back.
- The endpoint request action is `BACK`.

## Dynamic Data

References:

- Form value: `${form.field_name}`
- Current screen data: `${data.field_name}`
- Global screen data, Flow JSON `4.0+`: `${screen.SCREEN_ID.data.field_name}`

Use dynamic data for:

- Initial values.
- Visibility/enabled flags.
- Option arrays.
- Server-provided labels or copy.
- Validation errors.

For arrays used by `Dropdown`, `CheckboxGroup`, or `RadioButtonsGroup`, declare
`items.properties` with at least `id` and `title`, and include `__example__`.

## Forms

Before Flow JSON `4.0`, input collection normally uses a `Form` component with
`name` and `children`.

Starting with Flow JSON `4.0`, `Form` is optional. Components outside `Form` can
use:

- `init-value`
- `error-message`

Do not mix old and new patterns blindly. Check target Flow JSON version first.

## Actions

Supported action names from fetched Flow JSON guide:

- `navigate`: move to another screen with static payload.
- `data_exchange`: call Flow Data Endpoint with custom JSON payload.
- `complete`: terminate the Flow with submitted payload.

`navigate`:

- Primary static transition mechanism.
- Payload becomes next screen dynamic data.
- Do not use on terminal Footer.

`data_exchange`:

- Use when server must decide next screen, validate input, or provide data.
- Payload is customizable JSON.
- Avoid it when data is known at send time or from prior screens.

`complete`:

- Use on terminal screen as final user interaction.
- Flow response arrives through WhatsApp webhook.
