from fastapi import FastAPI
from routers import solicitudes, info

app = FastAPI()

app.include_router(solicitudes.router)
app.include_router(info.router)

@app.get("/")
def correr_back():
    return {"mensaje": "Hola, mundo!"}