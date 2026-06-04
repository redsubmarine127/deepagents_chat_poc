from pydantic import BaseModel


class SkillMetadata(BaseModel):
    id: str
    name: str
    description: str
    path: str
