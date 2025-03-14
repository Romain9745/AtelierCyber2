
from sqlalchemy.orm import Session
from config import cipher
from imapclient import IMAPClient
from email.utils import parsedate_tz, mktime_tz
from email import policy
from bs4 import BeautifulSoup
from datetime import datetime
from db.models import MailsInDb, EmailAccountinDB
from pydantic import BaseModel
import email
import asyncio
from fastapi import HTTPException
from utils.analyse import Email, analyse_email, EmailAnalysis

tasks = {}

async def start_imap_listener(email: str, password: str, imap_server: str, db):
    """Garde la connexion IMAP ouverte et surveille les nouveaux emails."""
    while email in tasks:  # Vérifie si la tâche est encore active
        try:
            with IMAPClient(imap_server) as client:
                client.login(email, password)
                client.select_folder("INBOX")

                while email in tasks:
                    messages = client.search("UNSEEN")
                    if messages:
                        print(f"📩 {len(messages)} nouveaux emails pour {email}")
                        mail = fetch_latest_email(client)
                        if mail:
                            asyncio.create_task(check_mail(mail, email, client, db))
                    await asyncio.sleep(5)

        except Exception as e:
            print(f"Erreur IMAP ({email}): {e}. Reconnexion dans 10s...")
            await asyncio.sleep(10)

async def start_imap_listener_after_login(email: str, password: str, imap_server: str, db):
    if email in tasks:
        raise ValueError(f"Le listener pour {email} est déjà en cours ")
    task= asyncio.create_task(start_imap_listener(email, password, imap_server, db))
    tasks[email] = task


def start_imap_listeners(db):
    """Démarre les listeners pour chaque compte email."""
    email_accounts = get_email_imap_accounts(db)
    for account in email_accounts:
        if account.email in tasks:
            print(f"Le listener pour {account.email} est déjà en cours.")
            continue  # Ne pas relancer une tâche déjà active

        try:
            # Tentative de déchiffrement du mot de passe
            password = cipher.decrypt(account.imap_password.encode()).decode()
            print(f"Démarrage du listener pour {account.email}...")

            # Créer une tâche pour chaque compte
            task = asyncio.create_task(start_imap_listener(account.email, password, account.imap_host, db))
            tasks[account.email] = task
            print(f"Listener pour {account.email} démarré avec succès.")

        except Exception as e:
            # Gestion des erreurs générales
            error_message = f"Erreur de démarrage du listener pour {account.email}: {e}"
            print(error_message)

            # Si c'est une erreur de déchiffrement du mot de passe
            if isinstance(e, ValueError):
                print(f"Impossible de déchiffrer le mot de passe pour {account.email}. Vérifie la clé de chiffrement.")
            # Continuer avec le prochain compte sans arrêter le processus

            continue



def stop_imap_listeners():
    """Arrête toutes les tâches IMAP en cours."""
    for email, task in tasks.items():
        task.cancel()
    tasks.clear()


def stop_imap_listener(email: str):
    """Arrête une tâche IMAP spécifique."""
    if email in tasks:
        tasks[email].cancel()
        del tasks[email]
        return True
    return False



async def check_mail(email: Email, mail: str, client: IMAPClient,db: Session):
    try:
        email_analys = await analyse_email(email,mail,db)
        if email_analys.phishing_detected:
            client.move(email.email_id, "Spam")
            print(f"Email moved to Junk: {email_analys.explanation}")
        db.add(MailsInDb(
                source=email.from_email,
                recipient=email.to_email,
                subject=email.subject,
                explanation=email_analys.explanation,
                email_body=email.body,
                receive_date=email.timestamp,
                analyzed_date=datetime.now(),
                is_phishing=email_analys.phishing_detected,
                blocked_date=datetime.now(),
                folder_id=1,
                source_email=mail
            ))
        db.commit()
        db.refresh()
            
    except Exception as e:
        print(f"Error analysing email: {e}")



def fetch_latest_email(client):
    """Fetches the latest unread email"""
    try:
        messages = client.search("UNSEEN")  # Fetch unread emails
        if not messages:
            return

        latest_email_id = messages[-1]
        response = client.fetch(latest_email_id, ["RFC822"])
        raw_email = response[latest_email_id][b"RFC822"]

        msg = email.message_from_bytes(raw_email, policy=policy.default)

        sender = msg["from"]
        recipient = msg["to"]
        subject = msg["subject"]
        date_str = msg["date"]

        # Convert email date to timestamp
        timestamp = None
        if date_str:
            parsed_date = parsedate_tz(date_str)  # Parse the date
            if parsed_date:
                timestamp = mktime_tz(parsed_date)  # Convert to timestamp (seconds)

        body = ""

        # Extract email content
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")
                    break
                elif content_type == "text/html" and not body:
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors="ignore")

        # Convert HTML to text if necessary
        text_body = BeautifulSoup(body, "html.parser").get_text()

        return Email(email_id=latest_email_id,from_email=sender, to_email=recipient, subject=subject, body=text_body, timestamp=datetime.fromtimestamp(timestamp))
    except Exception as e: 
        print(f"Error fetching email: {e}")


def get_email_imap_accounts(db: Session):
    email_imap_accounts = db.query(EmailAccountinDB).filter(EmailAccountinDB.account_type == 1).all()
    return email_imap_accounts