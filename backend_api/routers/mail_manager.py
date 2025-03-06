from fastapi import APIRouter, Request, HTTPException
from google_auth_oauthlib.flow import Flow
import webbrowser, json, imaplib, requests, base64


router = APIRouter()

# IMAP Login
#----------------------------------------------------------------------------------------------------------------------------
def imap_login(server: str, email: str, password: str):
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email, password)
        return {"message": "IMAP connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

router.post("/login/imap")
def login(server: str, email: str, password: str):
    return imap_login(server, email, password)
#----------------------------------------------------------------------------------------------------------------------------

# Gmail OAuth
#----------------------------------------------------------------------------------------------------------------------------
# TODO : Use user token instead of stored token

# TODO : Config file where we store env var 
# Company account -->   mail: hookshieldinc@gmail.com       password: !f5dA8e4$t64D5 
CLIENT_ID = "615748183428-4ooi03dcn37hgga691n34j2omsu0taoc.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://127.0.0.1:8000/gmail_callback"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Temporarily store the OAuth Flow instance
gmail_flow = Flow.from_client_config(
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
gmail_flow.redirect_uri = REDIRECT_URI

router.get("/login/gmail")
def gmail_login():
    """ Automatically opens the browser for OAuth authentication """
    auth_url, _ = gmail_flow.authorization_url(prompt="consent")
    
    # Open the browser automatically
    webbrowser.open(auth_url)
    
    return {"message": "Browser opened. Complete the authentication."}

router.get("/gmail_callback")
async def gmail_callback(request: Request):
    """ Retrieves the OAuth token after authentication and redirects the user """
    code = request.query_params.get("code")

    if not code:
        return {"error": "Missing OAuth code"}

    gmail_flow.fetch_token(code=code)
    credentials = gmail_flow.credentials

    try:
        with open("tokens.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Add new tokens
    data.update({"token": credentials.token})

    # Save the updated data in the JSON file
    with open("tokens.json", "w") as file:
        json.dump(data, file, indent=4)
    
    return {"message": "GMAIL connection successful, OAuth token stored in tokens.json"}

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

router.get("/gmail/webhook")
async def gmail_webhook(request: Request):
    """Receives new email notifications from Gmail (via Pub/Sub)"""
    data = await request.json()
    message_data = data.get("message", {}).get("data")

    if not message_data:
        return {"error": "No notification data"}

    decoded_data = base64.urlsafe_b64decode(message_data).decode("utf-8")
    print("Gmail Notification Received:", decoded_data)

    fetch_new_emails()

    return {"message": "Notification received"}

def fetch_new_emails():
    """Fetches the latest received emails"""
    try:
        with open("tokens.json", "r") as file:
            data = json.load(file)
            token = data.get("token")
            if not token:
                return {"error": "No OAuth token found"}
    except FileNotFoundError:
        return {"error": "tokens.json not found"}

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=1", headers=headers)

    if response.status_code == 200:
        email_id = response.json().get("messages", [{}])[0].get("id")

        email_response = requests.get(f"https://www.googleapis.com/gmail/v1/users/me/messages/{email_id}?format=full", headers=headers)

        if email_response.status_code == 200:
            email_data = email_response.json()
            headers_info = email_data.get("payload", {}).get("headers", [])

            subject = next((h["value"] for h in headers_info if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers_info if h["name"] == "From"), "Unknown Sender")

            # TODO : Send to AI Backend instead of printing
            print(f"New Email Received: {subject} from {sender}")

            return {"email_id": email_id, "subject": subject, "from": sender}

    return {"error": "Failed to retrieve emails"}
#----------------------------------------------------------------------------------------------------------------------------

# Outlook OAuth
# /!\ Need an account with a payment method and a free trial --> only for 1 Month /!\
#----------------------------------------------------------------------------------------------------------------------------
from fastapi import APIRouter, Request, HTTPException
import json, requests
from msal import ConfidentialClientApplication

router = APIRouter()

# TODO : Change with real values
# Outlook OAuth Configuration
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
TENANT_ID = "tenant_id" # Can use common instead of tenant_id if our outlook acc is not a company acc
REDIRECT_URI = "http://127.0.0.1:8000/outlook_callback"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]
TOKEN_FILE = "outlook_tokens.json" # TODO : Use the DB instead of a json file

router.get("/login/outlook")
def outlook_login():
    """Generates the Outlook OAuth login URL"""
    auth_url = f"{AUTHORITY}/oauth2/v2.0/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&response_mode=query&scope={' '.join(SCOPES)}"
    return {"auth_url": auth_url}

router.get("/outlook_callback")
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
