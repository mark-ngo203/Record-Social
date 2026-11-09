class DuplicateGroupNameException(Exception):
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.message = f"Group name '{group_name}' already exists."
        super().__init__(self.message)

class GroupNotFoundError(Exception):
    def __init__(self, group_id: int):
        self.group_id = group_id
        super().__init__(f"Group with id {group_id} not found")
