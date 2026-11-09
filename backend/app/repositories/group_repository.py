from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.group_user import GroupUser
from app.schemas.group_dto import (
    GroupAddUserRequest,
    GroupCreateRequest,
    GroupUpdateRequest,
)


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: int, group_model: GroupCreateRequest) -> Group:

        db_group = Group(
            name = group_model.name,
            owner_id = owner_id,
            max_members = group_model.max_members,
            album_event_duration = group_model.album_event_duration,
        )

        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)

        return db_group

    def get_by_id(self, group_id: int) -> Group:
        group = self.db.query(Group).filter(Group.id == group_id).one()

        return group

    def update(self, group_id: int, group_data: GroupUpdateRequest) -> Group:
        db_group = self.get_by_id(group_id)

        update_data = group_data.model_dump(exclude_unset=True, exclude={"id", "user_id"})

        # The DTO's new_owner_id maps to the owner_id column
        if "new_owner_id" in update_data:
            update_data["owner_id"] = update_data.pop("new_owner_id")

        for key, value in update_data.items():
            setattr(db_group, key, value)

        self.db.commit()
        self.db.refresh(db_group)

        return db_group

    def delete(self, group_id: int) -> bool:
        db_group = self.get_by_id(group_id)

        self.db.delete(db_group)
        self.db.commit()

        return True

    def add_user(self, group_id: int, user_data: GroupAddUserRequest) -> GroupUser:
        db_group_user = GroupUser(
            group_id = group_id,
            user_id = user_data.add_user_id,
            role = user_data.role,
        )

        self.db.add(db_group_user)
        self.db.commit()
        self.db.refresh(db_group_user)

        return db_group_user
