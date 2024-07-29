from fastapi import APIRouter
from app.auth.auth import router as auth_router
from app.posts.posts import router as posts_router
from app.users.users import router as users_router
from app.database import Base, engine

router = APIRouter()

Base.metadata.create_all(bind=engine)

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(posts_router, prefix="/posts", tags=["posts"])
