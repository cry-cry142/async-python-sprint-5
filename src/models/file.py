from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, unique=True, index=True)
    user_id = Column(ForeignKey('users.id'))
    user = relationship('User', back_populates='files')
