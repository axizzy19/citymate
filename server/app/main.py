from fastapi import FastAPI
from .database import Base, engine
from .api import cities, federated, feedback

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CityMate Federated Server")

app.include_router(cities.router)
app.include_router(federated.router)
app.include_router(feedback.router)