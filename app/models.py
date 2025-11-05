import sqlite3
from typing import Optional, List, Dict, Any
from app.config import Config

# =================== DB CONNECTION ===================
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

# =================== RoleModel ===================
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

# =================== UserModel ===================
class UserModel:
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.user_id, u.username, u.role_id, u.anonymized, u.created_at, u.updated_at, r.nom_role
                FROM Utilisateur u
                JOIN Role r ON u.role_id = r.role_id
                WHERE u.deleted_at IS NULL
            """)
            return [Database.dict_from_row(row) for row in cur.fetchall()]

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
    def delete(user_id: int) -> bool:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Utilisateur SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
            conn.commit()
            return cur.rowcount > 0

# =================== SiteModel ===================
class SiteModel:
    @staticmethod
    def get_all(include_prestataire: bool = False) -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            if include_prestataire:
                cur.execute("""
                    SELECT s.*, c.nom_commune, c.nom_commune_breton, d.nom_department, d.nom_department_breton
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.deleted_at IS NULL
                """)
            else:
                cur.execute("""
                    SELECT s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description, 
                           s.latitude, s.longitude, s.commune_id, c.nom_commune, c.nom_commune_breton, d.nom_department, d.nom_department_breton
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.deleted_at IS NULL
                """)
            sites = [Database.dict_from_row(row) for row in cur.fetchall()]
            # Masque GPS pour public
            if not include_prestataire:
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
                    SELECT s.*, c.nom_commune, c.nom_commune_breton, d.nom_department, d.nom_department_breton
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.site_id = ? AND s.deleted_at IS NULL
                """, (site_id,))
            else:
                cur.execute("""
                    SELECT s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description, 
                           s.latitude, s.longitude, s.commune_id, c.nom_commune, c.nom_commune_breton, d.nom_department, d.nom_department_breton
                    FROM Site_Touristique s
                    JOIN Commune c ON s.commune_id = c.commune_id
                    JOIN Department d ON c.department_id = d.department_id
                    WHERE s.site_id = ? AND s.deleted_at IS NULL
                """, (site_id,))
            site = cur.fetchone()
            if not site:
                return None
            s_dict = Database.dict_from_row(site)
            if not include_prestataire:
                s_dict['latitude'] = None
                s_dict['longitude'] = None
            return s_dict

    @staticmethod
    def create(nom_site: str, commune_id: int, prestataire_id: Optional[int] = None, est_activite: Optional[bool] = False, est_lieu: Optional[bool] = False, description: Optional[str] = None, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Site_Touristique (nom_site, commune_id, prestataire_id, est_activite, est_lieu, description, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nom_site, commune_id, prestataire_id, est_activite, est_lieu, description, latitude, longitude))
            conn.commit()
            return {'site_id': cur.lastrowid, 'nom_site': nom_site, 'commune_id': commune_id, 'prestataire_id': prestataire_id}


# =================== ParcoursModel ===================
class ParcoursModel:
    @staticmethod
    def get_all() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Parcours")
            return [Database.dict_from_row(row) for row in cur.fetchall()]

    @staticmethod
    def get_by_id(parcours_id: int, include_prestataire: bool = False) -> Optional[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Parcours WHERE parcours_id = ?", (parcours_id,))
            parcours = cur.fetchone()
            if not parcours:
                return None
            parcours_dict = Database.dict_from_row(parcours)

            # Récupération des sites liés
            cur.execute("""
                SELECT ps.ordre_visite, s.site_id, s.nom_site, s.est_activite, s.est_lieu, s.description,
                       s.latitude, s.longitude, c.nom_commune, c.nom_commune_breton, d.nom_department, d.nom_department_breton
                FROM Parcours_Site ps
                JOIN Site_Touristique s ON ps.site_id = s.site_id
                JOIN Commune c ON s.commune_id = c.commune_id
                JOIN Department d ON c.department_id = d.department_id
                WHERE ps.parcours_id = ?
                ORDER BY ps.ordre_visite
            """, (parcours_id,))
            sites = [Database.dict_from_row(row) for row in cur.fetchall()]
            if not include_prestataire:
                for site in sites:
                    site['latitude'] = None
                    site['longitude'] = None
            parcours_dict['sites'] = sites
            return parcours_dict

    @staticmethod
    def create(nom_parcours: str, createur_id: int, sites: List[Dict]) -> Dict:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            # Insertion du parcours
            cur.execute("""
                INSERT INTO Parcours (nom_parcours, createur_id)
                VALUES (?, ?)
            """, (nom_parcours, createur_id))
            parcours_id = cur.lastrowid

            # Insertion des sites associés
            for site in sites:
                cur.execute("""
                    INSERT INTO Parcours_Site (parcours_id, site_id, ordre_visite)
                    VALUES (?, ?, ?)
                """, (parcours_id, site["site_id"], site["ordre_visite"]))

            conn.commit()
            return {"parcours_id": parcours_id, "nom_parcours": nom_parcours, "createur_id": createur_id, "sites": sites}

# =================== CommuneModel ===================
class CommuneModel:
    @staticmethod
    def get_all_communes() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.*, d.nom_department, d.nom_department_breton
                FROM Commune c
                JOIN Department d ON c.department_id = d.department_id
            """)
            return [Database.dict_from_row(row) for row in cur.fetchall()]

# =================== DepartmentModel ===================
class DepartmentModel:
    @staticmethod
    def get_all_departments() -> List[Dict]:
        with Database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Department")
            return [Database.dict_from_row(row) for row in cur.fetchall()]
