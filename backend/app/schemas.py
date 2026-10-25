from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool
    full_name: str

class VehicleCreate(BaseModel):
    make: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0, le=1_000_000_000)
    quantity: int = Field(ge=0, le=1_000_000)
    description: str = Field(default="", max_length=1000)
    image_url: str = Field(default="", max_length=1000)

    @field_validator("make", "model", "category")
    @classmethod
    def non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be blank")
        return value.strip()

class VehicleUpdate(BaseModel):
    make: str | None = Field(default=None, min_length=1, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    price: float | None = Field(default=None, ge=0, le=1_000_000_000)
    quantity: int | None = Field(default=None, ge=0, le=1_000_000)
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)

class QuantityRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=1000)

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    make: str
    model: str
    category: str
    price: float
    quantity: int
    description: str
    image_url: str
