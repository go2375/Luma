import random
import re
import sqlite3
from typing import Dict, Any
from datetime import datetime, timedelta
from app.config import Config

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Vérifie si un username est identifiable
def is_identifiable(username: str) -> bool:
    if any(char in username for char in ["@", ".", " "]):
        return True
    return not re.fullmatch(r"[a-z0-9_]{4,20}", username)

# Génère un pseudonyme basé sur l'ID utilisateur
def generate_pseudonymous_username(user_id: int, prefix: str = "user") -> str:
    return f"{prefix}_{user_id}"

# Anonymise le username dans la base
def anonymize_username(user_id: int, prefix: str = "user") -> Dict[str, str]:
    new_username = generate_pseudonymous_username(user_id, prefix)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE Utilisateur
            SET username = ?, anonymized = 1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (new_username, user_id))
        conn.commit()
    return {"user_id": user_id, "new_username": new_username}

# Parcourt tous les utilisateurs et anonymise ceux identifiables
def check_and_fix_all_usernames() -> None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, anonymized FROM Utilisateur WHERE deleted_at IS NULL")
        users = cur.fetchall()
        
        anonymized_count = 0
        for row in users:
            user_id, username, already_anonymized = row["user_id"], row["username"], row["anonymized"]
            if not already_anonymized and is_identifiable(username):
                anonymize_username(user_id)
                anonymized_count += 1
        
    print(f"{anonymized_count} username(s) anonymisé(s)" if anonymized_count else "Tous les usernames sont RGPD conformes")

# Valide et corrige un username lors de l'inscription
def validate_and_fix_username(username: str, user_id: int = None) -> str:
    if is_identifiable(username):
        if user_id:
            return generate_pseudonymous_username(user_id)
        return f"user_{random.randint(10000, 99999)}"
    return username

# Anonymise le nom d'un site si c'est un site résidentiel
def anonymize_nom_site(site_row: Dict[str, Any]) -> str:
    nom_site = site_row.get("nom_site", "")
    site_id = site_row.get("site_id", 0)
    
    # Si le nom contient un nom de personne (majuscule suivi de minuscules)
    if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", nom_site):
        if site_row.get("est_lieu", False):
            return f"Lieu #{site_id}"
        if site_row.get("est_activite", False):
            return f"Activité #{site_id}"
    return nom_site

# Convertit un site pour affichage public (anonymisation nom + RGPD GPS)
def site_to_public_dict(site_row: Dict[str, Any]) -> Dict[str, Any]:
    public_data = {
        "site_id": site_row.get("site_id"),
        "nom_site": anonymize_nom_site(site_row),
        "est_activite": site_row.get("est_activite", False),
        "est_lieu": site_row.get("est_lieu", False),
        "commune_id": site_row.get("commune_id"),
        "nom_commune": site_row.get("nom_commune"),
        "nom_department": site_row.get("nom_department"),
        "description": site_row.get("description"),
        "created_at": site_row.get("created_at")
    }
    
    # Masque GPS pour sites résidentiels (est_lieu = True)
    if not site_row.get("est_lieu", False):
        public_data["latitude"] = site_row.get("latitude")
        public_data["longitude"] = site_row.get("longitude")
    else:
        public_data["localisation_approximative"] = site_row.get("nom_commune")
    
    return public_data

# Convertit un site pour affichage prestataire (toutes données)
def site_to_prestataire_dict(site_row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "site_id": site_row.get("site_id"),
        "nom_site": site_row.get("nom_site"),
        "est_activite": site_row.get("est_activite", False),
        "est_lieu": site_row.get("est_lieu", False),
        "description": site_row.get("description"),
        "latitude": site_row.get("latitude"),
        "longitude": site_row.get("longitude"),
        "commune_id": site_row.get("commune_id"),
        "nom_commune": site_row.get("nom_commune"),
        "nom_department": site_row.get("nom_department"),
        "prestataire_id": site_row.get("prestataire_id"),
        "created_at": site_row.get("created_at"),
        "updated_at": site_row.get("updated_at")
    }

# Supprime définitivement les enregistrements supprimés depuis plus de X jours
def cleanup_old_deleted_records(days: int = 30) -> None:
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Utilisateur WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff_date,))
        deleted_users = cur.rowcount
        cur.execute("DELETE FROM Site_Touristique WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff_date,))
        deleted_sites = cur.rowcount
        cur.execute("DELETE FROM Parcours WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff_date,))
        deleted_parcours = cur.rowcount
        conn.commit()
    print(f"Nettoyage RGPD : {deleted_users} utilisateurs, {deleted_sites} sites, {deleted_parcours} parcours supprimés définitivement")
