from fastapi import APIRouter
from ..schemas import GradientUpdate
from ..services.aggregation import aggregate_gradients
from ..services.model_store import get_global_model

router = APIRouter()

@router.post("/federated/update")
def receive_gradients(update: GradientUpdate):
    aggregate_gradients(update.gradients)
    return {"status": "gradients received"}


@router.get("/federated/model")
def download_model():
    model = get_global_model()
    return {"model": model}