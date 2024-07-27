from datetime import datetime, timedelta
from typing import Annotated, List
from jose import jwt
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from app.database import SessionLocal
from .schemas import User, UserCreate, Token
import app.crud as crud
from os import environ

router = APIRouter()

SECRET_KEY = environ.get("SECRET_KEY")
ALGORITHM = environ.get("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[SessionLocal, Depends(get_db)]

def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)

    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta = None):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: UserCreate):
    return crud.create_user(db, UserCreate(username=user.username, password=bcrypt_context.hash(user.password)))

@router.get("/users", response_model=List[User])
async def get_users(db: db_dependency):
    return crud.get_users(db)

@router.get("/users/{user_id}", response_model=User)
async def get_user(db: db_dependency, user_id: int):
    return crud.get_user_by_id(db, user_id)

@router.post("/token", response_model=Token)
async def generate_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user(db: db_dependency, token: Annotated[str, Depends(oauth2_bearer)]):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("id")
    username = payload.get("sub")

    return User(username=username, id=user_id)