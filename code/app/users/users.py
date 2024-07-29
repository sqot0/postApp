from typing import Annotated, List
from fastapi import Depends, APIRouter
from app.database import SessionLocal
from app.auth.schemas import User
import app.crud as crud
from fastapi_cache.decorator import cache
from app.database import get_db

router = APIRouter()

db_dependency = Annotated[SessionLocal, Depends(get_db)]

@router.get("/", response_model=List[User])
@cache(expire=60)
async def get_users(db: db_dependency, limit: int = 100):
    return crud.get_users(db, limit=limit)

@router.get("/{user_id}", response_model=User)
@cache(expire=60)
async def get_user(db: db_dependency, user_id: int):
    return crud.get_user_by_id(db, user_id)