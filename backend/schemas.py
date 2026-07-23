from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: bool
    created_at: datetime
    class Config: from_attributes = True

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(default=None, min_length=8, max_length=128)

class KundliRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    gender: str = Field(pattern="^(Male|Female|Other)$")
    birth_date: date
    birth_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    place_of_birth: str = Field(min_length=2, max_length=160)
    country: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    relationship_status: str = Field(min_length=2, max_length=60)
    occupation: Optional[str] = Field(default=None, max_length=120)
    questions: Optional[str] = Field(default=None, max_length=2000)
    @field_validator("birth_date")
    @classmethod
    def birth_date_is_past(cls, value):
        if value >= date.today(): raise ValueError("Birth date must be in the past")
        return value

class ReportOut(BaseModel):
    id: int
    full_name: str
    birth_date: date
    birth_time: str
    city: str
    content: str
    created_at: datetime
    class Config: from_attributes = True

class AnalyticsOut(BaseModel):
    users: int
    reports: int
    reports_today: int
