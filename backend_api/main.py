from fastapi import FastAPI, Request, HTTPException
import uvicorn
from routers.auth import router as auth
from routers.mail_manager import router as mail_router
from routers.admin import router as admin
from routers.blacklist import router as blacklist
from routers.emails import router as emails
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Go to http://127.0.0.1:8000/docs if you want a pretty interface or /redoc but it's not as good (imo)
# Else use curl but it's tedious, here's an example just in case: 
# curl -X 'POST' 'http://127.0.0.1:8000/connect/imap' -H 'Content-Type: application/json' -d '{"server": "server", "email": "email", "password": "password"}'

app.include_router(mail_router)
app.include_router(auth)
app.include_router(admin)
app.include_router(blacklist)
app.include_router(emails)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
