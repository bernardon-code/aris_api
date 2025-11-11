from http import HTTPStatus

from fastapi import FastAPI

from aris_api.routers import auth, users  # ✅ importa os módulos corretamente
from aris_api.schemas import Message

app = FastAPI()

# registra os routers na app principal
app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá. Mundo!'}
