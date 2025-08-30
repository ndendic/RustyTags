import uuid
from rusty_tags import Div, Button
from rusty_tags.datastar import signals, DS, reactive_class

def cn(*classes: str, **kwargs: dict) -> str:
    """Merge classes, handling dicts for conditional classes."""
    merged = ' '.join(c for c in classes if c)
    for k, v in kwargs.items():
        if v:
            merged += f' {k}'
    return merged.strip()

def Tabs(*children, default_value: str = "tab1", variant: str = "default", cls: str = "", id: str|None = None, **kwargs):
    if id is None:
        id = uuid.uuid4().hex[:8]
    prefix = f"{id}_"
    active_signal = f"{prefix}active"

    tab_variants = {
        "default": "border-b",
        "underline": "border-b border-transparent hover:border-foreground",
        # Add more, e.g., "pills": "rounded-md bg-muted"
    }
    base_cls = cn("space-y-4", tab_variants.get(variant, ""), cls)

    # Compose with sub-components if children are provided, or assume flat structure
    return Div(
        *children,
        signals=signals(**{active_signal: default_value}),
        cls=base_cls,
        **kwargs  # Mapping expansion for extra attrs
    )

def TabsList(*children, cls: str = "",**kwargs):
    return Div(
        *children,
        cls=cn("flex space-x-2 border-b", cls),
        role="tablist",
        **kwargs
    )

def TabsTrigger(*children, value: str, cls: str = "", on_click=None, **kwargs):
    # Get prefix from context if needed; for simplicity, assume parent passes it or use global (but prefer scoped)
    # In practice, you can pass prefix as a kwarg from Tabs if composing
    active_signal = "active"  # Replace with prefixed in full integration
    return Button(
        *children,
        on_click=on_click or f"${active_signal} = '{value}'",  # Set active signal
        cls=cn(
            "px-4 py-2",
            # reactive_class(  # Datastar's shorthand for data-class
            #     "font-bold border-b-2 border-foreground" = f"${active_signal} == '{value}'",
            #     "text-muted-foreground" = f"${active_signal} != '{value}'"
            # ),
            cls,
        ),
        data_class=f"{{'font-bold border-b-2 border-foreground' : $active == '{value}'}}",
        role="tab",
        **kwargs
    )

def TabsContent(*children, value: str, cls: str = "", **kwargs):
    active_signal = "active"  # Prefix as above
    return Div(
        *children,
        show=f"${active_signal} == '{value}'",  # Datastar conditional visibility
        cls=cn("pt-2 border border-foreground", cls),
        role="tabpanel",
        **kwargs
    )

# Usage example:
tabs = Tabs(
    TabsList(
        TabsTrigger("Account", value="account"),
        TabsTrigger("Password", value="password")
    ),
    TabsContent("Account content here.", value="account"),
    TabsContent("Password content here.", value="password"), 
    default_value="account", variant="underline", cls="w-[400px]"
)