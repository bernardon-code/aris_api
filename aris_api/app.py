from http import HTTPStatus

from fastapi import FastAPI

from aris_api.schemas import (
    Message, UserDB, UserPublic, UserSchema, 
)

app = FastAPI()
database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá. Mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(
        username=user.username,
        email=user.email,
        passward=user.passward,
        id=len(database) + 1
    )
    database.append(user_with_id)
    return user_with_id
