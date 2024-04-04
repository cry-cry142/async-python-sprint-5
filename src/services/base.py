from typing import Any, Generic, List, Optional, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder


from models.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(
    Repository, Generic[ModelType, CreateSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(
        self,
        db: AsyncSession,
        id: Any
    ) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == id)
        result = await db.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip=0,
        limit=100
    ) -> List[ModelType]:
        statement = select(self._model).offset(skip).limit(limit)
        result = await db.execute(statement=statement)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> ModelType:
        statement = select(self._model).where(self._model.id == id)
        result = await db.execute(statement=statement)
        db_obj = result.scalar_one_or_none()
        await db.delete(db_obj)
        await db.commit()
        return db_obj
