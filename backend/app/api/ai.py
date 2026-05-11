from fastapi import APIRouter
router = APIRouter()

@router.get("/classify")
def classify():
    return {"message": "AI classification coming in Day 5"}
