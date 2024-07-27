from fastapi import APIRouter, Depends, HTTPException
from .schemas import Post, PostCreate
from typing import Annotated, List
from app.crud import get_post_by_id, create_post, get_posts
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from os import environ

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = environ.get("ALGORITHM")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[SessionLocal, Depends(get_db)]

@router.get("/", response_model=List[Post])
async def get_posts_route(db: db_dependency):
    return get_posts(db)

@router.post("/", response_model=Post)
async def create_post_route(db: db_dependency, post: PostCreate, token: Annotated[str, Depends(oauth2_bearer)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("id")

    return create_post(db, post, user_id)

@router.get("/{id}", response_model=Post)
async def get_post(id: int, db: db_dependency):
    post = get_post_by_id(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post