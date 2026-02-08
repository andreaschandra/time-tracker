from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientCreate(BaseModel):
    name: str
    rate: float


class ClientOut(BaseModel):
    id: str
    name: str
    rate: float
    total_hours: float = 0.0


class TimeEntryCreate(BaseModel):
    date: str
    hours: float
    note: str = ""

    @field_validator("hours")
    @classmethod
    def hours_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Hours must be greater than 0")
        return v


class TimeEntryOut(BaseModel):
    id: str
    client_id: str
    date: str
    hours: float
    note: str
