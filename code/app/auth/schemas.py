from pydantic import BaseModel

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class AllTokens(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class User(BaseModel):
    id: int
    username: str
    email: str
    verified: bool
    
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: str