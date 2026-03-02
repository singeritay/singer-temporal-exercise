from pydantic import BaseModel, ConfigDict


class TemporalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temporal_server_url: str
    prometheus_bind_address: str = '0.0.0.0:9000'
