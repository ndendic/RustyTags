from typing import Any, Optional
import rusty_tags as rt
from .utils import cn


def Accordion(
    *children,
    name: Optional[str] = None,
    cls: str = "",
    **attrs: Any,
) -> rt.HtmlString:
    """
    Simple accordion container. When `name` is provided, only one child
    AccordionItem with that name can be open at a time (native HTML behavior).
    
    Args:
        *children: AccordionItem components or raw HTML
        name: Shared name for accordion items (enables single-open behavior)
        cls: CSS classes for root container
        **attrs: Additional HTML attributes
        
    Returns:
        Section containing accordion items
        
    Examples:
        # Multiple items can be open
        Accordion(
            AccordionItem("Question 1", P("Answer 1")),
            AccordionItem("Question 2", P("Answer 2"))
        )
        
        # Only one item can be open at a time
        Accordion(
            AccordionItem("Question 1", P("Answer 1"), name="faq"),
            AccordionItem("Question 2", P("Answer 2"), name="faq"),
            name="faq"
        )
    """
    # If accordion has a name, apply it to children that don't have one
    if name:
        processed_children = []
        for child in children:
            # If child is AccordionItem without name, add the accordion name
            if (hasattr(child, 'tag') and child.tag == 'details' and 
                'name' not in child.attrs):
                child_copy = rt.Details(*child.children, **child.attrs, name=name)
                processed_children.append(child_copy)
            else:
                processed_children.append(child)
        children = processed_children
    
    return rt.Section(
        *children,
        cls=cn("accordion", cls),
        **attrs
    )


def AccordionItem(
    trigger_content,
    *children,
    open: bool = False,
    name: Optional[str] = None,
    cls: str = "",
    hide_marker: bool = False,
    **attrs: Any
) -> rt.HtmlString:
    """
    Individual accordion item using HTML details/summary.
    
    Args:
        trigger_content: Content for the accordion trigger
        *children: Collapsible content
        open: Whether item starts open
        name: Name for grouping (only one item with same name can be open)
        cls: CSS classes for the details element
        **attrs: Additional HTML attributes
        
    Returns:
        details element with summary trigger and collapsible content
        
    Examples:
        # Standalone item
        AccordionItem("Click to expand", P("Hidden content"))
        
        # Grouped items (only one can be open)
        AccordionItem("Item 1", P("Content 1"), name="group")
        AccordionItem("Item 2", P("Content 2"), name="group")
    """
    details_attrs = {
        "cls": cn("accordion-item", cls),
        "open": open,
        **attrs
    }
    
    # Add name attribute for grouping behavior
    if name:
        details_attrs["name"] = name
    
    return rt.Details(
        rt.Summary(
            trigger_content,
            cls="accordion-trigger",
            style=f"list-style: none;" if hide_marker else ""
        ),
        rt.Div(
            *children,
            cls="accordion-content"
        ),
        **details_attrs
    )
