from pydantic import BaseModel

class CityResponse(BaseModel):
    name: str
    description: str


class GradientUpdate(BaseModel):
    device_id: str
    gradients: list


class FeedbackRequest(BaseModel):
    message: str