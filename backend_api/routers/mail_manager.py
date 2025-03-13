from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
import webbrowser, json, imaplib, requests, base64, email, time
from starlette.responses import RedirectResponse
import time
from email import policy
from email.utils import parsedate_tz, mktime_tz
from bs4 import BeautifulSoup
from utils.analyse import Email, analyse_email, EmailAnalysis
from db.models import MailsInDb,EmailAccountinDB,UserInDB,EmailAccountTypeinDB
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from db.db import SessionLocal
from routers.auth import get_current_user
from utils.users import UserInfo,pwd_context
from typing import Annotated
from datetime import datetime

global running
running = False


router = APIRouter(tags=["MailManager"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# IMAP Login
#----------------------------------------------------------------------------------------------------------------------------
from imapclient import IMAPClient

def imap_login(server: str, email: str, password: str, db: Session):
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email, password)
        return True
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/login/imap")
def login(server: str, email: str, password: str,background_tasks: BackgroundTasks,user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db),):
    if imap_login(server, email, password, db):
        userinDB = db.query(UserInDB).filter(UserInDB.email == user.email).first()
        if userinDB:
            encrypted_password = pwd_context.hash(password)
            db.add(EmailAccountinDB(email=email, added_by=userinDB.id, account_type=1, imap_password=encrypted_password, imap_host=server,created_at=datetime.now()))
            db.commit()
            background_tasks.add_task(start_imap_listener, email, password, server,db)
            return {"message": "IMAP account added successfully"}

async def check_mail(email: Email, mail: str, client: IMAPClient,db: Session):
    try:
        email_analys = await analyse_email(email,mail,db)
        if email_analys.phishing_detected:
            client.move(mail, "Spam")
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

async def start_imap_listener(email: str, password: str, imap_server: str,db: Session):
    """Garde la connexion ouverte et vérifie les nouveaux emails"""
    global running
    running = True
    while running:
        try:
            with IMAPClient(imap_server) as client:
                client.login(email, password)
                client.select_folder("INBOX")
                
                while running:
                    messages = client.search("UNSEEN")
                    if messages:
                        print(f"📩 {len(messages)} new email(s)!")
                        mail = fetch_latest_email(client)
                        print(mail)
                        if mail:
                            asyncio.create_task(check_mail(mail, email, client,db))
                        
                    
                    await asyncio.sleep(5)  # Vérifie toutes les 5 secondes

        except Exception as e:
            print(f"Connection lost: {e}. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)  # Attente avant reconnexion

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

        return Email(from_email=sender, to_email=recipient, subject=subject, body=text_body, timestamp=datetime.fromtimestamp(timestamp))
    except Exception as e: 
        print(f"Error fetching email: {e}")

@router.post("/stop_imap_listener")
def stop_imap_listener():
    global running
    running = False
    return {"message": "IMAP listener stopped"}

#----------------------------------------------------------------------------------------------------------------------------

# Gmail OAuth
#----------------------------------------------------------------------------------------------------------------------------
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials

# TODO : Use user token instead of stored token

# TODO : Config file where we store env var 
# Company account -->   mail: hookshieldinc@gmail.com       password: !f5dA8e4$t64D5 
CLIENT_ID = "615748183428-4ooi03dcn37hgga691n34j2omsu0taoc.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://127.0.0.1:8000/gmail_callback"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Temporarily store the OAuth Flow instance
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=SCOPES
)
flow.redirect_uri = REDIRECT_URI

@router.get("/login/gmail")
def gmail_login():
    """ Automatically opens the browser for OAuth authentication """
    auth_url, _ = flow.authorization_url(prompt="consent")
    
    # Open the browser automatically
    webbrowser.open(auth_url)
    
    return {"message": "Browser opened. Complete the authentication."}

