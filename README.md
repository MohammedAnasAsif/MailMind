# MailMind — AI Email Assistant

> Connect your Gmail → AI reads, categorizes, and drafts replies. Flags urgent threads. Saves 2 hours a day.

## Tech Stack
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **AI:** OpenAI GPT-4o
- **Auth:** JWT + Google OAuth2
- **Payments:** Stripe
- **Frontend:** React 18, Tailwind CSS
- **Deployment:** Railway (backend) + Vercel (frontend)

## Features
- Gmail OAuth integration — read and send emails
- AI-powered email categorization (urgent / action-needed / FYI / promo)
- One-click AI reply drafting with tone control
- Free tier (50 emails/month) + Pro plan via Stripe

## Local Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Status
🚧 Active development — Day 1
