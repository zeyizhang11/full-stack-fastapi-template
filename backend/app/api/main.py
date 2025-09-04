from fastapi import APIRouter

from app.api.routes import items, login, users, utils
from app.api.routes import boards, repair_records

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])

# 注册新的路由
api_router.include_router(boards.router, prefix="/boards", tags=["boards"])
api_router.include_router(repair_records.router, prefix="/repair-records", tags=["repair-records"])