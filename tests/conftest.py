from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from aris_api.app import app
from aris_api.database import get_session
from aris_api.models import User, table_registry
from aris_api.security import get_password_hash
from aris_api.settings import settings


@pytest.fixture
def client(db_session):
    """Cria um cliente de teste para FastAPI com a sessão de DB sobrescrita."""

    def get_session_override():
        return db_session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    """Cria uma sessão de banco de dados assíncrona em memória para testes."""
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20)):
    """Mocka a data de criação (created_at) de um modelo no banco."""

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        print(target)

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """Fixture para simular a hora do banco de dados."""
    return _mock_db_time


@pytest_asyncio.fixture
async def user(db_session: AsyncSession):
    """Cria um usuário de teste persistido no banco."""
    password = '123412341234'
    user = User(
        username='teste',
        email='teste@example.com',
        password=get_password_hash(password),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def token(client, user):
    """Gera um token JWT para o usuário de teste."""
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': user.clean_password,
        },
    )
    return response.json().get('access_token')


@pytest.fixture
def test_settings():
    """Retorna as configurações de teste."""
    return settings
