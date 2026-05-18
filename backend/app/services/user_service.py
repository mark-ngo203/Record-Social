from typing import Optional
import logging

from sqlalchemy.exc import IntegrityError, NoResultFound

from app.exceptions.user_exceptions import DuplicateUsernameException, UserNotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user_dto import UserCreateRequest, UserResponse, UserUpdateRequest, UserUpdateResponse


logger = logging.getLogger("user_service")

class UserService():
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, user_dto: UserCreateRequest) -> Optional[UserResponse]:
        try:
            user = self.repo.create(user_dto)
            logger.info("Created user", extra={"user id": user.id, "username": user.username, "created at": user.created_at})
            user_response = UserResponse.model_validate(user)

            return user_response.model_validate(user)
        except IntegrityError as e:
            self.repo.db.rollback()
            logger.warning("Username already exists", extra={"error": str(e)})
            raise DuplicateUsernameException(user_dto.username)

    def get_user(self, user_id: int) -> Optional[UserResponse]:
        try:
            user = self.repo.get_by_id(user_id)
            logger.info("Retrieved user", extra={"user id": user.id, "username": user.username, "created at": user.created_at})
            user_response = UserResponse.model_validate(user)

            return user_response
        except NoResultFound:
            logger.warning("User not found", extra={"user id": user_id})
            raise UserNotFoundError(user_id)

    def update_user(self, user_id: int, user_dto: UserUpdateRequest) -> Optional[UserUpdateResponse]:
        try:
            user = self.repo.update(user_id, user_dto)
            logger.info("Updated user", extra={"user id": user.id, "username": user.username, "updated at": user.updated_at})
            user_response = UserUpdateResponse.model_validate(user)

            return user_response
        except NoResultFound:
            logger.warning("User not found for update", extra={"user id": user_id})
            raise UserNotFoundError(user_id)
        except IntegrityError as e:
            self.repo.db.rollback()
            logger.warning("Username already exists on update", extra={"error": str(e)})
            raise DuplicateUsernameException(user_dto.username)

    def delete_user(self, user_id: int) -> bool:
        try:
            deleted = self.repo.delete(user_id)
            logger.info("Deleted user", extra={"user id": user_id, "deleted": deleted})
            return deleted
        except NoResultFound:
            logger.warning("User not found for deletion", extra={"user id": user_id})
            raise UserNotFoundError(user_id)
