# RustyTags DX Enhancement Plan

## Overview
Enhance developer experience by adding modern web development patterns while maintaining RustyTags' performance and simplicity focus.

## 1. CSS & Styling Enhancements

### CSS Class Utilities
```python
from rusty_tags.utils import cn, cva

# Class name concatenation with conditional logic
classes = cn(
    "base-class",
    "text-blue-500" if is_primary else "text-gray-500",
    {"active": is_active, "disabled": is_disabled}
)
Div(cls=classes)

# Component variant API (inspired by class-variance-authority)
button_variants = cva(
    "btn",  # base classes
    variants={
        "variant": {
            "primary": "bg-blue-500 text-white",
            "secondary": "bg-gray-500 text-white",
            "ghost": "bg-transparent"
        },
        "size": {
            "sm": "px-2 py-1 text-sm",
            "md": "px-4 py-2",
            "lg": "px-6 py-3 text-lg"
        }
    }
)

Button("Click me", cls=button_variants(variant="primary", size="md"))
```

### Style Object Builder
```python
from rusty_tags.utils import style

# CSS-in-JS style objects
styles = style({
    "color": "#333",
    "fontSize": "16px",
    "marginTop": "1rem",
    "backgroundColor": theme.colors.primary if is_primary else theme.colors.secondary
})
Div(style=styles)
```

## 2. Conditional Rendering & Control Flow

### Conditional Utilities
```python
from rusty_tags.utils import when, unless, show_if

# Conditional rendering helpers
content = Div(
    H1("Welcome"),
    when(user_logged_in, lambda: P(f"Hello {username}")),
    unless(is_loading, lambda: Button("Submit")),
    show_if(has_errors, lambda: Div(error_messages, cls="error"))
)

# List rendering with automatic keys
from rusty_tags.utils import render_list

items = render_list(
    products,
    lambda product: Div(
        H3(product.name),
        P(product.description),
        cls="product-card"
    ),
    key=lambda p: p.id  # automatic key generation
)
```

### Enhanced Fragment Support
```python
from rusty_tags import Fragment

# Multiple root elements without wrapper
def ProductCard(product):
    return Fragment(
        H3(product.name),
        P(product.description),
        P(f"${product.price}")
    )

# Conditional fragments
Fragment.when(condition, H1("Title"), P("Content"))
```

## 3. Component Patterns

### Component Factory
```python
from rusty_tags.utils import component

@component
def Card(title: str, children, variant="default", **attrs):
    """Reusable card component with variants"""
    base_classes = "rounded shadow p-4"
    variant_classes = {
        "default": "bg-white border",
        "primary": "bg-blue-50 border-blue-200",
        "warning": "bg-yellow-50 border-yellow-200"
    }

    return Div(
        H3(title, cls="font-bold mb-2") if title else None,
        Div(*children, cls="content"),
        cls=f"{base_classes} {variant_classes[variant]}",
        **attrs
    )

# Usage with type hints and validation
card = Card(
    "My Card",
    [P("Content here"), Button("Action")],
    variant="primary",
    id="main-card"
)
```

### Slot/Children Patterns
```python
from rusty_tags.utils import slot

@component
def Modal(title, children, footer=None):
    return Div(
        Div(
            H2(title, cls="modal-title"),
            Div(*children, cls="modal-body"),
            slot(footer, lambda f: Div(f, cls="modal-footer"))
        ),
        cls="modal"
    )
```

## 4. Developer Tools & Debugging

### HTML Validation & Pretty Printing
```python
from rusty_tags.utils import validate, pretty_print

html = Div(H1("Title"), P("Content"))

# Validate HTML5 semantics
issues = validate(html)  # Returns accessibility and semantic issues

# Pretty print for debugging
print(pretty_print(html, indent=2, highlight_datastar=True))

# Development mode with warnings
import os
if os.getenv("DEBUG"):
    html.debug()  # Shows attribute processing, performance metrics
```

