from typing import Optional, Callable, ParamSpec, TypeVar, Any
from functools import partial, wraps
from .rusty_tags import Html, Head, Title, Body, HtmlString, Script, CustomTag, I

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

def Icon(icon: str, **attrs) -> HtmlString:
    """Iconify icon element. Usage: Icon("home", cls="h-4 w-4")"""
    return I(Script("lucide.createIcons();"),data_lucide=icon, **attrs)

def cn(*classes: Any) -> str:
    result_classes: list[str] = []

    for cls in classes:
        if not cls:
            continue

        if isinstance(cls, str):
            result_classes.append(cls)
        elif isinstance(cls, dict):
            for class_name, condition in cls.items():
                if condition:
                    result_classes.append(str(class_name))
        elif isinstance(cls, list | tuple):
            result_classes.append(cn(*cls))
        else:
            result_classes.append(str(cls))

    return " ".join(result_classes)


def cva(base: str = "", config: dict[str, Any] | None = None) -> Callable[..., str]:
    if config is None:
        config = {}

    variants = config.get("variants", {})
    compound_variants = config.get("compoundVariants", [])
    default_variants = config.get("defaultVariants", {})

    def variant_function(**props: Any) -> str:
        classes = [base] if base else []

        # Merge defaults with props
        final_props = {**default_variants, **props}

        # Apply variants
        for variant_key, variant_values in variants.items():
            prop_value = final_props.get(variant_key)
            if prop_value and prop_value in variant_values:
                classes.append(variant_values[prop_value])

        # Apply compound variants
        for compound in compound_variants:
            compound_class = compound.get("class", "")
            if not compound_class:
                continue

            matches = True
            for key, value in compound.items():
                if key == "class":
                    continue
                if final_props.get(key) != value:
                    matches = False
                    break

            if matches:
                classes.append(compound_class)

        return cn(*classes)

    return variant_function
