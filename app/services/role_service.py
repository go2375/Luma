from app.models import RoleModel

class RoleService:
    @staticmethod
    def get_all():
        return RoleModel.get_all()

    @staticmethod
    def create(nom_role: str):
        return RoleModel.create(nom_role)

    @staticmethod
    def update(role_id: int, nom_role: str):
        return RoleModel.update(role_id, nom_role)

    @staticmethod
    def delete(role_id: int):
        return RoleModel.delete(role_id)
