from fastapi import FastAPI
import uvicorn
from routers.pièce_jointe import router as pj

app = FastAPI()

app.include_router(pj)

@app.get('/')
def read_root():
    return {"message": "Bienvenue sur mon serveur FastAPI !"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
