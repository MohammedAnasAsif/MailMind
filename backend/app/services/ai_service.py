from groq import Groq
from app.config import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)

def classify_email(subject: str, sender: str, body: str) -> dict:
    prompt = f"""You are an email classification assistant. Analyze this email and return a JSON response.

Email Details:
Subject: {subject}
From: {sender}
Body: {body[:1500]}

Classify this email and respond with ONLY a JSON object in this exact format:
{{
    "category": "urgent|action_needed|fyi|promotional|spam",
    "priority": "high|medium|low",
    "reasoning": "one sentence explanation",
    "requires_reply": true|false,
    "sentiment": "positive|neutral|negative"
}}

Categories:
- urgent: needs immediate attention (deadlines, emergencies, time-sensitive)
- action_needed: requires a response or action but not urgent
- fyi: informational only, no action needed
- promotional: marketing, newsletters, job alerts
- spam: unwanted or suspicious email"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200
    )
    
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except:
        return {
            "category": "fyi",
            "priority": "low", 
            "reasoning": "Could not classify",
            "requires_reply": False,
            "sentiment": "neutral"
        }

def draft_reply(subject: str, sender: str, body: str, tone: str = "professional") -> str:
    prompt = f"""You are an expert email assistant. Draft a reply to this email.

Email Details:
Subject: {subject}
From: {sender}
Body: {body[:2000]}

Write a {tone} reply that:
- Directly addresses the email content
- Is concise (3-5 sentences max)
- Sounds natural and human
- Does not include subject line
- Does not include "Dear" or overly formal openers

Reply only with the email body text, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    
    return response.choices[0].message.content.strip()

def process_threads(threads: list) -> list:
    processed = []
    for thread in threads:
        classification = classify_email(
            thread.get("subject", ""),
            thread.get("sender", ""),
            thread.get("body", "") or thread.get("snippet", "")
        )
        
        draft = None
        if classification.get("requires_reply"):
            draft = draft_reply(
                thread.get("subject", ""),
                thread.get("sender", ""),
                thread.get("body", "") or thread.get("snippet", "")
            )
        
        processed.append({
            **thread,
            "classification": classification,
            "draft_reply": draft
        })
    
    return processed
