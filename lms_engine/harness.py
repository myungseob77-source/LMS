from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Harness:
    """Explicit tool and verifier injection; no arbitrary shell execution."""
    execute: Callable[[str, int], str]
    verify: Callable[[str], bool]

    @classmethod
    def demo(cls):
        return cls(lambda task, attempt: f"Completed: {task}", bool)
