from pydantic import BaseModel, Field
from datetime import datetime


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)

class UserUpdateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    # Look into class attributes to match with DTO
    model_config = {"from_attributes": True}

class UserUpdateResponse(BaseModel):
    id: int
    username: str
    updated_at: datetime

    model_config = {"from_attributes": True}
