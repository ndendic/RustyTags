from typing import Optional
from functools import partial
from rusty_tags import *


def Page(*content, title: str = "StarModel", hdrs:Optional[tuple]=None,ftrs:Optional[tuple]=None, htmlkw:Optional[dict]=None, bodykw:Optional[dict]=None) -> HtmlString:
    """Base page layout with common HTML structure."""
    
    return Html(
        Head(
            Title(title),
            *hdrs if hdrs else (),
        ),
        Body(
            *content,                
            *ftrs if ftrs else (),
            **bodykw if bodykw else {},
        ),
        **htmlkw if htmlkw else {},
    )

def create_page_decorator(page_title: str = "MyPage", hdrs:Optional[tuple]=None,ftrs:Optional[tuple]=None, htmlkw:Optional[dict]=None, bodykw:Optional[dict]=None):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    page_func = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw)
    def page(fn=None, *,title: str|None = None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                return page_func(func(*args, **kwargs), title=title if title else page_title)
            return wrapper
        if fn is None:
            return decorator
        else:
            return decorator(fn)
    return page

def page_template(page_title: str = "MyPage", hdrs:Optional[tuple]=None,ftrs:Optional[tuple]=None, htmlkw:Optional[dict]=None, bodykw:Optional[dict]=None):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    template = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw)
    return template


def show(html: HtmlString):
    try:
        from IPython.display import HTML
        return HTML(html.render())
    except ImportError:
        raise ImportError("IPython is not installed. Please install IPython to use this function.")