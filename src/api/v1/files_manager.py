import urllib
from typing import Annotated, List
from fastapi import APIRouter, UploadFile, HTTPException, status, Depends, Header
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from services.file import file_crud
from services.user import user_crud
from schemas import file as file_schema
from db.db import get_session


router = APIRouter()
security = HTTPBearer()


async def verify_token(authorization: str = Header(security)):
    def is_valid(token: str) -> bool:
        if not isinstance(token, str) or 'Bearer' not in token:
            return False
        return True

    if not is_valid(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authorization'
        )


async def get_auth_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_session),
):
    unauth_ex = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Fail authorization user'
    )
    user = await user_crud.get_for_token(
        db=db,
        token=credentials.credentials
    )
    if not user:
        raise unauth_ex
    return user


@router.post(
    '/upload',
    dependencies=[Depends(verify_token)],
    response_model=file_schema.File
)
async def upload(
    path: UploadFile,
    *,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_auth_user),
):
    result = await file_crud.create(db=db, path=path, active_user=user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File name exist'
        )
    return result


@router.get(
    '/download',
    dependencies=[Depends(verify_token)]
)
async def download(
    path: str,
    *,
    db: AsyncSession = Depends(get_session),
    user=Depends(get_auth_user),
):
    file = await file_crud.get(
        db=db,
        file_name=path,
        active_user=user
    )
    bin_obj = file['Body'].read()
    fn = urllib.parse.quote(path)

    return Response(
        content=bin_obj,
        media_type=file['ContentType'],
        headers={
            'Content-Disposition': f'attachment; filename={fn}'
        }
    )


@router.get(
    '/',
    dependencies=[Depends(verify_token)],
    response_model=List[file_schema.File]
)
async def files(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    *,
    user=Depends(get_auth_user),
):
    files = await file_crud.get_all_files(
        db=db,
        active_user=user,
        skip=skip,
        limit=limit
    )

    return files
