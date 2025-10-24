import sqlite3

## Permet de préciser les types : Optional et Dict, où les clés sont toujours des chaînes de caractères
# (par exemple "username", "role_id", etc.) et les valeurs peuvent être de n’importe quel type : int, float, str, bool ou None.
from typing import Optional, List, Dict, Any

# On import objet Config de config.py
from app.config import Config

# Pour gérer la connexion à la base de données
class Database:
    # @staticmethod dans une classe n’a pas besoin d’une instance pour être appelé.
    @staticmethod
    def get_connection():
        # Ouvrir la base SQLite
        conn = sqlite3.connect(Config.DATABASE_PATH)
        # Permet de récupérer les lignes comme dictionnaire
        conn.row_factory = sqlite3.Row
        # Active les clés étrangères, désactivées par défaut par SQLite.
        conn.execute("PRAGMA foreign_keys = ON")
        # Permet de renvoyer l’objet conn, l’objet de connexion SQLite,
        # afin que les autres parties du code puissent utiliser cette connexion pour exécuter
        # des requêtes SQL (SELECT, INSERT, UPDATE, etc.).
        return conn
    
    @staticmethod
    # sqlite3.Row est un format interne de SQLite qui permet de convertir une ligne en dictionnaire Python, 
    # où les clés du dictionnaire sont les noms des colonnes (username, role_id, etc.)
    # et les valeurs sont les données correspondantes dans cette ligne.
    # Ce dictionnaire Python sera automatiquement converti en JSON lorsque l’API enverra
    # une réponse à une requête soumise par un client.
    def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
        # row[key] correspond à la valeur d’une colonne pour la ligne actuelle.
        # for key in row.keys() parcourit la liste des noms de colonnes.
        # {key: row[key] ...} crée un dictionnaire où chaque clé correspond au nom d’une colonne
        # et chaque valeur à la donnée correspondante.
        # Ainsi, dict_from_row(row) convertit une ligne SQL en dictionnaire Python,
        # prêt à être utilisé par l’API.
        return {key: row[key] for key in row.keys()}

# Modèle pour la table Role
class RoleModel:
    @staticmethod
    # Permet de définir la fonction qui va récupérer tous les rôles, 
    # en indiquant que la fonction retourne une liste de dictionnaires
    def get_all() -> List[Dict]:
        # "with" garantit que la connexion sera fermée automatiquement à la sortie du bloc et même en cas d’erreur
        with Database.get_connection() as conn:
            cur = conn.cursor()
            # Permet de récupérer toutes les colonnes et toutes les lignes de la table Role.
            cur.execute("SELECT * FROM Role")
            # cur.fetchall() extrait toutes les lignes du curseur SQL sous forme de liste de tuples, par exemple : [(1, "role_id"), (2, "nom_role")].
            # Pour chaque tuple row, la fonction Database.dict_from_row(row) convertit la ligne en dictionnaire, c’est-à-dire qu’elle associe chaque nom de colonne à sa valeur : {colonne: valeur}.
            # Cela permet d’envoyer les résultats SQL à une API sans accéder aux champs par index.
            # Par exemple, dict_from_row(row) transforme (1, "role_id") en {"id": 1, "name": "role_id"}.
            # Ainsi, la ligne retourne [{"id": 1, "name": "role_id"}, {"id": 2, "name": "nom_role"}].
            # Cette approche permet de créer une liste d’objets Python à partir des lignes SQL.
            return [Database.dict_from_row(row) for row in cur.fetchall()]

# Modèle pour la table Utilisateur
class UserModel:
    @staticmethod
    # Permet de récupérer un utilisateur par son username
    def get_by_username(username: str) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.*, r.nom_role 
                FROM Utilisateur u
                JOIN Role r ON u.role_id = r.role_id
                WHERE u.username = ?
            """, (username,))
            row = cur.fetchone()
            return Database.dict_from_row(row) if row else None
    
    @staticmethod
    # Permet de récupérer un utilisateur par son id
    def get_by_id(user_id: int) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.user_id, u.username, u.role_id, u.anonymized, u.created_at, u.updated_at, r.nom_role
                FROM Utilisateur u
                JOIN Role r ON u.role_id = r.role_id
                WHERE u.user_id = ? AND u.deleted_at IS NULL
            """, (user_id,))
            row = cur.fetchone()
            return Database.dict_from_row(row) if row else None

    @staticmethod
    # Permet de récupérer tous les utilisateurs non supprimés (sans password_hash)
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.user_id, u.username, u.role_id, u.anonymized, 
                       u.created_at, u.updated_at, r.nom_role
                FROM Utilisateur u
                JOIN Role r ON u.role_id = r.role_id
                WHERE u.deleted_at IS NULL
            """)
            return [Database.dict_from_row(row) for row in cur.fetchall()]
    
    @staticmethod
    #Permet de créer un nouvel utilisateur
    def create(username: str, password_hash: str, role_id: int) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Utilisateur (username, password_hash, role_id)
                VALUES (?, ?, ?)
            """, (username, password_hash, role_id))
            conn.commit()
            return {
                # lastrowid permet Cela permet de savoir immédiatement quel est l’id du nouvel utilisateur, sans faire une requête SELECT.
                'user_id': cur.lastrowid,
                'username': username,
                'role_id': role_id
            }  

    @staticmethod
    # Permet de mettre à jour les informations d’un utilisateur et mettre à jour updated_at automatiquement
    def update(user_id: int, **kwargs) -> bool:
        """Mettre à jour les informations d’un utilisateur (updated_at automatique)"""
        allowed_fields = ['username', 'role_id', 'password_hash', 'anonymized', 'deleted_at']
        # Filtrer seulement les champs autorisés
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        # Ca permet d'jouter updated_at automatiquement
        updates["updated_at"] = "CURRENT_TIMESTAMP"

        # Ca permet de construire la clause SET dynamiquement
        set_clause = ", ".join([
            f"{k} = ?" if k != "updated_at" else f"{k} = {updates[k]}" 
            for k in updates.keys()
        ])
        # Ca permet de préparer les valeurs pour l'exécution (exclude updated_at)
        values = [v for k, v in updates.items() if k != "updated_at"] + [user_id]

        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Utilisateur SET {set_clause} WHERE user_id = ?", values)
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    # Permet de modifier le rôle d'un utilisateur
    def update_role(user_id: int, role_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Utilisateur 
                SET role_id = ? 
                WHERE user_id = ?
            """, (role_id, user_id))
            conn.commit()
            return cur.rowcount > 0
    
    @staticmethod
    # Permet de modifier le mot de passe d'un utilisateur
    def update_password(user_id: int, new_password_hash: str) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Utilisateur 
                SET password_hash = ? 
                WHERE user_id = ?
            """, (new_password_hash, user_id))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    # Permet de supprimer définitivement un utilisateur
    def hard_delete(user_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM Utilisateur WHERE user_id = ?", (user_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    # Permet de marquer utilisateur comme supprimé
    def delete(user_id: int) -> bool:
        """Soft delete : marquer l'utilisateur comme supprimé"""
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Utilisateur 
                SET deleted_at = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    # Permet de marquer utilisateur comme anonymisé
    def mark_as_anonymized(user_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Utilisateur 
                SET anonymized = 1 
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            return cur.rowcount > 0

# # Modèle pour la table Site_Touristique
# class SiteModel:

# # Modèle pour la table Parcours
# class ParcoursModel:

# # Modèle pour la table Commune
# class CommuneModel:

# # Modèle pour la table Department
# class DepartmentModel: