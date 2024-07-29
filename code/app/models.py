from .database import Base
from .utils import generate_id
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    verified = Column(Boolean, nullable=False, default=False)

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, nullable=False, autoincrement=False, default=generate_id)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(DateTime, nullable=False, default=datetime.now())
    author = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")