from typing import Any
from enum import Enum

import rusty_tags as rt
from .utils import cn


def CodeBlock(
    *content: str,  # Contents of Code tag (often text)
    cls: str = "",  # Classes for the outer container
    code_cls: str = "",  # Classes for the code tag
    **kwargs: Any  # Additional args for Code tag
) -> rt.HtmlString:
    """
    CodeBlock with styling - wraps content in Div > Pre > Code structure.
    
    This is our first "anatomical pattern" component that provides a common
    structure for displaying code with proper semantic HTML and styling hooks.
    
    Args:
        *content: Text content to display in the code block
        cls: CSS classes for the outer container div
        code_cls: CSS classes for the inner code element
        **kwargs: Additional HTML attributes for the code element
    
    Returns:
        Styled code block with proper semantic structure
        
    Example:
        CodeBlock("print('Hello, World!')", 
                 cls="border rounded p-4", 
                 code_cls="language-python")
    """
    return rt.Div(
        rt.Pre(
            rt.Code(*content, cls=cn(code_cls), **kwargs)
        ),
        cls=cn(cls)
    )