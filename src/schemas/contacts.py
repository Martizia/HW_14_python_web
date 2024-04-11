from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    lastname: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str
    birthday: date
    notes: str = Field(max_length=250)
    favourite: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    favourite: bool


class ContactStatusUpdate(BaseModel):
    favourite: bool


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: date
    notes: str
    favourite: bool
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True
