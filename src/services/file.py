import boto3
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi import UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.file import File as FileModel
from models.user import User as UserModel
from schemas.file import FileCreate
from .base import RepositoryDB

s3 = boto3.client(
    service_name='s3',
    endpoint_url=settings.url_aws
)


class RepositoryFile(RepositoryDB[FileModel, FileCreate]):
    async def create(
        self,
        db: AsyncSession,
        *,
        path: UploadFile,
        active_user: UserModel
    ) -> Optional[FileModel]:
        statement = select(self._model).where(
            self._model.file_name == path.filename
        )
        result = await db.execute(statement=statement)
        file = result.scalar_one_or_none()
        if file:
            return

        # Upload to S3
        bin_data = await path.read()
        s3.put_object(
            Bucket=settings.bucket_name,
            Key=path.filename, Body=bin_data
        )

        obj_in_data = {
            'user': active_user,
            'file_name': path.filename
        }
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        file_name: str, 
        active_user: UserModel
    ) -> Optional[FileModel]:
        statement = select(self._model).where(
            self._model.file_name == file_name,
            self._model.user == active_user
        )
        result = await db.execute(statement=statement)
        file = result.scalar_one_or_none()
        if not file:
            return

        # Download from S3
        obj_file = s3.get_object(
            Bucket=settings.bucket_name,
            Key=file.file_name
        )

        return obj_file

    async def get_all_files(
        self,
        db: AsyncSession,
        active_user: UserModel = None,
        *,
        skip=0,
        limit=100,
    ) -> Optional[FileModel]:
        if active_user:
            statement = select(self._model).where(
                self._model.user == active_user
            ).offset(skip).limit(limit)
        else:
            statement = select(self._model).offset(skip).limit(limit)
        result = await db.execute(statement=statement)
        files = result.scalars().all()
        return files


file_crud = RepositoryFile(FileModel)
