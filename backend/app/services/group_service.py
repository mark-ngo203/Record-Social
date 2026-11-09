import logging

from sqlalchemy.exc import IntegrityError, NoResultFound

from app.exceptions.group_exceptions import DuplicateGroupNameException, GroupNotFoundError
from app.repositories.group_repository import GroupRepository
from app.schemas.group_dto import (
    GroupCreateRequest,
    GroupCreateResponse,
    GroupResponse,
)

logger = logging.getLogger("group_service")

class GroupService:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    def create_group(self, user_id: int, group_dto: GroupCreateRequest) -> GroupCreateResponse:
        try:
            group = self.repo.create(user_id, group_dto)
            logger.info("Created group", extra={"group id": group.id, "group name": group.name, "owner id": group.owner_id, "created at": group.created_at})
            group_response = GroupCreateResponse.model_validate(group)

            return group_response
        except IntegrityError as e:
            self.repo.db.rollback()
            logger.warning("Group name already exists", extra={"error": str(e)})
            raise DuplicateGroupNameException(group_dto.name)

    def get_group(self, group_id: int) -> GroupResponse:
        try:
            group = self.repo.get_by_id(group_id)
            logger.info("Retrieved group", extra={"group id": group.id, "group name": group.name, "owner id": group.owner_id, "created at": group.created_at})
            group_response = GroupResponse.model_validate(group)

            return group_response
        except NoResultFound:
            logger.warning("Group not found", extra={"group id": group_id})
            raise GroupNotFoundError(group_id)
