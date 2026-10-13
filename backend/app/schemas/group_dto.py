from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GroupCreateRequest(BaseModel):
    name: str = Field(min_length=5, max_length=20)
    max_members: int = Field(ge=1, le=10)
    album_event_duration: Literal["weekly", "bi-weekly", "monthly"]

class GroupCreateResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    max_members: int
    album_event_duration: Literal["weekly", "bi-weekly", "monthly"]
    created_at: datetime

    model_config = {"from_attributes": True}

class GroupUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=5, max_length=20)
    new_owner_id: int | None = None
    max_members: int | None = Field(default=None, ge=1, le=10)
    album_event_duration: Literal["weekly", "bi-weekly", "monthly"] | None = None

class GroupUpdateResponse(BaseModel):
    id: int
    name: str | None = None
    new_owner_id: int | None = None
    max_members: int | None = None
    album_event_duration: Literal["weekly", "bi-weekly", "monthly"] | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}

class GroupDeleteResponse(BaseModel):
    id: int
    deleted_at: datetime

    model_config = {"from_attributes": True}

class GroupAddUserRequest(BaseModel):
    add_user_id: int
    role: Literal["admin", "member"]

class GroupAddUserResponse(BaseModel):
    id: int
    add_user_id: int
    role: Literal["admin", "member"]
    added_at: datetime

    model_config = {"from_attributes": True}

class GroupUpdateUserRoleRequest(BaseModel):
    update_user_id: int
    role: Literal["owner", "admin", "member"]

class GroupUpdateUserRoleResponse(BaseModel):
    id: int
    update_user_id: int
    role: Literal["owner", "admin", "member"]
    updated_at: datetime

    model_config = {"from_attributes": True}

class GroupRemoveUserRequest(BaseModel):
    remove_user_id: int
    reason: str

class GroupRemoveUserResponse(BaseModel):
    id: int
    remove_user_id: int
    reason: str
    removed_at: datetime

    model_config = {"from_attributes": True}
