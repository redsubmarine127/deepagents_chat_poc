from fastapi import APIRouter

from app.skills.schemas import SkillMetadata


def create_router(skills: list[SkillMetadata]) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/skills")
    def list_skills() -> list[SkillMetadata]:
        return skills

    return router
