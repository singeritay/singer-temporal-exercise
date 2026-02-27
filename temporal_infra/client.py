from collections.abc import Awaitable
from pathlib import Path
from typing import Optional, Any, Callable, List

from temporalio.client import Client

from .config_loader import ConfigurationLoader
from .config_models import TemporalConfig


class TemporalClient:
    def __init__(self, config_path: Optional[str | Path] = None):
        self.config_path = (Path(config_path) if config_path else Path(__file__).with_name("temporal_config.yml"))
        self.config: TemporalConfig = ConfigurationLoader(self.config_path).load_for_current_env(TemporalConfig)
        self.temporal_server_url = self.config.temporal_server_url

    @property
    def client(self) -> Awaitable[Client]:
        return Client.connect(self.temporal_server_url)

    async def run_workflow(
            self,
            workflow_executable: Callable,
            args: List[Any],
            id: str,
            task_queue: str
    ) -> Any:
        temporal_client = await self.client
        result = await temporal_client.start_workflow(
            workflow_executable,
            args=args,
            id=id,
            task_queue=task_queue,
        )
        return await result.result()
