from app.models import UserModel
from app.auth import AuthService

class UserService:
    @staticmethod
    def get_all():
        return UserModel.get_all()

    @staticmethod
    def get_by_id(user_id: int):
        return UserModel.get_by_id(user_id)

    @staticmethod
    def create(username: str, password: str, role_id: int):
        hashed = AuthService.hash_password(password)
        return UserModel.create(username=username, password=hashed, role_id=role_id)

    @staticmethod
    def update(user_id: int, username: str = None, role_id: int = None):
        return UserModel.update(user_id=user_id, username=username, role_id=role_id)

    @staticmethod
    def delete(user_id: int):
        return UserModel.soft_delete(user_id)
