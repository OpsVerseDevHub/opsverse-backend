from pydantic import BaseModel

class SlackMappingCreate(BaseModel):
    project_id: int
    slack_channel_id: str
