from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from aris_api.app import app
from aris_api.database import get_session
from aris_api.models import User, table_registry
from aris_api.security import get_password_hash


@pytest.fixture
def client(db_session):
    def get_session_override():
        return db_session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)
    engine.dispose()


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        print(target)

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(db_session):
    password = '123412341234'
    user = User(
        username='teste',
        email='teste@example.com',
        password=get_password_hash(password),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={
            'username': user.username,
            'password': user.clean_password,
        },
    )
    return response.json().get('access_token')
