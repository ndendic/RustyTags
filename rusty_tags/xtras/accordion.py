from typing import Any, Literal
from itertools import count
import rusty_tags as rt
from .utils import cn, Icon
from rusty_tags.datastar import Signals

_accordion_ids = count(1)


def Accordion(
    *children,
    type: Literal["single", "multiple"] = "single",
    signal: str = "",
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """
    Accordion anatomical pattern with expand/collapse coordination.
    
    This component handles complex coordination between:
    - Multiple accordion items with proper state management
    - Single vs multiple open item modes
    - ARIA attributes for accessibility
    - Smooth expand/collapse animations
    
    Args:
        *children: AccordionItem function components
        type: "single" (one item open) or "multiple" (multiple items open)
        signal: Signal name for accordion state (auto-generated if not provided)
        cls: CSS classes for root container
        **attrs: Additional HTML attributes
        
    Returns:
        Complete accordion structure with proper coordination
        
    Example:
        Accordion(
            AccordionItem(
                "What is this?", 
                P("This is an accordion item."),
                id="item1"
            ),
            AccordionItem(
                "How does it work?", 
                P("It uses Datastar for state management."),
                id="item2"
            ),
            type="single"
        )
    """
    if not signal:
        signal = f"accordion_{next(_accordion_ids)}"
    
    # Process children by calling them with the signal context
    processed_children = [
        child(signal, type) if callable(child) else child
        for child in children
    ]
    
    return rt.Section(
        *processed_children,
        signals=Signals(**{signal: ""}),
        data_type=type,
        data_accordion_root="",
        cls=cn("accordion-container", cls),
        **attrs
    )


def AccordionItem(
    trigger_content,
    *children,
    id: str = "",
    open: bool = False,
    cls: str = "",
    **attrs: Any
):
    """
    Individual accordion item with trigger and collapsible content.
    
    Args:
        trigger_content: Content for the accordion trigger button
        *children: Collapsible content
        id: Unique item identifier
        open: Whether item starts open (only for "multiple" type)
        cls: CSS classes for the item
        **attrs: Additional HTML attributes
    """
    def create_item(signal: str, accordion_type: str = "single"):
        item_id = id or f"accordion-item-{next(_accordion_ids)}"
        
        if accordion_type == "single":
            # Single type: use signal to track which item is open
            is_open = f"${signal} === '{item_id}'"
            toggle_action = f"${signal} === '{item_id}' ? ${signal} = '' : ${signal} = '{item_id}'"
            open_class = f"${signal} === '{item_id}'"
        else:
            # Multiple type: each item has its own open state
            item_signal = f"{signal}_{item_id}"
            is_open = f"${item_signal}"
            toggle_action = f"${item_signal} = !${item_signal}"
            open_class = f"${item_signal}"
        
        return rt.Details(
            # Trigger button
            rt.Summary(
                trigger_content,
                # Chevron icon that rotates when open
                Icon("chevron-down", cls="accordion-chevron transition-transform duration-200"),
                cls="flex flex-1 items-center justify-between gap-4 py-4 text-left text-sm font-medium cursor-pointer hover:underline",
                on_click=toggle_action
            ),
            
            # Collapsible content with grid animation
            rt.Div(
                rt.Div(
                    *children,
                    cls="accordion-content-wrapper pb-4 pt-0"
                ),
                cls=cn(
                    "grid transition-[grid-template-rows] duration-300 ease-out",
                    "accordion-initially-open" if open else ""
                ),
                **{
                    "data-attr-style": f"grid-template-rows: {{{is_open}}} ? '1fr' : '0fr'"
                }
            ),
            
            id=item_id,
            data_accordion_item="",
            **{
                "data-attr-data-state": f"{{{is_open}}} ? 'open' : 'closed'",
                "data-attr-open": is_open if accordion_type == "multiple" else None
            },
            cls=cn("group border-b last:border-b-0", cls),
            **attrs
        )
    
    return create_item


def AccordionTrigger(
    *children,
    cls: str = "",
    **attrs: Any
):
    """
    Standalone accordion trigger for more control over styling.
    Used inside AccordionItem if you need custom trigger styling.
    
    Args:
        *children: Trigger content
        cls: CSS classes for the trigger
        **attrs: Additional HTML attributes
    """
    return lambda signal, accordion_type: rt.Summary(
        *children,
        Icon("chevron-down", cls="accordion-chevron transition-transform duration-200"),
        cls=cn(
            "flex flex-1 items-center justify-between gap-4 py-4",
            "text-left text-sm font-medium cursor-pointer hover:underline",
            cls
        ),
        **attrs
    )


def AccordionContent(
    *children,
    cls: str = "",
    **attrs: Any
):
    """
    Standalone accordion content for more control over styling.
    Used inside AccordionItem if you need custom content styling.
    
    Args:
        *children: Content to be shown/hidden
        cls: CSS classes for the content wrapper
        **attrs: Additional HTML attributes
    """
    return lambda signal, accordion_type: rt.Div(
        rt.Div(
            *children,
            cls=cn("accordion-content-wrapper pb-4 pt-0", cls)
        ),
        cls="grid transition-[grid-template-rows] duration-300 ease-out",
        **attrs
    )