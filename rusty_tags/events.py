import asyncio
import inspect
import threading
from typing import Any, TypeVar, Protocol
import collections.abc as c
from blinker import ANY, NamedSignal



    

async def _aiter_sync_gen(gen):
    """Bridge a sync generator to async without blocking the event loop."""
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    DONE = object()

    def pump():
        try:
            for item in gen:
                loop.call_soon_threadsafe(q.put_nowait, item)
        finally:
            loop.call_soon_threadsafe(q.put_nowait, DONE)

    threading.Thread(target=pump, daemon=True).start()

    while True:
        item = await q.get()
        if item is DONE:
            break
        yield item

async def _aiter_results(handler, *args, **kwargs):
    """
    Call handler(*args, **kwargs) and yield zero-or-more items:
      - async generator  -> yield each item
      - coroutine        -> yield awaited value once
      - sync generator   -> yield each item (via thread bridge)
      - plain sync value -> yield once
    """
    rv = handler(*args, **kwargs)

    if inspect.isasyncgen(rv):          # async generator
        async for x in rv:
            yield x
        return

    if inspect.isawaitable(rv):         # coroutine/awaitable
        yield await rv
        return

    if inspect.isgenerator(rv):         # sync generator
        async for x in _aiter_sync_gen(rv):
            yield x
        return

    # plain sync value
    yield rv


class Event(NamedSignal):    

    def emit(self, sender: Any = ANY, *args, **kwargs):
        """Enhanced emit that handles all handler types"""
        results = []
        for receiver in self.receivers_for(sender):
            # Determine handler type and consume appropriately
            if self._is_async(receiver):
                result = self._schedule_async(receiver, sender, *args, **kwargs)
            else:
                result = self._consume_sync(receiver, sender, *args, **kwargs)
            results.append(result) if result is not None else None
        return results
    
    def _is_async(self, func):
        return asyncio.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)
    
    def _schedule_async(self, receiver, sender, *args, **kwargs):
        """Schedule async handler without blocking"""
        async def consume():
            results = []
            async for item in _aiter_results(receiver, sender, *args, **kwargs):
                if item is not None: results.append(item)
            return results
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(consume())
        except RuntimeError:
            print(f"No event loop for async handler {receiver.__name__}")
    
    def _consume_sync(self, receiver, sender, **kwargs):
        """Consume sync handler/generator immediately"""
        results = []
        result = receiver(sender, **kwargs)
        if result is not None: results.append(result)
        if inspect.isgenerator(result):
            results = []
            for item in result:
                if item is not None: results.append(item)
        return results
    
    async def emit_async(self, sender: Any = ANY, *args, **kwargs):
        """Fully async emit with parallel execution"""
        tasks_results = []
        for receiver in self.receivers_for(sender):
            async def consume():
                results = []
                async for item in _aiter_results(receiver, sender, *args, **kwargs):
                    if item is not None: results.append(item)
                return results
            
            result = asyncio.create_task(consume())
            result = await result
            tasks_results.append(result) if result is not None else None
        
        return tasks_results


class Namespace(dict[str, Event]):
    """A dict mapping names to events."""

    def event(self, name: str, doc: str | None = None) -> Event:
        """Return the :class:`Event` for the given ``name``, creating it
        if required. Repeated calls with the same name return the same event.

        :param name: The name of the event.
        :param doc: The docstring of the event.
        """
        if name not in self:
            self[name] = Event(name, doc)

        return self[name]


class _PNamespaceEvent(Protocol):
    def __call__(self, name: str, doc: str | None = None) -> Event: ...


default_namespace: Namespace = Namespace()
"""A default :class:`Namespace` for creating named signals. :func:`signal`
creates a :class:`Event` in this namespace.
overides the blinker default_namespace.
"""

event: _PNamespaceEvent = default_namespace.event
"""Return a :class:`Event` in :data:`default_namespace` with the given
``name``, creating it if required. Repeated calls with the same name return the
same signal.
"""

F = TypeVar("F", bound=c.Callable[..., Any])

def on(signal: str|Event, sender: Any = ANY, weak: bool = True) -> c.Callable[[F], F]:
    sig = signal if isinstance(signal, Event) else event(signal)
    def decorator(fn):
        sig.connect(fn, sender, weak)
        return fn
    return decorator

def emit(event_to_emit: str|Event, sender: Any = ANY, *args, **kwargs):
    event_ = event_to_emit if isinstance(event_to_emit, Event) else event(event_to_emit)
    return event_.emit(sender, *args, **kwargs)

async def emit_async(event_to_emit: str|Event, sender: Any = ANY, *args, **kwargs):
    event_ = event_to_emit if isinstance(event_to_emit, Event) else event(event_to_emit)
    return await event_.emit_async(sender, *args, **kwargs)

# Export all public components
__all__ = [
    'event', 
    'on',
    'emit',
    'emit_async',
    'Event',
    'Namespace',
    'ANY',
    'default_namespace',
]






