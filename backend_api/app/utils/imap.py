from sqlalchemy.orm import Session
from config import cipher
from imapclient import IMAPClient
from email.utils import parsedate_tz, mktime_tz
from email import policy
from bs4 import BeautifulSoup
import imaplib
from datetime import datetime
from db.models import MailsInDb, EmailAccountinDB, UserStatsinDB, GlobalStatsinDB
import email
import asyncio
from email.utils import parseaddr, parsedate_tz, mktime_tz
from utils.analyse import Email, analyse_email, EmailAnalysis
from db.db import SessionLocal

def get_client(email: str,db: Session):
    """Récupère le client IMAP pour un compte spécifique."""
    email_account = db.query(EmailAccountinDB).filter(EmailAccountinDB.email == email).first()
    if not email_account:
        raise ValueError("Compte email non trouvé dans la base de données")

    try:
        password = cipher.decrypt(email_account.imap_password.encode()).decode()
        client = imaplib.IMAP4_SSL(email_account.imap_host)
        client.login(email, password)
        return client
    except Exception as e:
        raise ValueError(f"Erreur lors de la connexion au compte IMAP: {e}")


async def check_mail(email: Email, mail: str):
    try:
        db = SessionLocal()
        email_analys = await analyse_email(email, mail, db)
        spam_folder = "INBOX/HOOKSHIELD_SPAM"

        client= get_client(mail, db)

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
        print(f"Error checking email: {e}")

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
            
            fetch_email_by_uid(client, uid)
            
            client.uid('COPY', str(uid), 'INBOX')
            client.uid('STORE', str(uid), '+FLAGS', '\\Deleted')
            client.expunge()
            print(f"Message {uid} traité avec succès.")
            
            new_uid = get_new_uid_inbox(client)
            if not new_uid:
                raise ValueError(f"Impossible d'obtenir un nouveau UID pour le message {uid}")
            
            try:
                existing_mail = db.query(MailsInDb).filter_by(id=uid).first()
                existing_mail.id = new_uid
                db.commit()
                
                existing_entry = db.query(TicketInDB).filter_by(mail_uid=uid).first()
                existing_entry.last_modification_at = datetime.now()
                db.commit()
            except Exception as db_error:
                print(f"Erreur lors de la mise à jour en base : {db_error}")

    except imaplib.IMAP4.error as e:
        # Gestion des erreurs spécifiques à IMAP4
        print(f"Erreur IMAP avec le message {uid} : {e}")

    except Exception as e:
        # Gestion des erreurs générales
        print(f"Erreur inattendue lors du traitement du message {uid} : {e}")

