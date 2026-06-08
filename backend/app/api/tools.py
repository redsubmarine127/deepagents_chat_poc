from fastapi import APIRouter

from app.tools.schemas import ToolMetadata


def create_router(tools: list[ToolMetadata]) -> APIRouter:
    router = APIRouter()

    @router.get("/tools")
    def list_tools() -> list[ToolMetadata]:
        return tools

    return router
