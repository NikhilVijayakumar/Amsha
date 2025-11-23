# src.nikhil.amsha.toolkit.api.protocol.bot_manager_protocol
from typing import Protocol, Iterable, AsyncIterable, Any, Union

from nikhil.amsha.toolkit.api.protocol.task_config_protocol import TaskConfigProtocol


class BotManagerProtocol(Protocol):
    def run(self, utility_task: TaskConfigProtocol.UtilsType) -> Any:
        """Synchronous execution of a utility task that returns a final result."""
        ...

    def stream_run(self, application_task: TaskConfigProtocol.ApplicationType) -> Union[Iterable[str], AsyncIterable[str]]:
        """
        Streamable execution of an application task.
        Returns either a sync or async iterable yielding string chunks.
        """
        ...

