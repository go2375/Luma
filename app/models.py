import sqlite3
from typing import Optional, List, Dict, Any
from app.config import Config

class Database:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
        return {key: row[key] for key in row.keys()}

# ===== RoleModel =====
class RoleModel:
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Role")
            return [Database.dict_from_row(row) for row in cur.fetchall()]

    @staticmethod
    def get_by_id(role_id: int) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Role WHERE role_id = ?", (role_id,))
            row = cur.fetchone()
            return Database.dict_from_row(row) if row else None

    @staticmethod
    def create(nom_role: str) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Role (nom_role) VALUES (?)", (nom_role,))
            conn.commit()
            return {'role_id': cur.lastrowid, 'nom_role': nom_role}

    @staticmethod
    def update(role_id: int, nom_role: str) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Role SET nom_role = ? WHERE role_id = ?", (nom_role, role_id))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def delete(role_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM Role WHERE role_id = ?", (role_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

# ===== UserModel =====
class UserModel:
    @staticmethod
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
    def create(username: str, password_hash: str, role_id: int) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Utilisateur (username, password_hash, role_id)
                VALUES (?, ?, ?)
            """, (username, password_hash, role_id))
            conn.commit()
            return {'user_id': cur.lastrowid, 'username': username, 'role_id': role_id}

    @staticmethod
    def update(user_id: int, **kwargs) -> bool:
        allowed_fields = ['username', 'role_id', 'password_hash', 'anonymized', 'deleted_at']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()] + ["updated_at = CURRENT_TIMESTAMP"])
        values = list(updates.values()) + [user_id]
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Utilisateur SET {set_clause} WHERE user_id = ?", values)
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def update_role(user_id: int, role_id: int) -> bool:
        return UserModel.update(user_id, role_id=role_id)

    @staticmethod
    def update_password(user_id: int, new_password_hash: str) -> bool:
        return UserModel.update(user_id, password_hash=new_password_hash)

    @staticmethod
    def delete(user_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Utilisateur SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
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
    def mark_as_anonymized(user_id: int) -> bool:
        return UserModel.update(user_id, anonymized=1)

# ===== SiteModel =====
class SiteModel:
    @staticmethod
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
                    SELECT s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description, 
                           s.latitude, s.longitude, s.commune_id,
                           s.created_at, s.updated_at,
                           c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.deleted_at IS NULL
                """)
            sites = [Database.dict_from_row(row) for row in cur.fetchall()]
            # Masquage GPS par défaut
            for s in sites:
                s['latitude'] = None
                s['longitude'] = None
            return sites

    @staticmethod
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
                    SELECT s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description, 
                           s.latitude, s.longitude, s.commune_id,
                           s.created_at, s.updated_at,
                           c.nom_commune, d.nom_department
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.site_id = ? AND s.deleted_at IS NULL
                """, (site_id,))
            site = cur.fetchone()
            if not site:
                return None
            s_dict = Database.dict_from_row(site)
            s_dict['latitude'] = None
            s_dict['longitude'] = None
            return s_dict

    @staticmethod
    def create(nom_site: str, commune_id: int, prestataire_id: Optional[int] = None,
               est_activite: bool = False, est_lieu: bool = False, description: Optional[str] = None,
               latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Site_Touristique 
                (nom_site, est_activite, est_lieu, description, latitude, longitude, commune_id, prestataire_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nom_site, est_activite, est_lieu, description, latitude, longitude, commune_id, prestataire_id))
            conn.commit()
            return {'site_id': cur.lastrowid}

    @staticmethod
    def update(site_id: int, **kwargs) -> bool:
        allowed_fields = ['nom_site', 'est_activite', 'est_lieu', 'description', 
                          'latitude', 'longitude', 'commune_id', 'prestataire_id', 'anonymized', 'deleted_at']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()] + ["updated_at = CURRENT_TIMESTAMP"])
        values = list(updates.values()) + [site_id]
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Site_Touristique SET {set_clause} WHERE site_id = ?", values)
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def delete(site_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE Site_Touristique SET deleted_at = CURRENT_TIMESTAMP WHERE site_id = ?", (site_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def hard_delete(site_id: int) -> bool:
        try:
            with Database.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM Site_Touristique WHERE site_id = ?", (site_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            return False

# ===== ParcoursModel (RGPD compatible) =====
class ParcoursModel:
    @staticmethod
    def get_by_user(user_id: int) -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.*, u.username AS createur_username
                FROM Parcours p
                JOIN Utilisateur u ON p.createur_id = u.user_id
                WHERE p.createur_id = ?
            """, (user_id,))
            return [Database.dict_from_row(row) for row in cur.fetchall()]

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False) -> Optional[Dict]:
        """Récupère un parcours avec ses sites.
        Masque GPS si include_prestataire=False (visiteur public)
        """
        with Database.get_connection() as conn:
            cur = conn.cursor()
            # Récupération du parcours
            cur.execute("""
                SELECT p.*, u.username AS createur_username
                FROM Parcours p
                JOIN Utilisateur u ON p.createur_id = u.user_id
                WHERE p.parcours_id = ?
            """, (parcours_id,))
            parcours = cur.fetchone()
            if not parcours:
                return None

            parcours_dict = Database.dict_from_row(parcours)

            # Récupération des sites liés
            cur.execute("""
                SELECT ps.ordre_visite, s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description,
                       s.latitude, s.longitude, c.nom_commune, d.nom_department
                FROM Parcours_Site ps
                JOIN Site_Touristique s ON ps.site_id = s.site_id
                JOIN Commune c ON s.commune_id = c.commune_id
                JOIN Department d ON c.department_id = d.department_id
                WHERE ps.parcours_id = ?
                ORDER BY ps.ordre_visite
            """, (parcours_id,))
            sites = [Database.dict_from_row(row) for row in cur.fetchall()]

            # RGPD : Masquage GPS pour public
            if not include_prestataire:
                for site in sites:
                    site['latitude'] = None
                    site['longitude'] = None

            parcours_dict['sites'] = sites
            return parcours_dict

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: List[Dict] = None) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Parcours (nom_parcours, createur_id) VALUES (?, ?)", (nom_parcours, createur_id))
            parcours_id = cur.lastrowid
            if sites:
                for site in sites:
                    cur.execute(
                        "INSERT INTO Parcours_Site (parcours_id, site_id, ordre_visite) VALUES (?, ?, ?)",
                        (parcours_id, site['site_id'], site.get('ordre_visite'))
                    )
            conn.commit()
            return {'parcours_id': parcours_id}

    @staticmethod
    def update(parcours_id: int, **kwargs) -> bool:
        allowed_fields = ['nom_parcours', 'deleted_at']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()] + ["updated_at = CURRENT_TIMESTAMP"])
        values = list(updates.values()) + [parcours_id]
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE Parcours SET {set_clause} WHERE parcours_id = ?", values)
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def delete(parcours_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Parcours WHERE parcours_id = ?", (parcours_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def remove_site(parcours_id: int, site_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Parcours_Site WHERE parcours_id = ? AND site_id = ?", (parcours_id, site_id))
            conn.commit()
            return cur.rowcount > 0

# ===== CommuneModel =====
class CommuneModel:
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

# ===== DepartmentModel =====
class DepartmentModel:
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Department")
            return [Database.dict_from_row(row) for row in cur.fetchall()]
