from typing import Optional, Callable, ParamSpec, TypeVar
from functools import partial, wraps
from .rusty_tags import Html, Head, Title, Body, HtmlString, Script, CustomTag, Link

P = ParamSpec("P")
R = TypeVar("R")

fragment = CustomTag("Fragment")

HEADER_URLS = {        
        'highlight_js': "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js",
        'highlight_python': "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/python.min.js",
        'highlight_light_css': "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-light.css",
        'highlight_dark_css': "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.css",
        'highlight_copy': "https://cdn.jsdelivr.net/gh/arronhunt/highlightjs-copy/dist/highlightjs-copy.min.js",
        'highlight_copy_css': "https://cdn.jsdelivr.net/gh/arronhunt/highlightjs-copy/dist/highlightjs-copy.min.css",
}


def Page(*content, 
         title: str = "RustyTags", 
         hdrs:tuple=None,
         ftrs:tuple=None, 
         htmlkw:dict=None, 
         bodykw:dict=None,
         datastar:bool=True,
         lucide:bool=False,
         highlightjs:bool=False
    ) -> HtmlString:
    """Base page layout with common HTML structure."""
    # initialize empty tuple if None
    hdrs = hdrs if hdrs is not None else ()
    ftrs = ftrs if ftrs is not None else ()
    htmlkw = htmlkw if htmlkw is not None else {}
    bodykw = bodykw if bodykw is not None else {}

    if highlightjs:
            hdrs += (   # pyright: ignore[reportOperatorIssue]
                Script(src=HEADER_URLS['highlight_js']),
                Script(src=HEADER_URLS['highlight_python']),
                Link(rel="stylesheet", href=HEADER_URLS['highlight_light_css'], id='hljs-light'),
                Link(rel="stylesheet", href=HEADER_URLS['highlight_dark_css'], id='hljs-dark'),
                Script(src=HEADER_URLS['highlight_copy']),
                Link(rel="stylesheet", href=HEADER_URLS['highlight_copy_css']),
                Script('''
                    hljs.addPlugin(new CopyButtonPlugin());
                    hljs.configure({
                        cssSelector: 'pre code',
                        languages: ['python'],
                        ignoreUnescapedHTML: true
                    });
                    function updateTheme() {
                        const isDark = document.documentElement.classList.contains('dark');
                        document.getElementById('hljs-dark').disabled = !isDark;
                        document.getElementById('hljs-light').disabled = isDark;
                    }
                    new MutationObserver(mutations =>
                        mutations.forEach(m => m.target.tagName === 'HTML' &&
                            m.attributeName === 'class' && updateTheme())
                    ).observe(document.documentElement, { attributes: true });
                    updateTheme();
                    hljs.highlightAll();
                ''', type='module'),
            )
            ftrs += (Script("hljs.highlightAll();"),) 
    if lucide:
        hdrs += (Script(src="https://unpkg.com/lucide@latest"),)
        ftrs += (Script("lucide.createIcons();"),)

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
                    datastar:bool=True,
                    lucide:bool=True,
                    highlightjs:bool=False
                    ):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    page_func = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw, datastar=datastar, lucide=lucide, highlightjs=highlightjs)
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
    lucide:bool=False,
    highlightjs:bool=False
):
    """Create a decorator that wraps content in a Page layout.
    
    Returns a decorator function that can be used to wrap view functions.
    The decorator will take the function's output and wrap it in the Page layout.
    """
    template = partial(Page, hdrs=hdrs, ftrs=ftrs, htmlkw=htmlkw, bodykw=bodykw, title=page_title, datastar=datastar, lucide=lucide)
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