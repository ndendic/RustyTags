from .core import CustomTag, Html, Head, Title, Body, HtmlString, Script
from functools import partial
from typing import Optional, Callable, TypeVar, ParamSpec
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

fragment = CustomTag("Fragment")

def Page(*content,
         title: str = "RustyTags",
         hdrs:tuple|None=None,
         ftrs:tuple|None=None,
         htmlkw:dict|None=None,
         bodykw:dict|None=None,
         datastar: bool = True,
         ds_version: str = "1.0.0-RC.6",
    ) -> HtmlString:
    """Simple page layout with basic HTML structure."""
    hdrs = hdrs if hdrs is not None else ()
    ftrs = ftrs if ftrs is not None else ()
    htmlkw = htmlkw if htmlkw is not None else {}
    bodykw = bodykw if bodykw is not None else {}

    return Html(
        Head(
            Title(title),
            *hdrs,
            Script(src=f"https://cdn.jsdelivr.net/gh/starfederation/datastar@{ds_version}/bundles/datastar.js", type="module") if datastar else fragment,
        ),
        Body(
            *content,
            *ftrs,
            **bodykw,
        ),
        **htmlkw,
    )


def create_template(page_title: str = "MyPage", 
                    hdrs:Optional[tuple]=None,
                    ftrs:Optional[tuple]=None, 
                    htmlkw:Optional[dict]=None, 
                    bodykw:Optional[dict]=None,
                    datastar:bool=True,
                    lucide:bool=True,
                    highlightjs:bool=False,
                    tailwind4:bool=False
                    ):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    page_func = partial(Page, 
                        hdrs=hdrs, 
                        ftrs=ftrs, 
                        htmlkw=htmlkw, 
                        bodykw=bodykw, 
                        datastar=datastar,
                       )
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

def page_template(
        page_title: str = "MyPage", 
        hdrs:Optional[tuple]=None,
        ftrs:Optional[tuple]=None, 
        htmlkw:Optional[dict]=None, 
        bodykw:Optional[dict]=None, 
        datastar:bool=True, 
    ):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    template = partial(Page, 
                       hdrs=hdrs, 
                       ftrs=ftrs, 
                       htmlkw=htmlkw, 
                       bodykw=bodykw, 
                       title=page_title, 
                       datastar=datastar
                      )
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


def when(condition, element):
    """Conditional rendering helper

    Args:
        condition: Boolean condition to evaluate
        element: Tag/element to return if condition is True

    Returns:
        The element if condition is True, empty Fragment otherwise
    """
    from .core import Fragment
    if condition:
        return element
    return Fragment()


def unless(condition, element):
    """Inverse conditional rendering helper

    Args:
        condition: Boolean condition to evaluate
        element: Tag/element to return if condition is False

    Returns:
        The element if condition is False, empty Fragment otherwise
    """
    from .core import Fragment
    if not condition:
        return element
    return Fragment()