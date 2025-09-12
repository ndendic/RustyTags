## DataStar + Open Props in rustyTags: precise implementation guide

This guide codifies patterns used in the `lab/FastapiApp.py` playground to combine DataStar reactivity with Open Props tokens and OPUI components using rustyTags. It is intended for future contributors and AI assistants.

### 1) Prerequisites and imports

- Ensure Open Props and OPUI CSS are imported in your public stylesheet, and that the HTML includes it:
  - In CSS entry (already present): `@import "./open-props.css"; @import "./opui.css"; @import "./theme.css";`
  - In Python template headers:
    - `Link(rel='stylesheet', href='/static/css/main.css')`
    - Optional debugging: `Script(src="/static/js/datastar-inspector.js", type="module")` plus `<datastar-inspector />` feature element.

References: [Open Props](https://open-props.style/)

### 2) Signals: where and how to declare

- Page-level (via template):
  - `bodykws = dict(cls="page", data_class="{dark: $dark, light: !$dark}", signals=Signals(message="", conn=""))`
  - Passing `signals=Signals(...)` attaches initial reactive state to the element. All children can read `$signalName`.
- Section/container-level:
  - Any component can define a scoped signals object: `Div(..., signals=Signals(rds=[...]))`. Children see `$rds` in expressions.
- Allowed values include primitives, arrays, and objects (JSON-serializable).

### 3) Two-way binding to inputs

- Prefer direct `bind` for simple inputs instead of event handlers:
  - Example: `HTMLInput(type='range', min='1', max='5', value='3', bind='intensity')`
  - This keeps `$intensity` in sync with the control.

### 4) Event handling patterns

- Use direct assignment in event attributes for simplicity:
  - Toggle: `on_click='$dark = !$dark'`
  - Increment: `on_click='$count = ($count || 0) + 1'`
- The `DS.set(...)` helper also works, but assignment is shorter and idiomatic in these examples.

### 5) Dynamic styles with data_style

- Use `data_style` with a JavaScript object literal string. Keys are CSS properties in camelCase; values can be strings, numbers, ternaries, arrays, and signal expressions.

- Example A: toggle radius and choose a shadow by intensity

  Python (rustyTags):
  ```python
  Div(
      Button(
          "Toggle rounded",
          cls="button filled",
          on_click='$rounded = !$rounded',
          # You may attach data_style here or on a sibling; either is fine.
      ),
      HTMLInput(type='range', min='1', max='5', value='3', bind='intensity'),
      Div(
          "I react to signals via data-style",
          cls="content",
          data_style="{borderRadius: $rounded ? 'var(--radius-5)' : 'var(--radius-2)', boxShadow: ['var(--shadow-1)','var(--shadow-2)','var(--shadow-3)','var(--shadow-4)','var(--shadow-5)'][$intensity - 1], padding: 'var(--size-5)', background: 'var(--surface-default)'}"
      ),
      style="display: grid; gap: var(--size-4);"
  )
  ```

- Why arrays: CSS custom properties cannot be concatenated like `var(--shadow-${n})`. Use array lookup to map numeric signals to tokens:
  ```js
  ['var(--shadow-1)','var(--shadow-2)','var(--shadow-3)','var(--shadow-4)','var(--shadow-5)'][$intensity - 1]
  ```

- Safer/clamped lookup variant:
  ```js
  const i = Math.max(0, Math.min(4, ($intensity|0) - 1));
  ['var(--shadow-1)','var(--shadow-2)','var(--shadow-3)','var(--shadow-4)','var(--shadow-5)'][i]
  ```

- Example B: supply a token list via signals and index it
  ```python
  Div(
      ...,
      signals=Signals(rds=[f"var(--radius-{i})" for i in range(1, 6)]),
  )
  # then in data_style
  "{ borderRadius: $rounded ? $rds[$intensity - 1] : 'var(--radius-1)' }"
  ```

Reference: [DataStar data-style](https://data-star.dev/reference/attributes#data-style)

### 6) Dynamic classes with data_class

- Prefer a single `data_class` object mapping class names to boolean expressions:
  - Page/theme example (on `body` via template): `data_class="{dark: $dark, light: !$dark}"`
  - Local example: `Div(..., data_class="{open: $isOpen, loading: $loading}")`
- This replaces per-class attributes like `data-class-dark` and `data-class-light` with a concise, scalable mapping.

Reference: DataStar classes follow the same object-literal pattern as styles.

### 7) Using Open Props tokens and OPUI components

- Tokens: Favor Open Props variables for sizes, radii, shadows, gradients, typography, media, etc. Examples:
  - Spacing: `gap: var(--size-4)`
  - Shape: `border-radius: var(--radius-3)`
  - Shadows: `box-shadow: var(--shadow-3)`
  - Gradients: `background: var(--gradient-12)`

- OPUI components (class-based):
  - Buttons: `cls="button filled|outlined|tonal|elevated"`
  - Card layout: container `cls="card outlined|elevated"` with inner `.content`, `.actions`, and optional `hgroup` headings.

### 8) Common end-to-end patterns

- Theme toggle (page-wide):
  ```python
  # Template body (via page/create_template): data_class="{dark: $dark, light: !$dark}"
  Button("Toggle theme", cls="button outlined", on_click='$dark = !$dark')
  ```

- Intensity slider controlling shadow depth:
  ```python
  HTMLInput(type='range', min='1', max='5', value='3', bind='intensity')
  Div(data_style="{ boxShadow: ['var(--shadow-1)','var(--shadow-2)','var(--shadow-3)','var(--shadow-4)','var(--shadow-5)'][$intensity - 1] }")
  ```

- Radius toggle with token list in signals:
  ```python
  Div(
      Button("Toggle rounded", on_click='$rounded = !$rounded'),
      Div(data_style="{ borderRadius: $rounded ? $rds[$intensity - 1] : 'var(--radius-1)' }"),
      signals=Signals(rds=[f"var(--radius-{i})" for i in range(1, 6)])
  )
  ```

### 9) Do and Don’t

- Do: use arrays or maps to select between Open Props tokens based on a numeric signal.
- Do: prefer `bind` for simple form controls.
- Do: use `data_class` with an object literal to toggle multiple classes succinctly.
- Don’t: attempt string interpolation inside `var(...)` names (e.g., `var(--shadow-${n})`).
- Don’t: mix per-class attributes (`data-class-foo`) when `data_class` mapping can cover all cases.

### 10) Debugging

- Use `<datastar-inspector />` and the module script to introspect signals and element bindings during development.

---

This guide mirrors the working patterns in `lab/FastapiApp.py` and should be used as the reference for future DataStar + Open Props work in this repo.


### 11) Token layering and robust fallbacks (critical)

Problem we hit: component variables like `--sheet-bg`, `--sheet-text`, `--sheet-border` referenced theme tokens (e.g., `--surface-default`, `--text-color-1`, `--field-border-color`). If those theme tokens are undefined in scope or later a shorthand rule resets `background`, `background-color` could resolve to transparent, making panels look see-through.

Rules to follow:
- Define component-local tokens with layered fallbacks to theme tokens and then to a literal value.
- Prefer `background: var(--token)` on containers/panels to avoid being reset by later `background:` shorthands.
- Keep specificity reasonable; use attribute selectors already on the element where possible.

Example (from `components/sheet.css`):
```css
:root {
  /* Component-local tokens → theme tokens → hard fallbacks */
  --sheet-bg: var(--surface-default, white);
  --sheet-border: var(--field-border-color, var(--border-color, oklch(0 0 0 / 15%)));
  --sheet-text: var(--text-color-1, CanvasText);
}

[data-sheet-role="content"] {
  /* Use shorthand so later background: rules don't clear our color */
  background: var(--sheet-bg);
  color: var(--sheet-text);
  border-left: 1px solid var(--sheet-border);
}
```

Anti-patterns to avoid:
- Setting only `background-color:` while a later stylesheet uses `background:` on the same element.
- Depending exclusively on theme tokens without providing a final literal fallback.

Where to place tokens:
- Theme layer (`theme.css`): define global tokens like `--surface-default`, `--text-color-1`, `--field-border-color`.
- Component layer: define component-scoped tokens that fall back to theme tokens, then literals; consume them with `background:` on containers.

References: [Open Props](https://open-props.style/)


