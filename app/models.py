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

    @staticmethod
    # Permet de récupérer un rôle par son ID
    def get_by_id(role_id: int) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Role WHERE role_id = ?", (role_id,))
            row = cur.fetchone()
            return Database.dict_from_row(row) if row else None
    
    @staticmethod
    # Permet de créer un nouveau rôle
    def create(nom_role: str) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Role (nom_role) VALUES (?)", (nom_role,))
            conn.commit()
            return {'role_id': cur.lastrowid, 'nom_role': nom_role}
    
    @staticmethod
    # Permet de modifier un rôle
    def update(role_id: int, nom_role: str) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Role SET nom_role = ? WHERE role_id = ?", (nom_role, role_id))
            conn.commit()
            # Permet de retourner True si au moins une ligne a été modifiée
            return cur.rowcount > 0
    
    @staticmethod
    # Permet de supprimer un rôle
    def delete(role_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM Role WHERE role_id = ?", (role_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

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

# Modèle pour la table Site_Touristique
class SiteModel:
    @staticmethod
    # Permet de récupérer tous les sites non supprimés
    def get_all(include_prestataire: bool = False) -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            if include_prestataire:
                cur.execute("""
                    SELECT s.*, c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.deleted_at IS NULL
                """)
            else:
                cur.execute("""
                    SELECT s.site_id, s.nom_site, s.type_site, s.description, 
                           s.latitude, s.longitude, s.commune_id,
                           s.created_at, s.updated_at,
                           c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.deleted_at IS NULL
                """)
            return [Database.dict_from_row(row) for row in cur.fetchall()]
    
    @staticmethod
    # Permet de récupérer un site par son ID (si non supprimé)
    def get_by_id(site_id: int, include_prestataire: bool = False) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            if include_prestataire:
                cur.execute("""
                    SELECT s.*, c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.site_id = ? AND s.deleted_at IS NULL
                """, (site_id,))
            else:
                cur.execute("""
                    SELECT s.site_id, s.nom_site, s.type_site, s.description, 
                           s.latitude, s.longitude, s.commune_id,
                           s.created_at, s.updated_at,
                           c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.site_id = ? AND s.deleted_at IS NULL
                """, (site_id,))
            row = cur.fetchone()
            return Database.dict_from_row(row) if row else None
    
    @staticmethod
    # Permet de récupérer tous les sites non supprimés d'un prestataire
    def get_by_prestataire(prestataire_id: int) -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT s.*, c.nom_commune, d.nom_department
                FROM Site_Touristique s
                JOIN Commune c ON s.commune_id = c.commune_id
                JOIN Department d ON c.department_id = d.department_id
                WHERE s.prestataire_id = ? AND s.deleted_at IS NULL
            """, (prestataire_id,))
            return [Database.dict_from_row(row) for row in cur.fetchall()]
    
    @staticmethod
    # Permet de créer un nouveau site touristique
    def create(nom_site: str, commune_id: int, prestataire_id: Optional[int] = None,
               type_site: Optional[str] = None, description: Optional[str] = None,
               latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Site_Touristique 
                (nom_site, type_site, description, latitude, longitude, commune_id, prestataire_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nom_site, type_site, description, latitude, longitude, commune_id, prestataire_id))
            conn.commit()
            return {'site_id': cur.lastrowid}
    
    @staticmethod
    # Permet de mettre à jour les informations d’un site touristique avec updated_at mise à jour automatiquement
    def update(site_id: int, **kwargs) -> bool:
        allowed_fields = ['nom_site', 'type_site', 'description', 'latitude', 'longitude', 
                          'commune_id', 'prestataire_id', 'anonymized', 'deleted_at']
        # Permet de filtrer uniquement les champs autorisés
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        # Ajoute la mise à jour automatique du timestamp
        updates["updated_at"] = "CURRENT_TIMESTAMP"

        # Prépare la clause SET
        set_clause = ", ".join([f"{k} = ?" if k != "updated_at" else f"{k} = {updates[k]}" 
                                for k in updates.keys()])
        values = [v for k, v in updates.items() if k != "updated_at"] + [site_id]

        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Site_Touristique SET {set_clause} WHERE site_id = ?", values)
            conn.commit()
            return cur.rowcount > 0
    
    @staticmethod
    # Permet de marquer un site comme supprimé via deleted_at
    def delete(site_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE Site_Touristique 
                    SET deleted_at = CURRENT_TIMESTAMP 
                    WHERE site_id = ?
                """, (site_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    # Permet de supprimer définitivement un site
    def hard_delete(site_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM Site_Touristique WHERE site_id = ?", (site_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

# Modèle pour la table Parcours
class ParcoursModel:
    @staticmethod
    # Permet de récupérer tous les parcours d'un utilisateur
    def get_by_user(user_id: int) -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.*, u.username as createur_username
                FROM Parcours p
                JOIN Utilisateur u ON p.createur_id = u.user_id
                WHERE p.createur_id = ?
            """, (user_id,))
            return [Database.dict_from_row(row) for row in cur.fetchall()]

    @staticmethod
    # Permet de récupérer un parcours avec ses sites touristiques
    def get_by_id(parcours_id: int) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            # D'abord on récupère les parcours
            cur.execute("""
                SELECT p.*, u.username as createur_username
                FROM Parcours p
                JOIN Utilisateur u ON p.createur_id = u.user_id
                WHERE p.parcours_id = ?
            """, (parcours_id,))
            parcours = cur.fetchone()
            if not parcours:
                return None

            parcours_dict = Database.dict_from_row(parcours)

            # Ensuite on récupère les sites du parcours
            cur.execute("""
                SELECT ps.ordre_visite, s.site_id, s.nom_site, s.type_site, 
                       s.description, s.latitude, s.longitude,
                       c.nom_commune, d.nom_department
                FROM Parcours_Site ps
                JOIN Site_Touristique s ON ps.site_id = s.site_id
                JOIN Commune c ON s.commune_id = c.commune_id
                JOIN Department d ON c.department_id = d.department_id
                WHERE ps.parcours_id = ?
                ORDER BY ps.ordre_visite
            """, (parcours_id,))
            parcours_dict['sites'] = [Database.dict_from_row(row) for row in cur.fetchall()]

            return parcours_dict

    @staticmethod
    # Permet de créer un nouveau parcours et y ajouter des sites touristiques via sites (list[dict], optional), ici liste de sites ajoutée au parcours.
    def create(nom_parcours: str, createur_id: int, sites: list[dict] = None) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            # On crée le parcours
            cur.execute(
                "INSERT INTO Parcours (nom_parcours, createur_id) VALUES (?, ?)",
                (nom_parcours, createur_id)
            )
            parcours_id = cur.lastrowid

            # Ensuite on ajoute les sites
            if sites:
                for site in sites:
                    site_id = site['site_id']
                    ordre_visite = site.get('ordre_visite')
                    cur.execute(
                        "INSERT INTO Parcours_Site (parcours_id, site_id, ordre_visite) VALUES (?, ?, ?)",
                        (parcours_id, site_id, ordre_visite)
                    )

            conn.commit()
            return {'parcours_id': parcours_id}

    @staticmethod
    # Permet de mettre à jour un parcours avec updated_at mise à jour automatiquement, aussi si des sites d'un parcours ont été si des sites ont été retirés
    def update(parcours_id: int, **kwargs) -> bool:
        allowed_fields = ['nom_parcours', 'deleted_at']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        # Permet de récupérer le nombre actuel de sites liés au parcours
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) AS nb_sites
                FROM Parcours_Site
                WHERE parcours_id = ?
            """, (parcours_id,))
            nb_sites = cur.fetchone()['nb_sites']

        # Permet de vérifier si updated_at doit être mis à jour, soit parce qu'il y a des champs à mettre à jour,
        # soit parce que le nombre de sites a diminué (site à été supprimé)
        if updates or ('nb_sites_precedent' in kwargs and nb_sites < kwargs['nb_sites_precedent']):
            updates['updated_at'] = "CURRENT_TIMESTAMP"

        if not updates:
            return False

        set_clause = ", ".join([
            f"{k} = ?" if k != "updated_at" else f"{k} = {updates[k]}" 
            for k in updates.keys()
        ])
        values = [v for k, v in updates.items() if k != "updated_at"] + [parcours_id]

        # Permet d'exécuter la mise à jour dans la base de données
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Parcours SET {set_clause} WHERE parcours_id = ?", values)
            conn.commit()

            return cur.rowcount > 0

    @staticmethod
    # Permet de supprimer un parcours
    def delete(parcours_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Parcours WHERE parcours_id = ?", (parcours_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    # Permet de retirer un site d'un parcours
    def remove_site(parcours_id: int, site_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM Parcours_Site 
                WHERE parcours_id = ? AND site_id = ?
            """, (parcours_id, site_id))
            conn.commit()
            return cur.rowcount > 0

# Modèle pour la table Commune
class CommuneModel:
    # Permet de récupérer toutes les communes
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.*, d.nom_department
                FROM Commune c
                JOIN Department d ON c.department_id = d.department_id
            """)
            return [Database.dict_from_row(row) for row in cur.fetchall()]

# Modèle pour la table Department
class DepartmentModel:
    # Permet de récupérer tous les départements
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Department")
            return [Database.dict_from_row(row) for row in cur.fetchall()]