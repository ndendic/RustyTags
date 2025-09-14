from typing import Any, Literal

import rusty_tags as rt
from .utils import cn


def Button(
    *children: Any,
    type: Literal["button", "submit", "reset"] = "button",
    disabled: bool = False,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """
    Simple button component with automatic accessibility features.
    
    Args:
        *children: Button content (text, icons, etc.)
        type: Button type for forms
        disabled: Whether button is disabled
        cls: CSS classes
        **attrs: Additional HTML attributes (including on_click, etc.)
    
    Returns:
        Button HTML element with accessibility features
    """
    # Build attributes with accessibility
    button_attrs = {
        "type": type,
        "disabled": disabled,
        "cls": cls,
        # Automatic accessibility
        "role": "button",
        "tabindex": "0" if not disabled else "-1",
        "aria-disabled": "true" if disabled else "false",
        **attrs
    }
    
    # Add keyboard support if there's a click handler and button isn't disabled
    if "on_click" in attrs and not disabled:
        original_click = attrs["on_click"]
        button_attrs["on_keydown"] = f"if (evt.key === 'Enter' || evt.key === ' ') {{ evt.preventDefault(); {original_click} }}"
    
    return rt.Button(*children, **button_attrs)