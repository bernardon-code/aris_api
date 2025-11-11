from http import HTTPStatus

import pytest

from aris_api.database import get_session
from aris_api.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': '123412341234',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': '123412341234',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_delete_user(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'usuário deletado com sucesso',
    }


def test_update_integrity(client, user, token):
    client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': '123412341234',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': '123412341234',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'nome de usuário ou email já existente',
    }


def test_create_user_conflict(client):
    # Cria o primeiro usuário
    client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': '123412341234',
        },
    )

    # Tenta criar outro com o mesmo username
    response = client.post(
        '/users/',
        json={
            'username': 'alice',  # mesmo username
            'email': 'alice2@example.com',
            'password': '123412341234',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'nome de usuário já existe'}

    # Agora testa conflito por email
    response_email_conflict = client.post(
        '/users/',
        json={
            'username': 'bob',
            'email': 'alice@example.com',  # mesmo email
            'password': '123412341234',
        },
    )

    assert response_email_conflict.status_code == HTTPStatus.CONFLICT
    assert response_email_conflict.json() == {'detail': 'email já existe'}


def test_update_user_not_found(client, token):
    # Tenta atualizar um usuário inexistente (id=999)
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'ghost',
            'email': 'ghost@example.com',
            'password': '123412341234',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'usuário não encontrado'}


def test_delete_user_not_found(client):
    # Tenta deletar um usuário inexistente (id=999)
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'usuário não encontrado'}


@pytest.mark.asyncio
async def test_get_session_function():
    generator = get_session()
    session = await anext(generator)
    assert session is not None
    await generator.aclose()  # ✅ fecha corretamente
