import asyncio
import imaplib
from imapclient import IMAPClient
from AtelierCyber2.backend_listener.db.db import get_db

tasks = {}



# Configuration des emails
EMAIL_ACCOUNTS = [
    {"server": "imap.laposte.net", "email": "rom1298@laposte.net", "password": "$3?AhTdxX&Cmq&F"},
    {"server": "imap.laposte.net", "email": "rom1298@laposte.net", "password": "$3?AhTdxX&Cmq&F"}
]

import asyncio
import datetime
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from imapclient import IMAPClient
from db.db import AsyncSessionLocal
from db.models import EmailAccountinDB


# 🔁 Fréquence de mise à jour
CHECK_INTERVAL = 5
active_tasks = {}

async def fetch_accounts():
    """Récupère les comptes actifs à surveiller (Mode Synchrone)"""
    async with AsyncSessionLocal() as session:
        accounts = await session.query(EmailAccountinDB).all()
        return accounts

async def check_mail(account):
    """Écoute les emails IMAP pour un compte spécifique"""
    email = account.email
    try:
        with IMAPClient(account.server) as client:
            client.login(email, account.password)
            client.select_folder("INBOX")

            since_date = datetime.date.today()  # Filtre depuis aujourd'hui
            
            while True:
                messages = client.search(["SINCE", since_date.strftime("%d-%b-%Y"), "UNSEEN"])
                if messages:
                    print(f"📩 {len(messages)} nouveaux emails sur {email} !")

                await asyncio.sleep(CHECK_INTERVAL)  # ⏳ Ne bloque pas les autres tâches
    except Exception as e:
        print(f"Erreur pour {email} : {e}")

async def monitor_accounts():
    """Surveille dynamiquement les comptes à surveiller"""
    global active_tasks

    while True:
        print("🔄 Mise à jour de la liste des comptes à surveiller...")
        accounts = fetch_accounts()
        current_emails = set(active_tasks.keys())
        new_emails = {account.email for account in accounts}

        # 🟢 Ajouter les nouveaux comptes
        for account in accounts:
            if account.email not in active_tasks:
                print(f"✅ Ajout de {account.email} à la surveillance")
                task = asyncio.create_task(check_mail(account))
                active_tasks[account.email] = task

        # 🔴 Supprimer les comptes inactifs
        for email in current_emails - new_emails:
            print(f"❌ Suppression de {email} de la surveillance")
            active_tasks[email].cancel()
            del active_tasks[email]

        await asyncio.sleep(30)  # Attendre avant la prochaine mise à jour

# 🚀 Lancer le programme
async def main():
    await monitor_accounts()

asyncio.run(main())