from fastapi import FastAPI
from cryptography.fernet import Fernet
import uvicorn
from contextlib import asynccontextmanager
from routers.auth import router as auth
from routers.mail_manager import router as mail_router
from routers.admin import router as admin
from routers.blacklist import router as blacklist
from routers.emails import router as emails
from routers.stats import router as stats
from fastapi.middleware.cors import CORSMiddleware
from utils.db import get_db
from utils.imap import start_imap_listeners, stop_imap_listeners
from routers.stats import create_global_stats
from routers.auth import create_first_admin_account


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    print("🚀 Démarrage de l'application...")

    
    db = next(get_db())  # Récupération d'une session DB
    create_global_stats(db)  # Création des statistiques globales
    create_first_admin_account(db)  # Création du premier compte admin si nécessaire
    start_imap_listeners(db)  # Démarrage des listeners IMAP

    yield  # Attente que l'application tourne

    print("🛑 Arrêt de l'application...")
    stop_imap_listeners()  # Arrêt propre des listeners



app = FastAPI(lifespan=lifespan)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Go to http://127.0.0.1:8000/docs if you want a pretty interface or /redoc but it's not as good (imo)
# Else use curl but it's tedious, here's an example just in case
# curl -X 'POST' 'http://127.0.0.1:8000/connect/imap' -H 'Content-Type: application/json' -d '{"server": "server", "email": "email", "password": "password"}'

app.include_router(mail_router)
app.include_router(auth)
app.include_router(admin)
app.include_router(blacklist)
app.include_router(emails)
app.include_router(stats)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
