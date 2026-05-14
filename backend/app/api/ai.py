from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.gmail_service import fetch_inbox_threads
from app.services.ai_service import classify_email, draft_reply, process_threads
from app.services.send_service import send_email
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ClassifyRequest(BaseModel):
    subject: str
    sender: str
    body: str

class DraftRequest(BaseModel):
    subject: str
    sender: str
    body: str
    tone: str = "professional"

class SendRequest(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None

class ProcessAndDraftRequest(BaseModel):
    thread_id: str
    subject: str
    sender: str
    body: str
    tone: str = "professional"

@router.post("/classify")
def classify_single(
    request: ClassifyRequest,
    current_user: User = Depends(get_current_user)
):
    result = classify_email(request.subject, request.sender, request.body)
    return result

@router.post("/draft")
def draft_single(
    request: DraftRequest,
    current_user: User = Depends(get_current_user)
):
    draft = draft_reply(request.subject, request.sender, request.body, request.tone)
    return {"draft": draft}

@router.post("/send")
def send_reply(
    request: SendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=400,
            detail="Gmail not connected. Call /api/gmail/auth first."
        )
    
    result = send_email(
        current_user.google_access_token,
        current_user.google_refresh_token,
        request.to,
        request.subject,
        request.body,
        request.thread_id
    )
    
    current_user.emails_processed_this_month += 1
    db.commit()
    
    return result

@router.get("/process-inbox")
def process_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 5
):
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=400,
            detail="Gmail not connected. Call /api/gmail/auth first."
        )
    
    threads = fetch_inbox_threads(
        current_user.google_access_token,
        current_user.google_refresh_token,
        max_results=limit
    )
    
    processed = process_threads(threads)
    
    urgent = [t for t in processed if t["classification"]["category"] == "urgent"]
    action_needed = [t for t in processed if t["classification"]["category"] == "action_needed"]
    fyi = [t for t in processed if t["classification"]["category"] == "fyi"]
    promotional = [t for t in processed if t["classification"]["category"] in ["promotional", "spam"]]
    
    return {
        "total": len(processed),
        "summary": {
            "urgent": len(urgent),
            "action_needed": len(action_needed),
            "fyi": len(fyi),
            "promotional": len(promotional)
        },
        "threads": processed
    }
