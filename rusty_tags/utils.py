from typing import Optional, Callable, ParamSpec, TypeVar
from functools import partial, wraps
from .rusty_tags import Html, Head, Title, Body, HtmlString, Script, CustomTag

P = ParamSpec("P")
R = TypeVar("R")

fragment = CustomTag("Fragment")

def Page(*content, 
         title: str = "StarModel", 
         hdrs:Optional[tuple]=None,
         ftrs:Optional[tuple]=None, 
         htmlkw:Optional[dict]=None, 
         bodykw:Optional[dict]=None,
         datastar:bool=True) -> HtmlString:
    """Base page layout with common HTML structure."""
    
    return Html(
        Head(
            Title(title),
            *hdrs if hdrs else (),
            Script(src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js", type="module") if datastar else fragment,
        ),
        Body(
            *content,                
            *ftrs if ftrs else (),
            **bodykw if bodykw else {},
        ),
        **htmlkw if htmlkw else {},
    )

def create_template(page_title: str = "MyPage", 
                    hdrs:Optional[tuple]=None,
                    ftrs:Optional[tuple]=None, 
                    htmlkw:Optional[dict]=None, 
                    bodykw:Optional[dict]=None,
                    datastar:bool=True):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    page_func = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw, datastar=datastar)
    def page(title: str|None = None, wrap_in: Callable|None = None):
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func) 
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                if wrap_in:
                    return wrap_in(page_func(func(*args, **kwargs), title=title if title else page_title))
                else:
                    return page_func(func(*args, **kwargs), title=title if title else page_title)
            return wrapper
        return decorator
    return page

def page_template(page_title: str = "MyPage", hdrs:Optional[tuple]=None,ftrs:Optional[tuple]=None, htmlkw:Optional[dict]=None, bodykw:Optional[dict]=None):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    template = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw, title=page_title)
    return template

def show(html: HtmlString):
    try:
        from IPython.display import HTML
        return HTML(html.render())
    except ImportError:
        raise ImportError("IPython is not installed. Please install IPython to use this function.")
    
class AttrDict(dict):
    "`dict` subclass that also provides access to keys as attrs"
    def __getattr__(self,k): return self[k] if k in self else None
    def __setattr__(self, k, v): (self.__setitem__,super().__setattr__)[k[0]=='_'](k,v)
    def __dir__(self): return super().__dir__() + list(self.keys()) # type: ignore
    def copy(self): return AttrDict(**self)