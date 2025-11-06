import random
import re
import sqlite3
from typing import Dict, Any
from datetime import datetime, timedelta
from app.config import Config

# Connexion à la base SQLite
def get_db_connection() -> sqlite3.Connection:
    """
    Je crée une connexion à la base SQLite.
    Je configure row_factory pour récupérer des dictionnaires et j'active les clés étrangères.
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Anonymisation des utilisateurs
def is_identifiable(username: str) -> bool:
    """
    Je vérifie si le username contient des informations personnelles identifiables.
    Par exemple : email, espace ou caractères spéciaux.
    """
    if any(char in username for char in ["@", ".", " "]):
        return True
    # Vérifie le pattern : a-z, 0-9, underscore, 4-20 caractères
    return not re.fullmatch(r"[a-z0-9_]{4,20}", username)

def generate_pseudonymous_username(user_id: int, prefix: str = "user") -> str:
    """
    Je génère un pseudonyme pour un utilisateur basé sur son ID.
    Exemple : user_12
    """
    return f"{prefix}_{user_id}"

def anonymize_username(user_id: int, prefix: str = "user") -> Dict[str, str]:
    """
    Je modifie le username d'un utilisateur pour le rendre anonyme dans la base.
    Je marque également le champ `anonymized` pour savoir qu'il est RGPD compliant.
    """
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

def check_and_fix_all_usernames() -> None:
    """
    Je parcours tous les utilisateurs et j'anonymise ceux qui contiennent des données identifiables.
    Je fais un print pour indiquer combien de usernames ont été modifiés.
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, anonymized FROM Utilisateur WHERE deleted_at IS NULL")
        users = cur.fetchall()
        
        anonymized_count = 0
        for row in users:
            user_id = row["user_id"]
            username = row["username"]
            already_anonymized = row["anonymized"]
            if not already_anonymized and is_identifiable(username):
                anonymize_username(user_id)
                anonymized_count += 1
        
    print(f"{anonymized_count} username(s) anonymisé(s)" if anonymized_count else "Tous les usernames sont RGPD conformes")

def validate_and_fix_username(username: str, user_id: int = None) -> str:
    """
    Je valide un username lors de l'inscription.
    Si le username est identifiable, je le remplace par un pseudonyme.
    """
    if is_identifiable(username):
        if user_id is not None:
            return generate_pseudonymous_username(user_id)
        return f"user_{random.randint(10000, 99999)}"
    return username

# Anonymisation des sites
def anonymize_nom_site(site_row: Dict[str, Any]) -> str:
    """
    Je modifie le nom d'un site si c'est un nom de personne pour la RGPD.
    Je différencie les lieux, activités et fallback avec un ID unique.
    """
    nom_site = site_row.get("nom_site", "")
    site_id = site_row.get("site_id", 0)

    # Détecte un nom de personne : "Prénom Nom"
    if re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", nom_site):
        if site_row.get("est_lieu"):
            return f"Lieu #{site_id}"
        if site_row.get("est_activite"):
            return f"Activité #{site_id}"
        return f"Site #{site_id}"  # fallback
    return nom_site

def site_to_public_dict(site_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Je prépare un dictionnaire pour affichage public.
    Je masque les coordonnées GPS pour les lieux résidentiels.
    """
    public_data = {
        "site_id": site_row.get("site_id"),
        "nom_site": anonymize_nom_site(site_row),
        "est_activite": site_row.get("est_activite", False),
        "est_lieu": site_row.get("est_lieu", False),
        "commune_id": site_row.get("commune_id"),
        "nom_commune": site_row.get("nom_commune"),
        "nom_department": site_row.get("nom_department"),
        "nom_department_breton": site_row.get("nom_department_breton"),
        "description": site_row.get("description"),
        "created_at": site_row.get("created_at")
    }

    # Je masque latitude/longitude pour les lieux
    if site_row.get("est_lieu"):
        public_data["localisation_approximative"] = site_row.get("nom_commune")
    else:
        public_data["latitude"] = site_row.get("latitude")
        public_data["longitude"] = site_row.get("longitude")

    return public_data

def site_to_prestataire_dict(site_row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Je prépare un dictionnaire complet pour les prestataires.
    Toutes les données sont visibles.
    """
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
        "nom_department_breton": site_row.get("nom_department_breton"),
        "prestataire_id": site_row.get("prestataire_id"),
        "created_at": site_row.get("created_at"),
        "updated_at": site_row.get("updated_at")
    }

# Nettoyage des enregistrements
def cleanup_old_deleted_records(days: int = 30) -> None:
    """
    Je supprime définitivement les enregistrements marqués supprimés depuis 30 jours.
    Je nettoie les utilisateurs, sites et parcours.
    """
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
    total_deleted = deleted_users + deleted_sites + deleted_parcours
    print(f"Nettoyage RGPD : {deleted_users} utilisateurs, {deleted_sites} sites, {deleted_parcours} parcours supprimés définitivement (total {total_deleted})")
