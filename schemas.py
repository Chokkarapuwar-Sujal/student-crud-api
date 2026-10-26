from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class StudentCreate(BaseModel):
    name: str
    date_of_birth: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: str
    address: Optional[str] = None
    enrollment_date: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be empty.")
        if len(value) > 100:
            raise ValueError("Name must be 100 characters or fewer.")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: str) -> str:
        try:
            dob = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("date_of_birth must be in YYYY-MM-DD format.")
        if dob >= date.today():
            raise ValueError("date_of_birth must be in the past.")
        return value

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("enrollment_date must be in YYYY-MM-DD format.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            return None
        if len(value) > 20:
            raise ValueError("Phone must be 20 characters or fewer.")
        return value

    @field_validator("course")
    @classmethod
    def course_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Course must not be empty.")
        if len(value) > 100:
            raise ValueError("Course must be 100 characters or fewer.")
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value) > 300:
            raise ValueError("Address must be 300 characters or fewer.")
        return value

    @model_validator(mode="after")
    def require_contact_method(self):
        # at least one of email/phone must be provided
        if not self.email and not self.phone:
            raise ValueError(
                "At least one contact method (email or phone) is required."
            )
        return self


class StudentUpdate(BaseModel):
    """All fields optional - only provided fields get updated."""

    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Name must not be empty.")
            if len(value) > 100:
                raise ValueError("Name must be 100 characters or fewer.")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            try:
                dob = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("date_of_birth must be in YYYY-MM-DD format.")
            if dob >= date.today():
                raise ValueError("date_of_birth must be in the past.")
        return value

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_date(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "enrollment_date must be in YYYY-MM-DD format."
                )
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if len(value) > 20:
                raise ValueError("Phone must be 20 characters or fewer.")
        return value

    @field_validator("course")
    @classmethod
    def course_not_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Course must not be empty.")
            if len(value) > 100:
                raise ValueError("Course must be 100 characters or fewer.")
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value) > 300:
            raise ValueError("Address must be 300 characters or fewer.")
        return value


class StudentResponse(BaseModel):
    student_id: int
    name: str
    date_of_birth: str
    email: Optional[str] = None
    phone: Optional[str] = None
    course: str
    address: Optional[str] = None
    enrollment_date: str
