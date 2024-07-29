from datetime import datetime, timedelta
from typing import Annotated
from jose import jwt
from fastapi import Depends, HTTPException, APIRouter, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from app.database import SessionLocal
from .schemas import User, UserCreate, AccessToken, AllTokens
import app.crud as crud
import app.config as config
from app.utils import send_verification_email
from app.database import get_db

router = APIRouter()

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

db_dependency = Annotated[SessionLocal, Depends(get_db)]

def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user or not bcrypt_context.verify(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if to_encode.get("sub") is not None: to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, user: UserCreate, background_tasks: BackgroundTasks):
    user = crud.create_user(db, UserCreate(username=user.username, password=bcrypt_context.hash(user.password), email=user.email))
    verification_token = create_access_token({"id": user.id}, timedelta(hours=1))
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    return user

@router.post("/login", response_model=AllTokens)
async def login(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.id}, timedelta(minutes=20))
    refresh_token = create_access_token({"sub": user.id, "refresh": True}, timedelta(days=30))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/verify", response_model=User)
async def verify_user(db: db_dependency, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        user = crud.user_verify(db, user_id)
        return User(id=user.id, username=user.username, email=user.email, verified=user.verified)
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@router.post("/refresh", response_model=AccessToken)
async def refresh_token(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if payload.get("refresh") is None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        new_access_token = create_access_token({"sub": user_id}, timedelta(minutes=20))
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

@router.get("/me", response_model=User)
async def get_current_user(db: db_dependency, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_id = payload.get("sub")
        if payload.get("refresh") is not None: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Required access token")
        user = crud.get_user_by_id(db, user_id)
        return User(id=user.id, username=user.username, email=user.email, verified=user.verified)
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")