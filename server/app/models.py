from sqlalchemy import Column, Integer, String, Text
from .database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    message = Column(Text)


class GlobalModel(Base):
    __tablename__ = "global_model"

    id = Column(Integer, primary_key=True)
    version = Column(String)
    path = Column(String)