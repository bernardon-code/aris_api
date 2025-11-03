from http import HTTPStatus

from aris_api.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client):
    response = client.get('/')
    assert response.json() == {'message': 'Olá. Mundo!'}
    assert response.status_code == HTTPStatus.OK


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


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
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


def test_update_integrity(client, user):
    client.post(
        '/users/',
        json={
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': '123412341234',
        },
    )
    response = client.put(
        f'/users/{user.id}',
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
