from sqlalchemy.orm import Session

from app.schemas.user_dto import UserCreateRequest, UserUpdateRequest
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_model: UserCreateRequest) -> User:

        db_user = User(username = user_model.username)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).one()

        return user

    def update(self, user_id: int, user_data: UserUpdateRequest) -> User:
        db_user = self.get_by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)

        self.db.delete(db_user)
        self.db.commit()

        return True
