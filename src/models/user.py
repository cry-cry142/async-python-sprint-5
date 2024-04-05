from uuid import uuid4
from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, index=True)
    hashed_password = Column(String(64))
    token = Column(String(32), unique=True, index=True, default=uuid4().hex)
    files = relationship('File', back_populates='user')
