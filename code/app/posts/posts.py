from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import Post, PostCreate
from typing import Annotated, List
from app.crud import get_post_by_id, create_post, get_posts
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import app.config as config
from fastapi_cache.decorator import cache
from app.database import get_db

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

router = APIRouter()


db_dependency = Annotated[SessionLocal, Depends(get_db)]

@router.get("/", response_model=List[Post])
@cache(expire=60)
async def get_posts_route(db: db_dependency, limit: int = 100):
    return get_posts(db, limit=limit)

@router.post("/", response_model=Post)
async def create_post_route(db: db_dependency, post: PostCreate, token: Annotated[str, Depends(oauth2_bearer)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    if payload.get("refresh") is not None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Required access token")

    return create_post(db, post, user_id)

@router.get("/{id}", response_model=Post)
@cache(expire=60)
async def get_post_route(id: str, db: db_dependency):
    post = get_post_by_id(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post