### Performance Insights
```python
from rusty_tags.utils import profile

with profile() as prof:
    complex_page = Page(
        *[Div(f"Item {i}") for i in range(1000)]
    )

prof.report()  # Shows generation time, memory usage, cache hits
```

## 5. Responsive & Modern CSS Patterns

### Responsive Utilities
```python
from rusty_tags.utils import responsive

# Responsive class builder
classes = responsive({
    "base": "p-4",
    "sm": "p-6",
    "md": "p-8",
    "lg": "p-12"
})  # Generates: "p-4 sm:p-6 md:p-8 lg:p-12"

# Responsive style objects
styles = responsive({
    "base": {"fontSize": "14px"},
    "md": {"fontSize": "16px"},
    "lg": {"fontSize": "18px"}
})
```

### CSS Grid & Flexbox Helpers
```python
from rusty_tags.utils import grid, flex

# CSS Grid helper
layout = grid(
    items,
    cols="1fr 1fr 1fr",
    gap="1rem",
    render_item=lambda item: Div(item.name, cls="grid-item")
)

# Flexbox helper
navbar = flex(
    [Logo(), Nav(), UserMenu()],
    direction="row",
    justify="space-between",
    align="center"
)
```

## 6. Accessibility & Semantic Helpers

### A11y Utilities
```python
from rusty_tags.utils import aria, accessible

# ARIA attribute helpers
button = Button(
    "Toggle Menu",
    **aria(
        expanded=is_open,
        controls="mobile-menu",
        label="Toggle navigation menu"
    )
)

# Semantic validation
form = accessible.form(
    accessible.field("Name", Input(type="text"), required=True),
    accessible.field("Email", Input(type="email"), required=True),
    accessible.submit("Submit Form")
)
```

## 7. Context & Theme Support

### Theme Context
```python
from rusty_tags.utils import Theme, use_theme

theme = Theme({
    "colors": {"primary": "#3b82f6", "secondary": "#6b7280"},
    "spacing": {"sm": "0.5rem", "md": "1rem", "lg": "2rem"},
    "fonts": {"sans": "Inter, sans-serif"}
})

@use_theme(theme)
def ThemedButton(text, variant="primary"):
    return Button(
        text,
        style={
            "backgroundColor": f"var(--color-{variant})",
            "padding": "var(--spacing-md)",
            "fontFamily": "var(--font-sans)"
        }
    )
```

## 8. Enhanced Type Safety

### Attribute Validation
```python
from rusty_tags.utils import typed_component, Props

class ButtonProps(Props):
    variant: Literal["primary", "secondary", "ghost"] = "primary"
    size: Literal["sm", "md", "lg"] = "md"
    disabled: bool = False

@typed_component
def Button(children, props: ButtonProps, **attrs):
    return button(
        *children,
        cls=f"btn btn-{props.variant} btn-{props.size}",
        disabled=props.disabled,
        **attrs
    )
```

## 9. Animation & Interaction Helpers

### CSS Animation Utilities
```python
from rusty_tags.utils import animate, transition

# Animation helpers
loading_spinner = Div(
    cls=animate("spin", duration="1s", iteration="infinite")
)

# Transition helpers for Datastar
modal = Div(
    cls=transition(
        enter="opacity-0",
        enter_active="transition-opacity duration-300",
        enter_to="opacity-100"
    ),
    show="$showModal"
)
```

## Implementation Priority:

**Phase 1 (High Impact, Low Complexity):**
- CSS class utilities (cn, cva)
- Conditional rendering (when, unless, show_if)
- Pretty printing & debugging
- Fragment enhancements

**Phase 2 (Medium Complexity):**
- Component factory patterns
- Responsive utilities
- List rendering helpers
- Style object builders

**Phase 3 (Advanced Features):**
- Theme context system
- Type safety enhancements
- Performance profiling
- Accessibility validators

**Benefits:**
- Maintains RustyTags' performance focus
- Adds modern DX patterns developers expect
- Keeps core lightweight (utilities are optional imports)
- Provides progressive enhancement path
- Improves accessibility and maintainability