import os
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from typing import Any, Optional, TypeAlias, Type, List

from temporalio.client import Client
from temporalio.worker import Worker

from .config_loader import ConfigurationLoader
from .config_models import TemporalConfig

TemporalActivity: TypeAlias = Callable[..., Any] | Callable[..., Awaitable[Any]]
TemporalWorkflow: TypeAlias = Type


class TemporalWorker:
    def __init__(self, config_path: Optional[str | Path] = None, tasks_queue_name: str = None):
        self.config_path = (Path(config_path) if config_path else Path(__file__).with_name("temporal_config.yml"))
        self.config: TemporalConfig = ConfigurationLoader(self.config_path).load_for_current_env(TemporalConfig)
        self.temporal_server_url = self.config.temporal_server_url
        self.tasks_queue_name = os.getenv("TASKS_QUEUE_NAME", tasks_queue_name)
        if not self.tasks_queue_name:
            raise ValueError("Missing required task queue name. Set TASKS_QUEUE_NAME or pass task_queue_name.")
        self.tasks_queue_name = self.tasks_queue_name.strip()
        self._workflows: List[TemporalWorkflow] = []
        self._activities: List[TemporalActivity] = []

    async def run(self):
        if not self._workflows and not self._activities:
            raise ValueError("Cannot run worker without registered workflows or activities.")
        client = await Client.connect(self.temporal_server_url)
        worker = Worker(client=client,
                        task_queue=self.tasks_queue_name,
                        workflows=self._workflows,
                        activities=self._activities)
        return await worker.run()

    def add_activities(self, activities: TemporalActivity | Iterable[TemporalActivity]) -> None:
        activities = self._normalize_to_list(activities)
        for activity in activities:
            if not isinstance(activity, TemporalActivity):
                raise ValueError("Invalid activity type.")
        self._activities.extend(activities)

    def add_workflows(self, workflows: TemporalWorkflow | Iterable[TemporalWorkflow]) -> None:
        workflows = self._normalize_to_list(workflows)
        for workflow in workflows:
            if not isinstance(workflow, TemporalWorkflow):
                raise ValueError("Invalid workflow type.")
        self._workflows.extend(workflows)

    @staticmethod
    def _normalize_to_list(item_or_items: Any) -> List[Any]:
        if isinstance(item_or_items, Iterable) and not isinstance(item_or_items, (str, bytes)):
            return list(item_or_items)
        return [item_or_items]
