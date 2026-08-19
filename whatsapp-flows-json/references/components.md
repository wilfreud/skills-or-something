# Components

Official sources:

- https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/components
- https://developers.facebook.com/documentation/business-messaging/whatsapp/flows/guides/media_upload

## Component Families

Text:

- `TextHeading`
- `TextSubheading`
- `TextBody`
- `TextCaption`
- `RichText`

Entry:

- `TextInput`
- `TextArea`
- `DatePicker`
- `CalendarPicker`
- `Dropdown`
- `CheckboxGroup`
- `RadioButtonsGroup`
- `OptIn`

Action/display/control:

- `Footer`
- `EmbeddedLink`
- `Image`
- `If`
- `Switch`

Media upload:

- `PhotoPicker`
- `DocumentPicker`

## Common Properties

Many components support:

- `visible`: dynamic boolean, defaults true.
- `enabled`: dynamic boolean where available.
- `required`: dynamic boolean on inputs where available.
- `init-value`: available outside `Form` for supported components in Flow JSON
  `4.0+`.
- `error-message`: available outside `Form` for supported components in Flow
  JSON `4.0+`.

Every input component needs a stable `name`; names must be distinct on a screen.

## Text

Basic text components require `type` and `text`.

`TextBody` and `TextCaption` support limited markdown starting Flow JSON `5.1`
when `markdown=true`.

`RichText` was introduced in Flow JSON `5.1` for larger structured content. It
supports a subset of Markdown. Use it for standalone policies, terms, long
instructions, or rich documents. Use basic text components when text sits beside
interactive controls.

## TextInput and TextArea

`TextInput`:

- Required: `type`, `label`, `name`.
- `input-type`: `text`, `number`, `email`, `password`, `passcode`, or `phone`.
- `pattern` is supported starting Flow JSON `6.2` for selected input types and
  requires helper text.

`TextArea`:

- Required: `type`, `label`, `name`.
- Use for longer free text.

Keep labels short. Fetched component docs list label limits around 20
characters for text entry components.

## Choice Components

`CheckboxGroup`, `RadioButtonsGroup`, and `Dropdown` require `data-source`.

Data source objects use:

- `id`
- `title`
- optional `description`
- optional `metadata`
- optional `enabled`
- Flow JSON `5.0+` can also include image/color-related fields according to the
  fetched components guide.

Limits from fetched docs:

- `CheckboxGroup` and `RadioButtonsGroup`: 1 to 20 options.
- `Dropdown`: 1 option minimum; max 200 without images, 100 with images.

Images in WebP format are not supported on iOS versions before iOS 14.

## Date Components

`DatePicker`:

- Required: `type`, `label`, `name`.
- Starting Flow JSON `5.0`, values use `YYYY-MM-DD`, avoiding timezone coupling.
- Before Flow JSON `5.0`, cross-timezone behavior is not guaranteed. Avoid old
  DatePicker versions for cross-timezone users.

`CalendarPicker`:

- Supports single date or date range mode.
- Uses `YYYY-MM-DD`.
- Range mode values use `{ "start-date": "...", "end-date": "..." }`.

## Footer

`Footer` requires:

- `type`: `Footer`
- `label`
- `on-click-action`

Only one Footer per screen. Terminal screens require Footer.

## OptIn and EmbeddedLink

`OptIn` requires `type`, `label`, and `name`.

`OptIn` and `EmbeddedLink` can use `on-click-action`. Fetched docs list
`data_exchange` and `navigate`, with `open_url` allowed from Flow JSON `6.0+`.

## Conditional Components

`If`:

- Requires `condition` and non-empty `then`.
- Optional `else`.
- Allows nested `If` up to 3 levels.
- If a Footer appears inside `If`, it must appear in both branches and no
  Footer can exist outside that `If`.

`Switch`:

- Supported from Flow JSON `4.0`.
- Requires `value` and non-empty `cases`.
- Cases map string keys to arrays of components.

## Image

`Image` requires Base64 `src`.

`scale-type` can be `cover` or `contain`; default is `contain`.

When using `contain`, consider explicit height/width/aspect ratio because
Android may apply default height that creates spacing.

## Media Upload

`PhotoPicker`:

- Required: `type`, `name`, `label`.
- Optional `description`.
- `max-file-size-kb` default 25600, allowed 1 to 25600.
- `min-uploaded-photos` default 0, allowed 0 to 30.
- `max-uploaded-photos` default 30, allowed 1 to 30.
- Only one `PhotoPicker` per screen.

`DocumentPicker`:

- Required: `type`, `name`, `label`.
- Optional `description`.
- `max-file-size-kb` default 25600, allowed 1 to 25600.
- `min-uploaded-documents` default 0, allowed 0 to 30.
- `max-uploaded-documents` default 30, allowed 1 to 30.
- `allowed-mime-types` can restrict documents to supported MIME types.
- Only one `DocumentPicker` per screen.

Shared media upload rules:

- Do not use `PhotoPicker` and `DocumentPicker` on the same screen.
- Do not initialize them with Form `init-values`.
- Do not pass their values in `navigate` payload.
- Values are allowed only as top-level string properties in `data_exchange` or
  `complete` payloads.
- For endpoint data exchange, upload limits are up to 30 files per component.
- For response messages, no more than 10 files and 100 MiB aggregate.
