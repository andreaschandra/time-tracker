import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    clients = relationship("Client", back_populates="owner", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="clients")
    time_entries = relationship("TimeEntry", back_populates="client", cascade="all, delete-orphan")


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    date = Column(String, nullable=False)
    hours = Column(Float, nullable=False)
    note = Column(Text, default="")

    client = relationship("Client", back_populates="time_entries")
