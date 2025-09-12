import rusty_tags as rt
from typing import List, Dict, Optional, Union
from ..datastar import DS, signals

def SidebarItem(
        label: str, 
        href: Optional[str] = None,
        icon: Optional[str] = None,
        children: Optional[List[Dict]] = None
    ):
    """
    Single sidebar navigation item with optional nested children.
    
    Args:
        label: The display text for the item
        href: Optional URL for navigation
        icon: Optional icon identifier
        children: Optional list of child items for nested navigation
    """
    # Create the main item content
    item_content = []
    
    # Add icon if provided
    if icon:
        item_content.append(
            rt.Span(icon, cls="start")
        )
    
    # Add main text content
    item_content.append(
        rt.Span(label, cls="text")
    )
    
    # Add expand/collapse indicator for items with children
    if children:
        item_content.append(
            rt.Span(
                "▶", 
                cls="end",
                # style="{transition: transform 0.2s ease; transform: rotate(0deg)}",
                data_expanded="false"                
            )
        )
    
    # Determine the wrapper element
    if href and not children:
        # Simple link item
        item_wrapper = rt.A(*item_content, href=href, cls="sidebar-item")
    elif children:
        # Collapsible item
        item_wrapper = rt.Button(
            *item_content,
            cls="sidebar-item collapsible",
            on_click=DS.chain(
                "$toggleExpanded(this)",
                "this.setAttribute('data-expanded', !JSON.parse(this.getAttribute('data-expanded') || 'false'))",
                "this.querySelector('.end').style.transform = JSON.parse(this.getAttribute('data-expanded')) ? 'rotate(90deg)' : 'rotate(0deg)'"
            ),
            **{"data-expanded": "false"}
        )
    else:
        # Simple item without navigation
        item_wrapper = rt.Div(*item_content, cls="sidebar-item")
    
    # Create the complete list item
    list_item = rt.Li(item_wrapper)
    
    # Add nested children if present
    if children:
        nested_items = []
        for child in children:
            nested_items.append(
                SidebarItem(
                    label=child.get("label", ""),
                    href=child.get("href"),
                    icon=child.get("icon")
                )
            )
        
        nested_list = rt.Ul(
            *nested_items,
            cls="list nested",
            show="$isExpanded(this.parentElement)",
            style="display: none; padding-left: var(--size-4);"
        )
        
        list_item = rt.Li(item_wrapper, nested_list)
    
    return list_item


def Sidebar(
        *items,
        title: Optional[str] = None,
        collapsed: bool = False,
        **kwargs
    ):
    """
    Interactive sidebar component with collapsible sections and Datastar integration.
    
    Args:
        *items: SidebarItem components or navigation data
        title: Optional sidebar title
        collapsed: Whether sidebar starts collapsed
    """
    
    sidebar_content = []
    
    # Add title if provided
    if title:
        sidebar_content.append(
            rt.Header(
                rt.H3(title, cls="sidebar-title"),
                cls="sidebar-header"
            )
        )
    
    # Create navigation list
    nav_items = []
    for item in items:
        if isinstance(item, dict):
            # Convert dict to SidebarItem
            nav_items.append(
                SidebarItem(
                    label=item.get("label", ""),
                    href=item.get("href"),
                    icon=item.get("icon"),
                    children=item.get("children")
                )
            )
        else:
            # Already a component
            nav_items.append(item)
    
    sidebar_content.append(
        rt.Nav(
            rt.Ul(*nav_items, cls="list sidebar-nav"),
            role="navigation"
        )
    )
    
    # Create the complete sidebar
    return rt.Aside(
        *sidebar_content,
        cls="sidebar",
        signals=signals(collapsed=collapsed, expandedItems={}),
        style="width: 60px; transition: width 0.3s ease",
        **{
            "data-style": "{width: $collapsed ? '60px' : '280px'}",
            "data-class-collapsed": "$collapsed"
        },
        **kwargs
    )


def SidebarToggle(button_class: str = "sidebar-toggle", **kwargs):
    """
    Toggle button for sidebar collapse/expand.
    
    Args:
        button_class: CSS class for styling (default: "sidebar-toggle")
    """
    return rt.Button(
        "☰",
        cls=button_class,
        on_click=DS.set("collapsed", "!$collapsed"),
        title="Toggle sidebar",
        **kwargs
    )


# Utility function for creating navigation data
def create_nav_item(label: str, href: str|None = None, icon: str|None = None, children: List[Dict]|None = None):
    """Helper function to create navigation item dictionaries."""
    return {
        "label": label,
        "href": href,
        "icon": icon,
        "children": children
    }