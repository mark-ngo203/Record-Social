from fastapi import APIRouter, Depends, HTTPException

from app.db.database import get_db
from app.exceptions.user_exceptions import DuplicateUsernameException, UserNotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user_dto import UserCreateRequest, UserUpdateRequest
from app.services.user_service import UserService


router = APIRouter()

@router.post("/", status_code=201)
def create_user(user: UserCreateRequest, db=Depends(get_db)):
    try:
        service = UserService(UserRepository(db))
        created_user = service.create_user(user)

        return created_user
    except DuplicateUsernameException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/{user_id}", status_code=200)
def get_user(user_id: int, db=Depends(get_db)):
    try:
        service = UserService(UserRepository(db))
        user = service.get_user(user_id)

        return user
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", status_code=200)
def update_user(user_id: int, user: UserUpdateRequest, db=Depends(get_db)):
    try:
        service = UserService(UserRepository(db))
        updated_user = service.update_user(user_id, user)

        return updated_user
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateUsernameException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db=Depends(get_db)):
    try:
        service = UserService(UserRepository(db))
        service.delete_user(user_id)

        return None
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
