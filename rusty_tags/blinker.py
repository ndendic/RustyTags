from blinker import ANY, signal
from typing import TypeVar, Any
import collections.abc as c
test2 = signal("test2")

F = TypeVar("F", bound=c.Callable[..., Any])

def event(signal_name: str, sender: Any = ANY, weak: bool = True) -> c.Callable[[F], F]:
    sig = signal(signal_name)
    def decorator(fn):
        sig.connect(fn, sender, weak)
        return fn
    return decorator