from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template
from rusty_tags.datastar import DS, Signals
from rusty_tags.events import on, emit_async, event, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from datastar_py.fastapi import datastar_response, ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any
from .components.tabs import tabs
from .components.sidebar import sidebar, navbar
hdrs = (
    # Basecoat CSS
    Script(src='https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4'),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/basecoat-css@0.3.2/dist/basecoat.cdn.min.css'),
    Script(src='https://cdn.jsdelivr.net/npm/basecoat-css@0.3.2/dist/js/all.min.js', defer=''),
    Script("(() => {\r\n    try {\r\n      const stored = localStorage.getItem('themeMode');\r\n      if (stored ? stored === 'dark'\r\n                  : matchMedia('(prefers-color-scheme: dark)').matches) {\r\n        document.documentElement.classList.add('dark');\r\n      }\r\n    } catch (_) {}\r\n\r\n    const apply = dark => {\r\n      document.documentElement.classList.toggle('dark', dark);\r\n      try { localStorage.setItem('themeMode', dark ? 'dark' : 'light'); } catch (_) {}\r\n    };\r\n\r\n    document.addEventListener('basecoat:theme', (event) => {\r\n      const mode = event.detail?.mode;\r\n      apply(mode === 'dark' ? true\r\n            : mode === 'light' ? false\r\n            : !document.documentElement.classList.contains('dark'));\r\n    });\r\n  })();"),
    # Franken UI
    # Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/core.min.css'),
    # Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/utilities.min.css'),
    # Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/core.iife.js', type='module'),
    # Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/icon.iife.js', type='module'),
    # Script('const htmlElement = document.documentElement;\r\n\r\n  const __FRANKEN__ = JSON.parse(\r\n    localStorage.getItem("__FRANKEN__") || "{}",\r\n  );\r\n\r\n  if (\r\n    __FRANKEN__.mode === "dark" ||\r\n    (!__FRANKEN__.mode &&\r\n      window.matchMedia("(prefers-color-scheme: dark)").matches)\r\n  ) {\r\n    htmlElement.classList.add("dark");\r\n  } else {\r\n    htmlElement.classList.remove("dark");\r\n  }\r\n\r\n  htmlElement.classList.add(__FRANKEN__.theme || "uk-theme-yellow");\r\n  htmlElement.classList.add(__FRANKEN__.radii || "uk-radii-md");\r\n  htmlElement.classList.add(__FRANKEN__.shadows || "uk-shadows-sm");\r\n  htmlElement.classList.add(__FRANKEN__.font || "uk-font-sm");\r\n  htmlElement.classList.add(__FRANKEN__.chart || "uk-chart-default");')
)
htmlkws = dict(cls="bg-background text-foreground font-sans antialiased")
bodykws = dict(cls="h-screen text-foreground font-sans antialiased", signals=Signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)

app = FastAPI()

def Section(title, *content):
    return Div(
        H2(title, cls="text-4xl font-extrabold tracking-tight text-balance mb-4 text-primary"),
        Div(
            *content,
            cls=" border rounded-md p-4"
        ),  
        cls="my-4 max-w-md"
    )

def Notification(message, topic: str | list[str] = "updates", sender: str | Any = ANY):
    element = Div(
        Span(
            CustomTag('uk-icon', icon='rocket'),
            cls='flex-none mr-2'
        ),
        message,
        cls='flex items-center text-primary'
    )
    return execute_script(f"UIkit.notification({{message: '{element}', pos: 'top-right'}})", 
                          topic=topic, sender=sender)

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Div(sidebar,Main(
        navbar,
        Div(
            Section("Server event updates demo 🙂",
                Form(
                    Input(placeholder="Send server some message and press Enter", 
                        type="text", bind="message", cls="uk-input"),
                    on_submit=DS.get(f"/cmds/message.send/{uuid4().hex}/")
                    # on_submit="@post('/cmds/commands/user.global', {contentType: 'form'})"
                ),
                Div(id="updates")
            ),
            tabs,
            cls="p-4 md:p-6 xl:p-12",
            id="content"
        ),
        signals=Signals(message=""),
        on_load=DS.get("/updates")
    ))

@app.get("/cmds/{command}/{sender}")
@datastar_response
async def commands(command: str, sender: str, request: Request, signals: ReadSignals):
    """Trigger events and broadcast to all connected clients"""
    signals = Signals(signals) if signals else {}
    backend_signal = event(command)
    await emit_async(backend_signal, sender, signals=signals, request=request)

@app.get("/updates")
@datastar_response
async def event_stream(request: Request, signals: ReadSignals):
    """SSE endpoint with automatic client management"""
    with Client(topics=["updates"]) as client:
        async for update in client.stream():
            yield update
    
@on("message.send")
async def notify(sender, request: Request, signals: Signals):
    message = signals.message or "No message provided" 
    yield sse_elements(Div(f"Server processed message: {message}", cls="text-lg text-bold mt-4 mt-2"),
                             selector="#updates", mode=ElementPatchMode.APPEND, topic="updates")
    yield sse_signals({"message": ""}, topic="updates")
    yield Notification(f"Server notification: {message}")




# @on(command, sender="user.global")
# def log(sender, request: Request, signals: dict | None):
#     message = (signals or {}).get("message", "No message provided")
#     print(f"Logging via 'log' handler: {message}")
#     return Notification(f"Logging via log handler: {message}")

# @on(command, sender="user.global")
# async def log_event(sender, request: Request, signals: dict | None):
#     message = (signals or {}).get("message", "No message provided")
#     print(f"Logging via 'log_event' handler: {message}")
#     return Notification(f"Logging via 'log_event' handler: {message}")




