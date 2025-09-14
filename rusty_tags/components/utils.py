from collections.abc import Callable
from typing import Any, Dict, Optional
import uuid

from rusty_tags import HtmlString, I, Script
from rusty_tags.datastar import Signals


def Icon(icon: str, **attrs) -> HtmlString:
    """Iconify icon element. Usage: Icon("home", cls="h-4 w-4")"""
    return I(Script("lucide.createIcons();"),data_lucide=icon, **attrs)

def cn(*classes: Any) -> str:
    result_classes: list[str] = []

    for cls in classes:
        if not cls:
            continue

        if isinstance(cls, str):
            result_classes.append(cls)
        elif isinstance(cls, dict):
            for class_name, condition in cls.items():
                if condition:
                    result_classes.append(str(class_name))
        elif isinstance(cls, list | tuple):
            result_classes.append(cn(*cls))
        else:
            result_classes.append(str(cls))

    return " ".join(result_classes)


def cva(base: str = "", config: dict[str, Any] | None = None) -> Callable[..., str]:
    if config is None:
        config = {}

    variants = config.get("variants", {})
    compound_variants = config.get("compoundVariants", [])
    default_variants = config.get("defaultVariants", {})

    def variant_function(**props: Any) -> str:
        classes = [base] if base else []

        # Merge defaults with props
        final_props = {**default_variants, **props}

        # Apply variants
        for variant_key, variant_values in variants.items():
            prop_value = final_props.get(variant_key)
            if prop_value and prop_value in variant_values:
                classes.append(variant_values[prop_value])

        # Apply compound variants
        for compound in compound_variants:
            compound_class = compound.get("class", "")
            if not compound_class:
                continue

            matches = True
            for key, value in compound.items():
                if key == "class":
                    continue
                if final_props.get(key) != value:
                    matches = False
                    break

            if matches:
                classes.append(compound_class)

        return cn(*classes)

    return variant_function


def generate_component_id(component_type: str, user_id: Optional[str] = None) -> str:
    """Generate component ID following the pattern: user_id or {component_type}-{short_hash}"""
    if user_id:
        return user_id
    
    # Generate a short hash for uniqueness
    short_hash = uuid.uuid4().hex[:6]
    return f"{component_type}-{short_hash}"


def create_component_signals(
    component_id: str, 
    default_signals: Dict[str, Any],
    user_signals: Optional[Dict[str, Any]] = None,
    expose_signals: bool = False
) -> Dict[str, Any]:
    """Create component signals with proper naming and visibility control.
    
    Args:
        component_id: The component's ID
        default_signals: Default signals for this component type
        user_signals: User-provided signal overrides
        expose_signals: Whether to make private signals public
    
    Returns:
        Dict of signals ready for Datastar integration
    """
    if user_signals:
        # User provided explicit signals - use exactly as provided
        return user_signals
    
    # Generate signals based on component ID and defaults
    signals = {}
    for signal_name, default_value in default_signals.items():
        # Check if signal should be private (starts with underscore in template)
        if signal_name.startswith('_') and not expose_signals:
            # Keep private by prefixing with underscore
            final_name = f"_{component_id}{signal_name}"
        else:
            # Make public by removing leading underscore if present
            base_name = signal_name.lstrip('_')
            final_name = f"{component_id}_{base_name}"
        
        signals[final_name] = default_value
    
    return signals
