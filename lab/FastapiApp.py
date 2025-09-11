from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from rusty_tags.components.sheet import Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter, SheetTrigger
from datastar_py.fastapi import  ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any
from rusty_tags.components.inputs import Input
from fastapi.staticfiles import StaticFiles

hdrs = (Link(rel='stylesheet', href='/static/css/main.css'),)
htmlkws = dict(cls="")
bodykws = dict(cls="page", signals=Signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)

app = FastAPI()
app.mount("/static", StaticFiles(directory="lab/static"), name="static")

def Section(title, *content):
    return Div(
        H2(title),
        Div(
            *content,
        ),  
    )

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
        Section("Input fields 🙂",
            Form(
                Input(label="Username", placeholder="Something...", 
                      supporting_text="Send server some message and press Enter", 
                      type="text", bind="username"),
                Input(label="Password", placeholder="Password", 
                      supporting_text="Send server some password and press Enter", 
                      type="password", bind="password"),
                Input(label="Email", placeholder="Email", 
                      supporting_text="Send server some email and press Enter", 
                      type="email", bind="email"),
                Input(label="Phone", placeholder="Phone", 
                      supporting_text="Send server some phone and press Enter", 
                      type="tel", bind="phone"),
                Input(label="Date", placeholder="Date", 
                      supporting_text="Send server some date and press Enter", 
                      type="date", bind="date"),
                Input(label="Time", placeholder="Time", 
                      supporting_text="Send server some time and press Enter", 
                      type="time", bind="time"),
                Input(label="URL", placeholder="URL", 
                      supporting_text="Send server some URL and press Enter", 
                      type="url", bind="url"),
                Input(label="Search", placeholder="Search", 
                      supporting_text="Send server some search and press Enter", 
                      type="search", bind="search"),
                Input(label="Month", placeholder="Month", 
                      supporting_text="Send server some month and press Enter", 
                      type="month", bind="month"),
                Input(label="Number", placeholder="Number", 
                      supporting_text="Send server some number and press Enter", 
                      type="number", bind="number"),
                Input(label="Week", placeholder="Week", 
                      supporting_text="Send server some week and press Enter", 
                      type="week", bind="week"),
                Input(label="Datetime", placeholder="Datetime", 
                      supporting_text="Send server some datetime and press Enter", 
                      type="datetime-local", bind="datetime"),
                on_submit=DS.get(f"/cmds/message.send/{uuid4().hex}/"),
                style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; width: 100%;",
            ),
            Div(id="updates"),
        ),
        cls="container",
        signals=Signals(message=""),
        on_load=DS.get("/updates")
    )

@app.get("/sheets")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def sheets():
    SheetSide = ["top", "right", "bottom", "left"]
    return Main(
        Div(
                    H2("Sheet (Modal Drawer)", cls="text-2xl font-semibold mb-4"),
                    Div(
                        *[SheetTrigger(f"Open {side.capitalize()} Sheet", signal=f"demo_sheet_{side}") for side in SheetSide],
                        cls="grid grid-cols-2 gap-2 items-center",
                    ), 
                    *[Sheet(
                        SheetContent(
                            SheetHeader(
                                SheetTitle("Sheet Title", signal=f"demo_sheet_{side}"),
                                SheetDescription(
                                    "This is a sheet description.", signal="demo_sheet"
                                ),
                            ),
                            Div(
                                P(
                                    "Sheet content goes here. Press ESC or click outside to close."
                                ),
                                Input("Input",placeholder="Type something..."),
                                cls="p-6 space-y-4",
                            ),
                            SheetFooter(
                                Button(
                                    "Cancel",
                                    on_click=f"$demo_sheet_{side}_open = false",
                                    variant="outline",
                                ),
                                Button("Save Changes"),
                            ),
                            signal=f"demo_sheet_{side}",
                            side=side,
                            size="md",
                        ),
                        signal=f"demo_sheet_{side}",
                        side=side,
                        size="md",
                        modal=True,
                    ) for side in SheetSide],
                    cls="container mx-auto p-8",
                    id="content",
                ),
        cls="container",
        signals=Signals(message=""),
        on_load=DS.get("/updates")
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




