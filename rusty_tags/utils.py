from .core import CustomTag, Html, Head, Title, Body, HtmlString, Script
from functools import partial, wraps
from typing import Optional, Callable, TypeVar, ParamSpec
from asyncio import iscoroutinefunction

P = ParamSpec("P")
R = TypeVar("R")

fragment = CustomTag("Fragment")

def template(func):
    func_is_async = iscoroutinefunction(func)
    
    def make_wrapper(inner, *args, **kwargs):
        inner_is_async = iscoroutinefunction(inner)
        
        if func_is_async or inner_is_async:
            @wraps(inner)
            async def wrapped(*inner_args, **inner_kwargs):
                content = await inner(*inner_args, **inner_kwargs) if inner_is_async else inner(*inner_args, **inner_kwargs)
                return await func(content, *args, **kwargs) if func_is_async else func(content, *args, **kwargs)
            return wrapped
        else:
            @wraps(inner)
            def wrapped(*inner_args, **inner_kwargs):
                content = inner(*inner_args, **inner_kwargs)
                return func(content, *args, **kwargs)
            return wrapped
    
    @wraps(func)
    def decorator(*args, **kwargs):
        if not args:
            return lambda inner: make_wrapper(inner, **kwargs)
        
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return make_wrapper(args[0])
        
        return func(*args, **kwargs)
    
    return decorator

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

    @template
    def page(
        *content,
        title: str | None = None,
        wrap_in: Callable | None = None,
    ):
        result = Page(
            *content,
            title=title if title else page_title,
            hdrs=hdrs,
            ftrs=ftrs,
            htmlkw=htmlkw,
            bodykw=bodykw,
            datastar=datastar,
        )
        if wrap_in:
            return wrap_in(result)
        return result

    return page

# legacy function for backwards compatibility
create_template = page_template

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