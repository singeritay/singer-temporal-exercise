from pydantic import BaseModel, ConfigDict


class TemporalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    temporal_server_url: str
