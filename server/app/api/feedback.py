from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Feedback
from ..schemas import FeedbackRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/feedback")
def send_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    fb = Feedback(message=request.message)
    db.add(fb)
    db.commit()
    return {"status": "saved"}