from fastapi import APIRouter
router = APIRouter()

@router.get("/inbox")
def get_inbox():
    return {"message": "Gmail integration coming in Day 3"}
