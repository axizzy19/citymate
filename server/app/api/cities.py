from fastapi import APIRouter
from ..services.restcountries import get_country_info

router = APIRouter()


@router.get("/country/{country_name}")
def country_info(country_name: str):

    data = get_country_info(country_name)

    if not data:
        return {"error": "country not found"}

    return data