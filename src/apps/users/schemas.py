from ninja import Schema
from pydantic import EmailStr, model_validator, Field


class SignUpSchema(Schema):
    email: EmailStr
    password: str = Field(..., min_length=8, write_only=True)
    password_confirm: str = Field(..., write_only=True)
    first_name: str = ""
    last_name: str = ""

    @model_validator(mode="after")
    def check_passwords_match(self) -> "SignUpSchema":
        pw1 = self.password
        pw2 = self.password_confirm
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Passwords do not match")
        return self


# --- Output Schema ---
class UserSchema(Schema):
    """Schema for representing a user's public data."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
