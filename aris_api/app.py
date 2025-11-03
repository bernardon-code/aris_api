from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aris_api.database import get_session
from aris_api.models import User
from aris_api.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá. Mundo!'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Nome de usuário já existe',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email já existe',
            )

    user_db = User(
        username=user.username,
        email=user.email,
        password=user.password,
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    try:
        user_db.username = user.username
        user_db.email = user.email
        user_db.password = user.password
        session.commit()
        session.refresh(user_db)

        return user_db
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='nome de usuário ou email já existente',
        )


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    session.delete(user_db)
    session.commit()
    return Message(message='usuário deletado com sucesso')
