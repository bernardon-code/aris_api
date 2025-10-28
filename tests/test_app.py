from http import HTTPStatus

from fastapi.testclient import TestClient

from aris_api.app import app

client = TestClient(app)


def test_root_deve_retornar_ola_mundo():
    client = TestClient(app)
    response = client.get('/')
    assert response.json() == {'message': 'Olá. Mundo!'}
    assert response.status_code == HTTPStatus.OK
