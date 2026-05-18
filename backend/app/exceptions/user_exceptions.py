class DuplicateUsernameException(Exception):
    def __init__(self, username: str):
        self.username = username
        self.message = f"Username '{username}' already exists."
        super().__init__(self.message)

class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")