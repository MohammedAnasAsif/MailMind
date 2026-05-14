from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.config import settings
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def send_email(
    access_token: str,
    refresh_token: str,
    to: str,
    subject: str,
    body: str,
    thread_id: str = None
) -> dict:
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    
    service = build("gmail", "v1", credentials=creds)
    
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    message.attach(MIMEText(body, "plain"))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    send_body = {"raw": raw}
    if thread_id:
        send_body["threadId"] = thread_id
    
    sent = service.users().messages().send(
        userId="me",
        body=send_body
    ).execute()
    
    return {
        "message_id": sent["id"],
        "thread_id": sent.get("threadId"),
        "status": "sent"
    }
