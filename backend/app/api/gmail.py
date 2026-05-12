from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.gmail_service import get_google_flow, fetch_inbox_threads

router = APIRouter()

@router.get("/auth")
def gmail_auth(current_user: User = Depends(get_current_user)):
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=str(current_user.id)
    )
    return {"auth_url": auth_url}

@router.get("/callback")
def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    flow = get_google_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    user = db.query(User).filter(User.id == int(state)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.google_access_token = credentials.token
    user.google_refresh_token = credentials.refresh_token
    db.commit()
    return {"message": "Gmail connected successfully", "email": user.email}

@router.get("/inbox")
def get_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=400,
            detail="Gmail not connected. Call /api/gmail/auth first."
        )
    threads = fetch_inbox_threads(
        current_user.google_access_token,
        current_user.google_refresh_token
    )
    return {"threads": threads, "count": len(threads)}
