from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from services.user import user_crud
from schemas import user as user_schema


router = APIRouter()


@router.post('/auth', response_model=user_schema.User)
async def auth(
    user_in: user_schema.UserAuth,
    *,
    db: AsyncSession = Depends(get_session)
):
    user = await user_crud.auth(db=db, obj_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or password is not correct'
        )
    return user


@router.post('/', response_model=user_schema.User)
async def create(
    user_in: user_schema.UserCreate,
    *,
    db: AsyncSession = Depends(get_session),
):
    user = await user_crud.create(db=db, obj_in=user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username exist'
        )
    return user
