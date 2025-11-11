from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from aris_api.database import get_session
from aris_api.models import User
from aris_api.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from aris_api.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

# ✅ Define o tipo de dependência com Annotated
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
async def create_user(user: UserSchema, session: SessionDep):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='nome de usuário já existe',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='email já existe',
            )

    user_db = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(user_db)
    await session.commit()  # ✅ await
    await session.refresh(user_db)  # ✅ await
    return user_db


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: SessionDep,
    get_current_user: CurrentUserDep,
    filter_users: Annotated[FilterPage, Query()],
):
    result = await session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    )
    users = result.all()  # ✅ precisa materializar a lista
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,
    current_user: CurrentUserDep,  # ✅ nome correto
):
    user_db = await session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='usuário não encontrado',
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='não autorizado para atualizar este usuário',
        )

    try:
        user_db.username = user.username
        user_db.email = user.email
        user_db.password = get_password_hash(user.password)
        await session.commit()
        await session.refresh(user_db)
        return user_db
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='nome de usuário ou email já existente',
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_user(user_id: int, session: SessionDep):
    user_db = await session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='usuário não encontrado',
        )

    await session.delete(user_db)  # ✅ await
    await session.commit()  # ✅ await
    return Message(message='usuário deletado com sucesso')
