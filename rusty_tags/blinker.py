import asyncio
import collections.abc as c
import inspect
import threading
from typing import Any, TypeVar

from blinker import ANY, signal

SENTINEL = object()

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

async def send_stream(sig, sender, out_q: asyncio.Queue, *args, **kwargs):
    """
    Iterate all receivers for `sender`, stream their yielded/returned items
    into `out_q` as soon as they're produced.
    """
    async def worker(recv):
        try:
            async for item in _aiter_results(recv, sender, *args, **kwargs):
                if item is not None:
                    await out_q.put(item)
        except Exception as e:
            # push exceptions if you want to surface them to the UI/log
            await out_q.put(e)

    # Run all receivers concurrently
    try:
        async with asyncio.TaskGroup() as tg:
            for recv in sig.receivers_for(sender):
                tg.create_task(worker(recv))
    finally:
        # optional: mark end of this dispatch burst
        await out_q.put(SENTINEL)


F = TypeVar("F", bound=c.Callable[..., Any])

def event(signal_name: str, sender: Any = ANY, weak: bool = True) -> c.Callable[[F], F]:
    sig = signal(signal_name)
    def decorator(fn):
        sig.connect(fn, sender, weak)
        return fn
    return decorator