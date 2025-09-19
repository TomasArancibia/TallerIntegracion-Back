from fastapi import FastAPI
from routers import solicitudes

app = FastAPI()

app.include_router(solicitudes.router)

@app.get("/")
def correr_back():
    return {"mensaje": "Hola, mundo!"}