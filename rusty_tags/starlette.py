import asyncio
from typing import Literal, Any, Mapping
from datastar_py.starlette import ServerSentEventGenerator as SSE
from datastar_py.sse import _HtmlProvider
from datastar_py.consts import ElementPatchMode
from blinker import ANY, signal
from .backend import send, send_async

def elements(
        elements: str | _HtmlProvider,
        selector: str,
        mode: ElementPatchMode,
        use_view_transitions: bool | None = None,
        event_id: str | None = None,
        retry_duration: int | None = None,
        topic: str | list[str] | Any = ANY,
        sender: str | Any = ANY):
    
    result = SSE.patch_elements(elements,
        selector=selector,
        mode=mode,
        # use_view_transitions=use_view_transitions,
        # event_id=event_id,
        # retry_duration=retry_duration
        )  
    if isinstance(topic, list):
        for t in topic:
            send(t, sender, result=result)
    else:
        send(topic, sender, result=result)
    return result

def remove_elements(
        selector: str, 
        event_id: str | None = None, 
        retry_duration: int | None = None,
        topic: str | list[str] | Any = ANY,
        sender: str | Any = ANY
    ):
        result = SSE.patch_elements(
            selector=selector,
            mode=ElementPatchMode.REMOVE,
            event_id=event_id,
            retry_duration=retry_duration,
        )
        if isinstance(topic, list):
            for t in topic:
                send(t, sender, result=result)
        else:
            send(topic, sender, result=result)
        return result

def signals(
        signals: dict | str,
        *,
        event_id: str | None = None,
        only_if_missing: bool | None = None,
        retry_duration: int | None = None,
        topic: str | list[str] | Any = ANY,
        sender: str | Any = ANY):
    result = SSE.patch_signals(
        signals=signals,
        event_id=event_id,
        only_if_missing=only_if_missing,
        retry_duration=retry_duration)  
    if isinstance(topic, list):
        for t in topic:
            send(t, sender, result=result)
    else:
        send(topic, sender, result=result)
    return result

def execute_script(
        script: str,
        *,
        auto_remove: bool = True,
        attributes: Mapping[str, str] | list[str] | None = None,
        event_id: str | None = None,
        retry_duration: int | None = None,
        topic: str | list[str] | Any = ANY,
        sender: str | Any = ANY):
    result = SSE.execute_script(script, 
                                auto_remove=auto_remove, 
                                attributes=attributes, 
                                event_id=event_id, 
                                retry_duration=retry_duration)
    if isinstance(topic, list):
        for t in topic:
            send(t, sender, result=result)
    else:
        send(topic, sender, result=result)
    return result

def redirect(
        location: str,
        topic: str | list[str] | Any = ANY,
        sender: str | Any = ANY):
    result = SSE.redirect(location)
    if isinstance(topic, list):
        for t in topic:
            send(t, sender, result=result)
    else:
        send(topic, sender, result=result)
    return result