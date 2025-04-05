from sqlalchemy.orm import Session
from config import cipher
from email.utils import parsedate_tz, mktime_tz
from email import policy
from bs4 import BeautifulSoup
import imaplib
from datetime import datetime
from db.models import MailsInDb, EmailAccountinDB, UserStatsinDB, GlobalStatsinDB, TicketInDB
import email
import asyncio
from email.utils import parseaddr, parsedate_tz, mktime_tz
from utils.analyse import Email, analyse_email, EmailAnalysis

tasks = {}

async def start_imap_listener(email: str, password: str, imap_server: str, db):
    """Garde la connexion IMAP ouverte et surveille les nouveaux emails."""
    while email in tasks:  # Vérifie si la tâche est encore active
        try:
            with imaplib.IMAP4_SSL(imap_server) as client:
                client.login(email, password)
                client.select("INBOX", False)

                while email in tasks:
                    status, messages = client.search(None, 'UNSEEN')
                    if status == 'OK' and messages[0]:
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



async def check_mail(email: Email, mail: str, client: imaplib.IMAP4_SSL, db: Session):
    try:
        email_analys = await analyse_email(email, mail, db)
        spam_folder = "INBOX/HOOKSHIELD_SPAM"

        # Vérifier si le dossier existe, sinon le créer
        client.select('INBOX')
        result, data = client.list()
        folders = [folder.decode().split('"')[-2].strip() for folder in data]

        if spam_folder not in folders:
            client.create(spam_folder)
        # Déplacer les e-mails dans le dossier approprié
        email_id = str(email.email_id)
        if email_analys.phishing_detected:
            client.store(email_id, '+FLAGS', '\\Seen')
            client.copy(email_id, spam_folder)
            client.store(email_id, '+FLAGS', '\\Deleted')
            client.expunge()
            
            # Récupérer le nouvel ID de l'email
            email.email_id=get_new_uid(client)
            
            db.query(UserStatsinDB).filter(UserStatsinDB.user_id == email_analys.user_account_id).update({
                UserStatsinDB.mails_blocked: UserStatsinDB.mails_blocked + 1
            })
            global_stats = db.query(GlobalStatsinDB).first()
            if global_stats:
                global_stats.total_mails_blocked += 1
        else:
            db.query(UserStatsinDB).filter(UserStatsinDB.user_id == email_analys.user_account_id).update({
                UserStatsinDB.mail_authentic: UserStatsinDB.mail_authentic + 1
            })
            global_stats = db.query(GlobalStatsinDB).first()
            if global_stats:
                global_stats.total_mail_authentic += 1

        db.add(MailsInDb(
            id=int(email.email_id.strip('{}')) if isinstance(email.email_id, str) else email.email_id,
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

        # Mise à jour du nombre total de mails analysés
        global_stats = db.query(GlobalStatsinDB).first()
        if global_stats:
            global_stats.total_mail_analyzed += 1

        db.query(UserStatsinDB).filter(UserStatsinDB.user_id == email_analys.user_account_id).update({
            UserStatsinDB.mail_analyzed: UserStatsinDB.mail_analyzed + 1
        })

        db.commit()
        fetch_email_by_uid(client, email.email_id)

    except Exception as e:
        print(f"Error analysing email: {e}")


def fetch_latest_email(client):
    """Fetches the latest unread email and extracts attachments if available"""
    try:
        status, messages = client.search(None, 'UNSEEN')
        if status != 'OK' or not messages[0]:
            return

        latest_email_id = messages[-1].split()[-1]
        status, msg_data = client.fetch(latest_email_id, '(RFC822)')
        if status != 'OK':
            return

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email, policy=policy.default)

        sender = msg["from"]
        recipient = msg["to"]
        subject = msg["subject"]
        date_str = msg["date"]

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


def get_email_imap_accounts(db: Session):
    email_imap_accounts = db.query(EmailAccountinDB).filter(EmailAccountinDB.account_type == 1).all()
    return email_imap_accounts

def get_new_uid(client: imaplib.IMAP4_SSL) -> str:
    try:
        # Sélectionner la boîte mail
        client.select('INBOX/HOOKSHIELD_SPAM')
        
        # Rechercher tous les emails dans la boîte
        result, email_ids = client.uid('search', None, 'ALL')
        
        if result != 'OK' or not email_ids[0]:
            print("Aucun email trouvé.")
            return ""
        
        # Obtenir l'ID du dernier email
        latest_email_uid = email_ids[0].split()[-1].decode()
        
        print("UID du dernier email :", latest_email_uid)
        return latest_email_uid
    
    except Exception as e:
        print(f"Erreur: {e}")
        return ""
    
def get_new_uid_inbox(client: imaplib.IMAP4_SSL) -> str:
    try:
        # Sélectionner la boîte mail
        client.select('INBOX')
        
        # Rechercher tous les emails dans la boîte
        result, email_ids = client.uid('search', None, 'ALL')
        
        if result != 'OK' or not email_ids[0]:
            print("Aucun email trouvé.")
            return ""
        
        # Obtenir l'ID du dernier email
        latest_email_uid = email_ids[0].split()[-1].decode()
        
        print("UID du dernier email :", latest_email_uid)
        return latest_email_uid
    
    except Exception as e:
        print(f"Erreur: {e}")
        return ""
    
def fetch_email_by_uid(client: imaplib.IMAP4_SSL, uid: str) -> str:
    try:
        if not uid.isdigit():
            print("UID invalide. UID is ", uid)
            return ""

        client.select('INBOX/HOOKSHIELD_SPAM')
        result, msg_data = client.uid('fetch', uid, '(RFC822)')
        
        if result != 'OK' or not msg_data or not any(isinstance(part, tuple) for part in msg_data):
            print("Échec lors de la récupération de l'email.")
            return ""
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1], policy=policy.default)
                print(f"Sujet: {msg['subject']}")
                print(f"De: {msg['from']}")
                print(f"À: {msg['to']}")
                print("Contenu:")
                
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            email_body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                            print(email_body)
                            return email_body
                else:
                    email_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
                    print(email_body)
                    return email_body
        
    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
        return ""
    except ValueError as e:
        print(f"Value error: {e}")
        return ""
    
