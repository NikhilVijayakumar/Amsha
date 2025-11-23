# src.nikhil.amsha.toolkit.api.protocol.bot_manager_protocol
from typing import Protocol, Iterable, AsyncIterable, Any, Union


# BotManager contract
class BotManagerProtocol(Protocol):
    def run(self, target: Any, task_type: Any) -> Any:
        """Synchronous execution that returns a final result."""
        ...

    def stream_run(self, target: Any, task_type: Any) -> Union[Iterable[str], AsyncIterable[str]]:
        """
        Return either:
          - a sync iterable/generator yielding string chunks, OR
          - an async iterable/async generator yielding string chunks.
        """
        ...

