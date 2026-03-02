import asyncio
import os
from collections.abc import Awaitable, Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional, TypeAlias, Type

from temporalio.worker import Worker

from .client import TemporalClient
from .config_loader import ConfigurationLoader
from .config_models import TemporalConfig
from .logger_provider import TemporalLogger

TemporalActivity: TypeAlias = Callable[..., Any] | Callable[..., Awaitable[Any]]
TemporalWorkflow: TypeAlias = Type

DEFAULT_CONFIG_FILE = 'temporal_config.yml'


class TemporalWorker:
    def __init__(
            self,
            config_path: Optional[str | Path] = None,
            tasks_queue_name: str = None,
            activities: Optional[Iterable[TemporalActivity]] = None,
            workflows: Optional[Iterable[TemporalWorkflow]] = None,
            use_prometheus_server: bool = True
    ):
        self.config_path = Path(config_path) if config_path else Path(__file__).with_name(DEFAULT_CONFIG_FILE)
        self.config = ConfigurationLoader(self.config_path).load_for_current_env(TemporalConfig)
        self.temporal_server_url = self.config.temporal_server_url
        self.use_prometheus_server = use_prometheus_server
        self.tasks_queue_name = self._resolve_task_queue_name(tasks_queue_name)
        self._workflows, self._activities = [], []
        self.logger = self._initialize_logger()
        self._register_initial_handlers(activities=activities, workflows=workflows)

    @staticmethod
    def _resolve_task_queue_name(tasks_queue_name: Optional[str]) -> str:
        resolved_queue_name = os.getenv("TASKS_QUEUE_NAME", tasks_queue_name)
        if not resolved_queue_name:
            raise ValueError("Missing required task queue name. Set TASKS_QUEUE_NAME or pass task_queue_name.")
        return resolved_queue_name.strip()

    def _initialize_logger(self) -> TemporalLogger:
        self.logger = TemporalLogger(name="temporalio")
        self.logger.info("Logger initialized for temporalio namespace")
        return self.logger

    def _register_initial_handlers(self, activities: Optional[Iterable[TemporalActivity]],
                                   workflows: Optional[Iterable[TemporalWorkflow]]) -> None:
        if activities:
            self.add_activities(*activities)
        if workflows:
            self.add_workflows(*workflows)

    async def run(self):
        if not self._workflows and not self._activities:
            raise ValueError("Cannot run worker without registered workflows or activities.")
        client = await TemporalClient(config_path=self.config_path, use_prometheus_server=self.use_prometheus_server).try_connect_to_client()
        with ThreadPoolExecutor(max_workers=10) as executor:
            heartbeat_task = asyncio.create_task(self._heartbeat())
            worker = Worker(
                client=client,
                task_queue=self.tasks_queue_name,
                workflows=self._workflows,
                activities=self._activities,
                activity_executor=executor
            )
            try:
                self.logger.info("Running worker")
                return await worker.run()
            finally:
                heartbeat_task.cancel()
        #TODO: graceful shutdown

    async def _heartbeat(self):
        while True:
            self.logger.info("Worker heartbeat: Healthy and polling queue",
                             extra={"queue": self.tasks_queue_name})
            await asyncio.sleep(10)

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
