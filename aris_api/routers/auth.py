from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aris_api.database import get_session
from aris_api.models import User
from aris_api.schemas import Token
from aris_api.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

# ✅ Define dependências com Annotated (boa prática atual)
FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: FormData,
    session: SessionDep,
):
    user_db = await session.scalar(
        select(User).where(
            (User.email == form_data.username)
            | (User.username == form_data.username)
        )
    )

    if not user_db or not verify_password(
        form_data.password, user_db.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='email ou senha incorretos',
        )

    access_token = create_access_token({'sub': user_db.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
