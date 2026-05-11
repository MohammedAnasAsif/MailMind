from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, gmail, ai
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MailMind API",
    description="AI-powered email assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(gmail.router, prefix="/api/gmail", tags=["gmail"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
def root():
    return {"status": "MailMind API is running"}
