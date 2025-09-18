# RustyTags Primitive Component Rules

## Core Interaction Principles
- Adopt a Datastar-first mindset: wire interactivity through signals, reactive attributes, and inline expressions instead of external JavaScript helpers.
- Reach for native HTML features before custom logic (e.g., `<dialog>`, `popover` attributes, `<details>/<summary>` accordions, form elements with built-in validation).
- Keep JavaScript snippets inline and minimal; they should mainly set or read signals (e.g., `$open = true`, `on_click='$count = ($count || 0) + 1'`).
- Normalize only what is necessary via inline CSS (positioning, resets, user-provided hooks). Push all non-essential styling to consumer stylesheets.

## Signal Declaration & Scope
- Declare signals where the state lives: page-level templates, component roots, or nested containers (`Div(..., signals=Signals(is_open=False))`).
- Prefer primitives or simple objects for state; strings, booleans, and lightweight dicts/arrays ensure expressions stay readable.
- Expose customizable defaults through function parameters, but always back them with an explicit `Signals(...)` block. Document expected keys in component docstrings.

### Example: Scoped signal for a dialog trigger
```python
DialogShell(
    Button("Open dialog", on_click='$dialogOpen = true'),
    DialogContent(...),
    signals=Signals(dialogOpen=False)
)
```

## Reactive Attributes & Events
- Use direct assignment in event handlers to mutate signals (`on_click='$dialogOpen = !$dialogOpen'`). Prefer this over helper functions unless readability suffers.
- Project dynamic attributes with `data-attr-*`; align the suffix with the real attribute name.
- Bind form controls with `bind` for two-way sync when possible.

### Example: aria attributes bound to state
```python
Button(
    "Toggle",
    on_click='$dialogOpen = !$dialogOpen',
    data_attr_aria_expanded='$dialogOpen',
    data_attr_aria_controls='dialog-panel',
)
```

## Styling Hooks via Signals
- Use `data_style` and `data_class` JSON-like literals to react to signal changes.
- Favor arrays or maps to look up Open Props tokens from numeric signals; avoid string interpolation inside CSS variable names.

### Example: Open Props driven styling
```python
Div(
    cls="surface",
    data_style="{boxShadow: ['var(--shadow-1)','var(--shadow-2)'][$elevated ? 1 : 0], opacity: $dialogOpen ? 1 : 0.5}"
)
```

## Native-first Composition
- For anatomical patterns, start by composing native elements and attributes; enhance only when HTML cannot meet requirements (e.g., focus traps or nested signal coordination).
- Mirror native semantics through proper aria roles before layering additional behaviors.
- Use existing components (e.g., `Accordion`, `Tabs`) as baselines; improvements should retain native affordances while tightening Datastar integration.

## Development Flow
- When introducing a component, implement the primitive in `rusty_tags/components/` and immediately craft documentation in `lab/docs/pages/` following `instructions/DOCUMENTATION_FLOW.md`.
- Define demo functions (`example_basic`, `example_advanced`, etc.) at the top of the doc file; they must be import-safe and return ready-to-render components for `ComponentShowcase`.
- Register the new documentation route in `lab/docs/pages/__init__.py` and expose a link from `lab/docs/app.py`.
- Ensure each `ComponentShowcase` presents both live preview and code tabs; the showcased examples should exercise signals, reactive attributes, and styling hooks described above.
- Validate examples by running them in isolation (e.g., `print(example_basic())`) before wiring them into the docs page; this keeps demos deterministic for contributors and AI agents.

## Reference Materials
- Consult `rusty_tags.datastar` utilities for idiomatic helpers (e.g., `Signals`, `data_attr_*` patterns) before inventing new abstractions.
- Use the official Datastar documentation (<https://data-star.dev/>) to validate attribute syntax and advanced patterns (`data-style`, `data-class`, `bind`).

## Quality Gates
- Each component must demonstrate: signal declaration, reactive attributes, a styling hook, and at least one native HTML affordance.
- Reject implementations that rely on standalone JS files or custom global helpers; refactor them into Datastar expressions instead.
- Document keyboard and accessibility expectations alongside usage examples to keep the primitives predictable and copy-friendly.
