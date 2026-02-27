import os
from collections.abc import Awaitable, Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional, TypeAlias, Type, List

from temporalio.client import Client
from temporalio.worker import Worker

from .config_loader import ConfigurationLoader
from .config_models import TemporalConfig

TemporalActivity: TypeAlias = Callable[..., Any] | Callable[..., Awaitable[Any]]
TemporalWorkflow: TypeAlias = Type


class TemporalWorker:
    def __init__(
            self,
            config_path: Optional[str | Path] = None,
            tasks_queue_name: str = None,
            activities: Optional[Iterable[TemporalActivity]] = None,
            workflows: Optional[Iterable[TemporalWorkflow]] = None,
    ):
        self.config_path = (Path(config_path) if config_path else Path(__file__).with_name("temporal_config.yml"))
        self.config: TemporalConfig = ConfigurationLoader(self.config_path).load_for_current_env(TemporalConfig)
        self.temporal_server_url = self.config.temporal_server_url
        self.tasks_queue_name = os.getenv("TASKS_QUEUE_NAME", tasks_queue_name)
        if not self.tasks_queue_name:
            raise ValueError("Missing required task queue name. Set TASKS_QUEUE_NAME or pass task_queue_name.")
        self.tasks_queue_name = self.tasks_queue_name.strip()
        self._workflows: List[TemporalWorkflow] = []
        self._activities: List[TemporalActivity] = []
        if activities:
            self.add_activities(*activities)
        if workflows:
            self.add_workflows(*workflows)

    async def run(self):
        if not self._workflows and not self._activities:
            raise ValueError("Cannot run worker without registered workflows or activities.")
        client = await Client.connect(self.temporal_server_url)
        with ThreadPoolExecutor(max_workers=10) as executor:
            worker = Worker(
                client=client,
                task_queue=self.tasks_queue_name,
                workflows=self._workflows,
                activities=self._activities,
                activity_executor=executor
            )
            return await worker.run()

    def add_activities(self, *activities_to_add: TemporalActivity) -> None:
        if not activities_to_add:
            return
        for activity_fn in activities_to_add:
            if not callable(activity_fn):
                raise ValueError("Invalid activity type. Activities must be callable functions.")
            self._activities.append(activity_fn)

    def add_workflows(self, *workflows_to_add: TemporalWorkflow) -> None:
        if not workflows_to_add:
            return
        for workflow_cls in workflows_to_add:
            if not isinstance(workflow_cls, type):
                raise ValueError("Invalid workflow type. Workflows must be classes.")
            self._workflows.append(workflow_cls)
