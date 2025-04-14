import asyncio
from db.db import AsyncSessionLocal
from db.models import EmailAccountinDB
import aioimaplib
from sqlalchemy.future import select
from config import cipher
from datetime import datetime
from email.utils import parsedate_tz, mktime_tz, parseaddr
from email import policy
from email import message_from_bytes
from bs4 import BeautifulSoup
import email
from pydantic import BaseModel
import httpx


CHECK_INTERVAL = 5
active_tasks = {}

class Email(BaseModel):
    email_id: int
    from_email: str
    to_email: str
    subject: str
    body: str
    timestamp: datetime
    attachments: list[dict]

class EmailAnalysisRequestData(BaseModel):
    email: Email
    account: str

async def send_email_to_api(data: EmailAnalysisRequestData):
    """Envoie les données d'email à l'API de façon asynchrone."""
    url = "http://api:8000/imap/email"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data.model_dump(mode="json"))
        if response.status_code == 200:
            print("Email successfully sent to the API")
        else:
            print(f"Failed to send email: {response.status_code}")

async def fetch_accounts():
    """Récupère les comptes actifs à surveiller"""
    async with AsyncSessionLocal() as session:
    # Use select() instead of query() for asynchronous queries
        result = await session.execute(select(EmailAccountinDB))
        accounts = result.scalars().all()  # Get the actual list of accounts
        return accounts

async def imap_listener(account):
    """Écoute les emails IMAP pour un compte spécifique"""
    email = account.email
    try:
            client = aioimaplib.IMAP4_SSL(account.imap_host)
            await client.wait_hello_from_server()
            print('decrypting')
            password = cipher.decrypt(account.imap_password.encode()).decode()
            await client.login(email, password)
            print('logged in')
            await client.select("INBOX")
            while True:
                status, messages = await client.search('UNSEEN')
                if status == 'OK' and messages[0]:
                
                    print(f"{len(messages)} nouveaux emails sur {email} !")
                    mail = await fetch_latest_email(client)
                    if mail:
                        print(f"Nouveau mail de {mail.from_email} à {mail.to_email} : {mail.subject}")
                        data = EmailAnalysisRequestData(email=mail, account=email)
                        await send_email_to_api(data)



                await asyncio.sleep(CHECK_INTERVAL)  # Ne bloque pas les autres tâches
    except Exception as e:
        print(f"Erreur pour {email} : {e}")
        active_tasks[email].cancel()
        del active_tasks[email]  # Supprimer la tâche de la liste active


async def monitor_accounts():
    """Surveille dynamiquement les comptes à surveiller"""
    global active_tasks

    while True:
        print("Mise à jour de la liste des comptes à surveiller...")
        accounts = await fetch_accounts()
        current_emails = set(active_tasks.keys())
        new_emails = {account.email for account in accounts}

        # Ajouter les nouveaux comptes
        for account in accounts:
            if account.email not in active_tasks:
                print(f"Ajout de {account.email} à la surveillance")
                task = asyncio.create_task(imap_listener(account))
                active_tasks[account.email] = task

        # Supprimer les comptes inactifs
        for email in current_emails - new_emails:
            print(f"Suppression de {email} de la surveillance")
            active_tasks[email].cancel()
            del active_tasks[email]

        await asyncio.sleep(CHECK_INTERVAL)  # Attendre avant la prochaine mise à jour

async def fetch_latest_email(client):
    """Fetches the latest unread email and extracts attachments if available"""
    try:
        status, messages = await client.search('UNSEEN')
        if status != 'OK' or not messages[0]:
            return

        latest_email_id = messages[-2].split()[-1].decode()
        status, msg_data = await client.fetch(latest_email_id, '(RFC822)')
        print('ho ho')
        if status != 'OK':
            return

        if not msg_data or not msg_data[0]:
            print("No message data available")
            return

        raw_email = msg_data[1]
        if not raw_email:
            print("No raw email content")
            return

        try:
            msg = email.message_from_bytes(raw_email, policy=policy.default)
        except Exception as e:
            print(f"Error parsing email: {e}")
            return

        sender = msg["from"]
        recipient = msg["to"]
        subject = msg["subject"]
        date_str = msg["date"]

        print("i was there too")
        sender_email = parseaddr(sender)[1]  # Extract only the email address
        recipient_email = parseaddr(recipient)[1]

        # Convert email date to timestamp
        timestamp = None
        if date_str:
            parsed_date = parsedate_tz(date_str)
            if parsed_date:
                timestamp = mktime_tz(parsed_date)

        body = ""
        attachments = []

        print('here i am')

        # Extract email content and attachments
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Extract plain text or HTML body
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")
                elif content_type == "text/html" and not body:
                    body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")

                # Extract attachments
                if part.get_filename():
                    filename = part.get_filename()
                    file_data = part.get_payload(decode=True)
                    attachments.append({"filename": filename, "data": file_data})
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors="ignore")

        # Convert HTML to text if necessary
        text_body = BeautifulSoup(body, "html.parser").get_text()

        print(f"Found {len(attachments)} attachment(s)")
        return Email(email_id=latest_email_id, from_email=sender_email, to_email=recipient_email, subject=subject, body=text_body, timestamp=datetime.fromtimestamp(timestamp), attachments=attachments)
    
    except Exception as e: 
        print(f"Error fetching email: {e}")

# 🚀 Lancer le programme
async def main():
    await monitor_accounts()

asyncio.run(main())