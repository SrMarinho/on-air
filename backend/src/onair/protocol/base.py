from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
