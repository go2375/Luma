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

# # Modèle pour la table Utilisateur
# class UtilisateurModel:

# # Modèle pour la table Site_Touristique
# class SiteModel:

# # Modèle pour la table Parcours
# class ParcoursModel:

# # Modèle pour la table Commune
# class CommuneModel:

# # Modèle pour la table Department
# class DepartmentModel: