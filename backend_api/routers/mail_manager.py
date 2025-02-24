from fastapi import APIRouter, Request, HTTPException
from google_auth_oauthlib.flow import Flow
import webbrowser, json, imaplib


router = APIRouter()

# IMAP Login
#----------------------------------------------------------------------------------------------------------------------------
# Does not seem to be working atm ??????
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
#----------------------------------------------------------------------------------------------------------------------------

# Outlook OAuth
#----------------------------------------------------------------------------------------------------------------------------
# TODO
#----------------------------------------------------------------------------------------------------------------------------
