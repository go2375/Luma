from app.models import UserModel

class UserService:
    @staticmethod
    def get_all():
        return UserModel.get_all()

    @staticmethod
    def get_by_id(user_id: int):
        return UserModel.get_by_id(user_id)

    @staticmethod
    def get_by_username(username: str):
        return UserModel.get_by_username(username)

    @staticmethod
    def create(username: str, password: str, role_id: int):
        from app.auth import AuthService
        password_hash = AuthService.hash_password(password)
        return UserModel.create(username, password_hash, role_id)

    @staticmethod
    def update(user_id: int, username: str = None, role_id: int = None):
        updates = {}
        if username:
            updates["username"] = username
        if role_id:
            updates["role_id"] = role_id
        return UserModel.update(user_id, **updates)

    @staticmethod
    def delete(user_id: int):
        return UserModel.delete(user_id)
