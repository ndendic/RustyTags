from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from datastar_py.fastapi import  ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any
from rusty_tags.components.inputs import Input
from rusty_tags.components.sidebar import Sidebar
from rusty_tags import Input as HTMLInput
from fastapi.staticfiles import StaticFiles
from rusty_tags.components.sheet import Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter

hdrs = (Link(rel='stylesheet', href='/static/css/main.css'), Script(src="/static/js/datastar-inspector.js", type="module"))
htmlkws = dict(lang="en")
bodykws = dict(cls="page",data_class= "{dark: $dark, light: !$dark}", signals=Signals(message="", conn=""))

ftrs=(
    CustomTag("datastar-inspector"),
)
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, ftrs=ftrs)

app = FastAPI()
app.mount("/static", StaticFiles(directory="lab/static"), name="static")

def Section(title, *content, **kwargs):
    return Div(
        H3(title),
        Div(
            *content,
        ),
        **kwargs
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
    sds = ['left', 'right', 'top', 'bottom']
    return Main(
        Section("Server event updates demo 🙂",
            Form(
                Input(label="Message", placeholder="Something...", 
                      supporting_text="Send server some message and press Enter", 
                      type="text", bind="message"),
                on_submit=DS.get(f"/cmds/message.send/{uuid4().hex}/")
                # on_submit="@post('/cmds/commands/user.global', {contentType: 'form'})"
            ),
            Div(id="updates"),
            Div(
                *[SheetTrigger(f"Open {sd} Sheet", signal=f"sheet_{sd}", cls="button outlined") for sd in sds],
            ),
            *[Sheet(
                SheetContent(
                    SheetHeader(
                        SheetTitle("Sheet Title", signal="sheet_right"),
                        SheetDescription("This is a sheet description.", signal="sheet_right"),
                    ),
                    Div(
                        P("Sheet content goes here. Press ESC or click outside to close."),
                        Input(label="Type something...", placeholder="Type something..."),
                        style="padding: var(--size-6);",
                    ),
                    SheetFooter(
                        Button("Cancel", on_click="$sheet_right_open = false", variant="outline", cls="button outlined"),
                        Button("Save Changes", cls="button filled"),
                    ),
                    signal=f"sheet_{sd}",
                    side=sd,  # pyright: ignore[reportArgumentType]
                    size="md",
                ),
                signal=f"sheet_{sd}",
                side=sd,
                size="md",
                modal=True,
            ) for sd in sds],
        ),
        cls="container",
        signals=Signals(message=""),
        on_load=DS.get("/updates")
    )

@app.get("/playground")
@page(title="Playground 🎉", wrap_in=HTMLResponse)
def playground():
    return Div(
        
        Main(
            # Open Props + Datastar playground examples
            Section("Sidebar demo",
                Div(
                    Button("Toggle sidebar", cls="button outlined", on_click="$sidebarOpen = !$sidebarOpen"),
                    style="display:flex; gap: var(--size-3); align-items:center;"
                ),
                # Sidebar root with internal signals; overlay auto on small screens
                Sidebar(
                    {"label": "Home", "href": "#"},
                    {"label": "Projects", "children": [
                        {"label": "Alpha", "href": "#"},
                        {"label": "Beta", "href": "#"}
                    ]},
                    {"label": "Settings", "href": "#"},
                    title="Demo Sidebar",
                    side="left",
                    mode="push",
                    overlay="never",
                    signal="demoSidebar",
                    default_open=True,
                    controlled=True,
                    control_var="sidebarOpen"
                ),
                signals=Signals(sidebarOpen=True),
            ),
            # main content placeholder to demonstrate push
            Div(
                P("Main content goes here. In push mode, this area shifts when the sidebar opens."),
                cls="main",
                style="padding: var(--size-6);"
            ),
            Section("Open Props tokens and spacing",
                Div(
                    Div(
                        Div(
                            cls="circle",
                            style="inline-size: var(--size-6); block-size: var(--size-6); background: var(--gradient-9); border-radius: var(--radius-round);"
                        ),
                        Div(
                            cls="circle",
                            style="inline-size: var(--size-8); block-size: var(--size-8); background: var(--gradient-12); border-radius: var(--radius-round);"
                        ),
                        Div(
                            cls="circle",
                            style="inline-size: var(--size-10); block-size: var(--size-10); background: var(--gradient-16); border-radius: var(--radius-round);"
                        ),
                        style="display: grid; grid-auto-flow: column; gap: var(--size-4); align-items: end;"
                    ),
                    P("Sizes come from Open Props, using variables like ", Code("--size-*"), "."),
                ),
            ),

            Section("Buttons (Open Props UI variants)",
                Div(
                    Button("Filled", cls="button filled"),
                    Button("Tonal", cls="button tonal"),
                    Button("Outlined", cls="button outlined"),
                    Button("Elevated", cls="button elevated"),
                    style="display: flex; gap: var(--size-2); flex-wrap: wrap;"
                ),
                Div(
                    Div(
                        Button("Red", cls="button filled"),
                        Button("Red outlined", cls="button outlined"),
                        cls="red",
                        style="display: flex; gap: var(--size-2); flex-wrap: wrap;"
                    ),
                    Div(
                        Button("Blue", cls="button filled"),
                        Button("Blue outlined", cls="button outlined"),
                        cls="blue",
                        style="display: flex; gap: var(--size-2); flex-wrap: wrap; margin-block-start: var(--size-2);"
                    ),
                ),
            ),

            Section("Card (outlined/elevated)",
                Div(
                    CustomTag('hgroup',
                        P("Overline"),
                        H3("Card title"),
                        P("Short supporting text for the card header"),
                    ),
                    Div(
                        P("This card is styled with Open Props UI tokens for borders, radius, and shadows."),
                        cls="content"
                    ),
                    Div(
                        Button("Primary", cls="button filled"),
                        Button("Secondary", cls="button outlined"),
                        cls="actions"
                    ),
                    cls="card outlined"
                ),
            ),

            Section("data-style dynamic styling (Datastar)",
                Div(
                    Div(
                        Button(
                            "Toggle rounded",
                            cls="button filled",
                            on_click='$rounded = !$rounded',
                            data_style="{borderRadius: $rounded ? $rds[$intensity - 1] : 'var(--radius-1)'}"
                        ),
                        HTMLInput(type='range', min='1', max='5', value='3',
                            bind='intensity'
                        ),
                        style="display:flex; gap: var(--size-3); align-items: center;"
                    ),
                    style="display: grid; gap: var(--size-4);",
                    signals=Signals(rds=[f"var(--radius-{i})" for i in range(1, 6)]),
                ),
            ),

            Section("Light / Dark theme switch (scoped)",
                Div(
                    Button(
                        "Toggle theme",
                        cls="button outlined",
                        on_click='$dark = !$dark'
                    ),
                    Div(
                        Div(
                            H4("Scoped Theme Box"),
                            P("This box flips between .light and .dark using Datastar classes."),
                            style="padding: var(--size-5); border-radius: var(--radius-3); box-shadow: var(--shadow-3); background: var(--surface-default);"
                        ),                    
                        style="display: block; border-radius: var(--radius-3);"
                    ),
                    style="display: grid; gap: var(--size-3);"
                ),
            ),

            cls="container main",
            signals=Signals(message="", rounded=False, intensity=3, dark=False),
            # on_load=DS.get("/updates")
        ),
        
    )

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
    # yield Notification(f"Server notification: {message}")




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




