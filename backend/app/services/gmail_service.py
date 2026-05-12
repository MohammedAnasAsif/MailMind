from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.config import settings
import base64

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def get_google_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8000/api/gmail/callback"]
            }
        },
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/api/gmail/callback"
    )

def get_gmail_service(access_token: str, refresh_token: str):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    return build("gmail", "v1", credentials=creds)

def fetch_inbox_threads(access_token: str, refresh_token: str, max_results: int = 20):
    service = get_gmail_service(access_token, refresh_token)
    results = service.users().threads().list(
        userId="me",
        maxResults=max_results,
        q="is:inbox"
    ).execute()
    threads = results.get("threads", [])
    parsed = []
    for thread in threads:
        t = service.users().threads().get(
            userId="me",
            id=thread["id"],
            format="full"
        ).execute()
        messages = t.get("messages", [])
        if not messages:
            continue
        first_msg = messages[0]
        last_msg = messages[-1]
        headers = {h["name"]: h["value"] for h in first_msg["payload"]["headers"]}
        body = extract_body(last_msg["payload"])
        parsed.append({
            "thread_id": thread["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "sender": headers.get("From", ""),
            "snippet": t.get("snippet", ""),
            "body": body[:2000],
            "message_count": len(messages),
            "unread": "UNREAD" in first_msg.get("labelIds", [])
        })
    return parsed

def extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    body_data = payload.get("body", {}).get("data", "")
    if body_data:
        return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
    return ""
