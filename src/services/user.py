from hashlib import sha256
from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User as UserModel
from schemas.user import UserCreate, UserAuth
from .base import RepositoryDB


class RepositoryUser(RepositoryDB[UserModel, UserCreate]):
    async def get_for_token(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[UserModel]:
        statement = select(self._model).where(self._model.token == token)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate
    ) -> Optional[UserModel]:
        obj_in_data: dict = jsonable_encoder(obj_in)
        statement = select(self._model).where(
            self._model.username == obj_in_data['username']
        )
        result = await db.execute(statement=statement)
        user = result.scalar_one_or_none()
        if user:
            return
        hashed_password = sha256(
            bytes(obj_in_data.pop('password'), encoding='utf-8')
        ).hexdigest()
        obj_in_data['hashed_password'] = hashed_password
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def auth(
        self,
        db: AsyncSession,
        *,
        obj_in: UserAuth,
        # username: str,
        # password: str
    ) -> Optional[UserModel]:
        obj_in_data: dict = jsonable_encoder(obj_in)
        hashed_password = sha256(
            bytes(obj_in_data['password'], encoding='utf-8')
        ).hexdigest()
        statement = select(self._model).where(
            self._model.username == obj_in_data['username'],
            self._model.hashed_password == hashed_password
        )
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()


user_crud = RepositoryUser(UserModel)
