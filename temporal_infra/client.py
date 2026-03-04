import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Any, Callable, List

from temporalio.api import workflowservice
from temporalio.client import Client
from temporalio.runtime import Runtime, TelemetryConfig, PrometheusConfig
from temporalio.service import RPCError

from .logger_provider import TemporalLogger
from .config_loader import ConfigurationLoader
from .config_models import TemporalConfig


class TemporalClient:
    def __init__(self, config_path: Optional[str | Path] = None,
                 use_prometheus_server: bool = False, logger: logging.Logger = None
                 ):
        self.config_path = (Path(config_path) if config_path else Path(__file__).with_name("temporal_config.yml"))
        self.config: TemporalConfig = ConfigurationLoader(self.config_path).load_for_current_env(TemporalConfig)
        self.temporal_server_url = self.config.temporal_server_url
        self.use_prometheus_server = use_prometheus_server
        self.prometheus_bind_address = self._resolve_prometheus_bind_address()
        self.logger = logger or TemporalLogger()

    def _resolve_prometheus_bind_address(self) -> str:
        bind_address = os.getenv(
            "TEMPORAL_PROMETHEUS_BIND_ADDRESS",
            self.config.prometheus_bind_address,
        ).strip()
        if self.use_prometheus_server and not bind_address:
            raise ValueError(
                "Missing Prometheus bind address. Set TEMPORAL_PROMETHEUS_BIND_ADDRESS "
                "or provide prometheus_bind_address in temporal_config.yml."
            )
        return bind_address

    async def try_connect_to_client(self) -> Optional[Client]:
        try:
            runtime = self._get_runtime()
            client = await Client.connect(self.temporal_server_url, runtime=runtime)
            sample_request = workflowservice.v1.GetSystemInfoRequest()
            await client.service_client.workflow_service.get_system_info(sample_request)
            self.logger.info("Readiness check successful: Temporal Server is reachable.")
            return client
        except (RPCError, asyncio.TimeoutError, RuntimeError) as e:
            self.logger.error(f"Readiness check failed: {e}")
            raise

    def _get_runtime(self) -> Optional[Runtime]:
        if self.use_prometheus_server:
            return Runtime(
                telemetry=TelemetryConfig(
                    metrics=PrometheusConfig(bind_address=self.prometheus_bind_address),
                )
            )
        return None

    async def run_workflow(
            self,
            workflow_executable: Callable,
            args: List[Any],
            id: str,
            task_queue: str
    ) -> Any:
        temporal_client = await self.try_connect_to_client()
        result = await temporal_client.start_workflow(
            workflow_executable,
            args=args,
            id=id,
            task_queue=task_queue,
        )
        return await result.result()
