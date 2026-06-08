from pydantic import BaseModel


class ToolMetadata(BaseModel):
    id: str
    name: str
    description: str
    path: str