@router.get("/gmail_callback")
async def gmail_callback(request: Request, user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")

    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_in_db = db.query(UserInDB).filter(UserInDB.email == user.email).first()
    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found")

    gmail_type = db.query(EmailAccountTypeinDB).filter(EmailAccountTypeinDB.type_name == "Gmail").first()
    if not gmail_type:
        gmail_type = EmailAccountTypeinDB(type_name="Google")
        db.add(gmail_type)
        db.commit()
    db.add(EmailAccountinDB(
        email=user.email,
        added_by=user_in_db.id,
        account_type=gmail_type.id,
        imap_password=None,
        imap_host=None,
        token=credentials.token,
        created_at=datetime.now()
    ))
    db.commit()

    return RedirectResponse(url=f'http://localhost:8000/MailManager')

@router.get("/fetch_gmail")
async def fetch_gmail(user: Annotated[UserInfo, Depends(get_current_user)], db: Session = Depends(get_db)):
    # Fetch the email account from the database
    email_account = db.query(EmailAccountinDB).filter(EmailAccountinDB.email == user.email).first()
    if not email_account or not email_account.token:
        raise HTTPException(status_code=400, detail="OAuth token not found")

    credentials = Credentials(token=email_account.token)

    # Check if the token is expired and refresh it if necessary
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(GoogleRequest())
        # Update the token in the database
        email_account.token = credentials.token  # Store the new token string
        db.commit()

    # Set up the authorization header with the token
    headers = {"Authorization": f"Bearer {credentials.token}"}
    
    # Retrieve emails from Gmail API
    response = requests.get("https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=1", headers=headers)

    if response.status_code == 200:
        email_id = response.json().get("messages", [{}])[0].get("id")
        email_response = requests.get(f"https://www.googleapis.com/gmail/v1/users/me/messages/{email_id}?format=full", headers=headers)

        if email_response.status_code == 200:
            email_data = email_response.json()

            # TODO : Create a function to serialize every data structure of mails (imap vs gmail vs outlook) to match the analysis function
            email_analysis = await analyse_email(email_data, email_account.email, db)

            if email_analysis.phishing_detected:
                # Move the email to Spam (You would need to interact with the Gmail API to move it)
                requests.post(f"https://www.googleapis.com/gmail/v1/users/me/messages/{email_data['id']}/modify",
                            headers=headers,
                            json={"addLabelIds": ["SPAM"]})
                print(f"Email moved to Junk: {email_analysis.explanation}")

                # Save email analysis results into the database
                db.add(MailsInDb(
                    source=email_data['payload']['headers'][1]['value'],  # Sender's email address
                    recipient=email_account.email,  # Assuming the recipient is the logged-in user
                    subject=email_data['payload']['headers'][3]['value'],  # Subject
                    explanation=email_analysis.explanation,
                    email_body=email_data['snippet'],  # Body of the email
                    receive_date=datetime.fromtimestamp(email_data['internalDate'] / 1000),  # Convert from milliseconds
                    analyzed_date=datetime.now(),
                    is_phishing=email_analysis.phishing_detected,
                    blocked_date=datetime.now() if email_analysis.phishing_detected else None,
                    folder_id=1,  # Assuming "1" corresponds to a folder for phishing/spam
                    source_email=email_data['id']
                ))

                db.commit()
                db.refresh()

            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve emails")


            headers_info = email_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers_info if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers_info if h["name"] == "From"), "Unknown Sender")
            return {"email_id": email_id, "subject": subject, "from": sender}

    # If there was an error retrieving emails, raise an exception
    raise HTTPException(status_code=500, detail="Failed to retrieve emails")

def gmail_serialization():
    print("a")

# TODO : Test webhooks once we've set up a public address
# TODO : Modify function to be user-specific and add separation by recipient
def setup_gmail_webhook():
    """Configures Gmail push notifications via Cloud Pub/Sub"""
    try:
        with open("tokens.json", "r") as file:
            data = json.load(file)
            token = data.get("token")
            if not token:
                return {"error": "No OAuth token found"}
    except FileNotFoundError:
        return {"error": "tokens.json not found"}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    pubsub_topic = "projects/project-id/topics/topic-name"  # TODO : Change this

    body = {
        "labelIds": ["INBOX"],
        "topicName": pubsub_topic
    }

    response = requests.post(
        "https://www.googleapis.com/gmail/v1/users/me/watch", headers=headers, json=body
    )

    return response.json()

@router.get("/gmail/webhook")
async def gmail_webhook(request: Request):
    """Receives new email notifications from Gmail (via Pub/Sub)"""
    data = await request.json()
    message_data = data.get("message", {}).get("data")

    if not message_data:
        return {"error": "No notification data"}

    decoded_data = base64.urlsafe_b64decode(message_data).decode("utf-8")
    print("Gmail Notification Received:", decoded_data)

    fetch_gmail()

    return {"message": "Notification received"}
#----------------------------------------------------------------------------------------------------------------------------

# Outlook OAuth
# /!\ Need an account with a payment method and a free trial --> only for 1 Month /!\
#----------------------------------------------------------------------------------------------------------------------------
from msal import ConfidentialClientApplication

# TODO : Change with real values + Config/env file with all of the ID/Secret/URI/etc. stuff
# Outlook OAuth Configuration
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
TENANT_ID = "tenant_id" # Can use common instead of tenant_id if our outlook acc is not a company acc
REDIRECT_URI = "http://127.0.0.1:8000/outlook_callback"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]
TOKEN_FILE = "outlook_tokens.json" # TODO : Use the DB instead of a json file

@router.get("/login/outlook")
def outlook_login():
    """Generates the Outlook OAuth login URL"""
    auth_url = f"{AUTHORITY}/oauth2/v2.0/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&response_mode=query&scope={' '.join(SCOPES)}"
    return {"auth_url": auth_url}

@router.get("/outlook_callback")
def outlook_callback(request: Request):
    """Handles OAuth callback and stores token"""
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing OAuth code"}

    token_url = f"{AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": " ".join(SCOPES),
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    if "access_token" in token_data:
        with open(TOKEN_FILE, "w") as token_file:
            json.dump(token_data, token_file, indent=4)
        return {"message": "Outlook OAuth token stored successfully"}
    else:
        return {"error": token_data}
#----------------------------------------------------------------------------------------------------------------------------
