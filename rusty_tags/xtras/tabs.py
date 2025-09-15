from itertools import count
from typing import Any, Optional, Union
import rusty_tags as rt
from .utils import cn
from rusty_tags.datastar import Signals

_tab_ids = count(1)


def Tabs(
    *children,
    default_tab: str,
    signal: Optional[str] = None,
    cls: str = "",
    **attrs: Any
) -> rt.HtmlString:
    """
    Tabs anatomical pattern component using function closures for clean composition.
    
    This component handles complex coordination between:
    - Tab triggers with proper ARIA attributes  
    - Tab content panels with associations
    - State management via Datastar signals
    - Accessibility and keyboard navigation
    
    Args:
        *children: TabsList and TabsContent function components
        default_tab: ID of initially active tab
        signal: Signal name for tab state (auto-generated if not provided)
        cls: CSS classes for root container
        **attrs: Additional HTML attributes
        
    Returns:
        Complete tabs structure with proper coordination
        
    Example:
        Tabs(
            TabsList(
                TabsTrigger("Tab 1", id="tab1"),
                TabsTrigger("Tab 2", id="tab2"),
            ),
            TabsContent(P("Content 1"), id="tab1"),
            TabsContent(P("Content 2"), id="tab2"),
            default_tab="tab1"
        )
    """
    if not signal:
        signal = f"tabs_{next(_tab_ids)}"
    
    # Process children by calling them with the signal context
    processed_children = [
        child(signal, default_tab) if callable(child) else child
        for child in children
    ]
    
    return rt.Div(
        *processed_children,
        signals=Signals(**{signal: default_tab}),
        cls=cn("tabs-container", cls),
        **attrs
    )


def TabsList(
    *children,
    cls: str = "",
    **attrs: Any
):
    """
    Container for tab trigger buttons with proper tablist role.
    
    Args:
        *children: TabsTrigger components
        cls: CSS classes for the tab list
        **attrs: Additional HTML attributes
    """
    def create_list(signal: str, default_tab: str):
        # Process child triggers with signal context
        processed_children = [
            child(signal, default_tab) if callable(child) else child
            for child in children
        ]
        
        return rt.Div(
            *processed_children,
            role="tablist",
            cls=cn("tabs-list", cls),
            **attrs
        )
    
    return create_list


def TabsTrigger(
    *children,
    id: str,
    disabled: bool = False,
    cls: str = "",
    **attrs: Any
):
    """
    Individual tab trigger button with proper ARIA attributes.
    
    Args:
        *children: Button content (text, icons, etc.)
        id: Unique tab identifier
        disabled: Whether the tab is disabled
        cls: CSS classes for the trigger
        **attrs: Additional HTML attributes
    """
    def create_trigger(signal: str, default_tab: str):
        is_active = default_tab == id
        
        return rt.Button(
            *children,
            id=id,
            type="button",
            role="tab",
            disabled=disabled,
            on_click=f"${signal} = '{id}'",
            **{
                "aria-selected": "true" if is_active else f"${signal} === '{id}'",
                "aria-controls": f"panel-{id}",
                "tabindex": "0" if is_active else "-1",
                "data-attr-aria-selected": f"${signal} === '{id}'",
                "data-attr-tabindex": f"${signal} === '{id}' ? '0' : '-1'",
            },
            cls=cn("tabs-trigger", cls),
            **attrs
        )
    
    return create_trigger


def TabsContent(
    *children,
    id: str,
    cls: str = "",
    **attrs: Any
):
    """
    Tab content panel that shows/hides based on active tab.
    
    Args:
        *children: Panel content
        id: Tab identifier (matches TabsTrigger id)
        cls: CSS classes for the content panel
        **attrs: Additional HTML attributes
    """
    def create_content(signal: str, default_tab: str):
        return rt.Div(
            *children,
            id=f"panel-{id}",
            role="tabpanel",
            tabindex="0",
            show=f"${signal} === '{id}'",
            **{
                "aria-labelledby": id,
            },
            cls=cn("tabs-content", cls),
            **attrs
        )
    
    return create_content
