from typing import Callable


def aggregate_callables(*callables: Callable[[], None]):
    for c in callables:
        c()
