from fastapi import FastAPI

app = FastAPI()
@app.get("/inicio")
def correr_back():
    return {"mensaje": "Hola, mundo!"}