def send_email_to_inbox(email: str, password: str, imap_server: str, db: Session, uid: str):
    print("The variables are ", email, password, imap_server)
    try:
        with imaplib.IMAP4_SSL(imap_server) as client:
            client.login(email, password)
            client.select("INBOX/HOOKSHIELD_SPAM")
            print("client selected the box INBOX/HOOKSHIELD_SPAM")
            
            fetch_email_by_uid(client, uid)
            
            client.uid('COPY', str(uid), 'INBOX')
            print("copy to INBOX")
            client.uid('STORE', str(uid), '+FLAGS', '\\Deleted')
            print("FLAG deleted")
            client.expunge()
            print("expunge")
            print(f"Message {uid} traité avec succès.")
            
            new_uid = get_new_uid_inbox(client)
            if not new_uid:
                raise ValueError(f"Impossible d'obtenir un nouveau UID pour le message {uid}")
            
            try:
                existing_mail = db.query(MailsInDb).filter_by(id=uid).first()
                existing_mail.id = new_uid
                db.commit()
                print("Email modifié dans la DB")
                
                existing_entry = db.query(TicketInDB).filter_by(mail_uid=uid).first()
                existing_entry.last_modification_at = datetime.now()
                db.commit()
                print("Ticket modifié dans la DB")
            except Exception as db_error:
                print(f"Erreur lors de la mise à jour en base : {db_error}")

    except imaplib.IMAP4.error as e:
        # Gestion des erreurs spécifiques à IMAP4
        print(f"Erreur IMAP avec le message {uid} : {e}")

    except Exception as e:
        # Gestion des erreurs générales
        print(f"Erreur inattendue lors du traitement du message {uid} : {e}")

