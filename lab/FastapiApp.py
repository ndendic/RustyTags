from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template, AttrDict
from rusty_tags.datastar import DS, signals
from rusty_tags.backend import on_event, broadcast, Client, event
from datastar_py.fastapi import datastar_response, ReadSignals, ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

hdrs = (
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/core.min.css'),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/utilities.min.css'),
    Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/core.iife.js', type='module'),
    Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/icon.iife.js', type='module'),
    Script('const htmlElement = document.documentElement;\r\n\r\n  const __FRANKEN__ = JSON.parse(\r\n    localStorage.getItem("__FRANKEN__") || "{}",\r\n  );\r\n\r\n  if (\r\n    __FRANKEN__.mode === "dark" ||\r\n    (!__FRANKEN__.mode &&\r\n      window.matchMedia("(prefers-color-scheme: dark)").matches)\r\n  ) {\r\n    htmlElement.classList.add("dark");\r\n  } else {\r\n    htmlElement.classList.remove("dark");\r\n  }\r\n\r\n  htmlElement.classList.add(__FRANKEN__.theme || "uk-theme-yellow");\r\n  htmlElement.classList.add(__FRANKEN__.radii || "uk-radii-md");\r\n  htmlElement.classList.add(__FRANKEN__.shadows || "uk-shadows-sm");\r\n  htmlElement.classList.add(__FRANKEN__.font || "uk-font-sm");\r\n  htmlElement.classList.add(__FRANKEN__.chart || "uk-chart-default");')
)
htmlkws = dict(cls="bg-background text-foreground font-sans antialiased")
bodykws = dict(cls="h-screen p-16 bg-white text-foreground font-sans antialiased", signals=signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)

app = FastAPI()

def Section(title, *content):
    return Div(
        H2(title, cls="uk-h2 mb-4 text-primary"),
        Div(
            *content,
            cls=" border rounded-md p-4"
        ),  
        cls="my-4 max-w-md"
    )
def Notification(message):
    element = Div(
        Span(
            CustomTag('uk-icon', icon='rocket'),
            cls='flex-none mr-2'
        ),
        message,
        cls='flex items-center text-primary'
    )
    return SSE.execute_script(f"UIkit.notification({{message: '{element}', pos: 'top-right'}})")

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
        Section("Server event updates demo 🙂", 
            Form(
                Input(placeholder="Send server some message and press Enter", type="text", bind="message", cls="uk-input"),
                on_submit=DS.get("/cmds/commands/user.global")
                # on_submit="@post('/cmds/commands/user.global', {contentType: 'form'})"
            ),
            Div(id="updates")
        ),
        signals=signals(message=""),
        on_load=DS.get("/updates")
    )

@app.get("/cmds/{command}/{sender}")
@datastar_response
async def commands(command: str, sender: str, request: Request, signals: ReadSignals):
    """Trigger events and broadcast to all connected clients"""
    signals = AttrDict(signals) if signals else AttrDict()
    backend_signal = event(command)
    broadcast(backend_signal, sender, signals=signals, request=request)
    return Notification(f"Server processed message from {sender}")

@app.get("/updates")
@datastar_response
async def event_stream(request: Request, signals: ReadSignals):
    """SSE endpoint with automatic client management"""
    with Client() as client:
        async for update in client.stream():
            yield update
    

@on_event("commands", sender="user")
def notify(sender, request: Request, signals: AttrDict | None):
    message = signals.message or "No message provided" 
    yield Notification(f"Server processed message: {message}")
    yield SSE.patch_elements(Div(f"Server processed message: {message}", cls="text-lg text-bold mt-4 mt-2"),
                             selector="#updates", mode=ElementPatchMode.APPEND)
    yield SSE.patch_signals({"message": ""})

command = event("commands")

@command.connect
def log(sender, request: Request, signals: dict | None):
    message = (signals or {}).get("message", "No message provided")
    print(f"Logging via 'log' handler: {message}")

@on_event(command, sender="user")
async def log_event(sender, request: Request, signals: dict | None):
    message = (signals or {}).get("message", "No message provided")
    return print(f"Logging via 'log_event' handler: {message}")




