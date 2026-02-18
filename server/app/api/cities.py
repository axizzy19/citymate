from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import City
from ..schemas import CityResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/cities/{city_name}", response_model=CityResponse)
def get_city(city_name: str, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.name == city_name).first()
    return city