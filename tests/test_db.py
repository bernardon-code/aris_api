from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ import adicionado

from aris_api.models import User


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, mock_db_time):
    """Testa a criação de um novo usuário e valida os campos persistidos."""
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Julio',
            email='julio@gmail.com',
            password='123412341234',
        )
        db_session.add(new_user)
        await db_session.commit()

        user = await db_session.scalar(
            select(User).where(User.username == 'Julio')
        )  # ✅ parêntese fechado corretamente

        assert asdict(user) == {
            'id': 1,
            'username': 'Julio',
            'email': 'julio@gmail.com',
            'password': '123412341234',
            'created_at': time,
        }
