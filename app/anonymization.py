# Permet de générer des identifiants aléatoires pour créer des pseudonymes temporaires
import random
# Permet d'utiliser module de regex (expressions régulières) qui permet de vérifier si un texte (ici username) correspond à notre modèle choisi.
import re
import sqlite3
from typing import Dict, List
from datetime import datetime, timedelta
from app.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

## Permet d'anonymiser des usernames
# Permet de vérifier si le username peut conduire à identifier une personne. On vérifie si username contient :
# '@' (adresse e-mail probable), '.' (format prenom.nom), les espaces ou si username ne respecte pas le pattern sécurisé.
def is_identifiable(username: str) -> bool:
    if "@" in username or "." in username or " " in username:
        # Si l’un de ces cas est vrai, on considère que le username est identifiable et qu'il est à anonymiser
        return True
    
    # On vérifie la pattern sécurisé (lettres minuscules, chiffres, underscore, 4-20 caractères)
    if not re.fullmatch(r"[a-z0-9_]{4,20}", username):
        return True
    
    return False

# Permet de générer un username anonymisé basé sur l'ID utilisateur avec un préfixe (par défaut user)
def generate_pseudonymous_username(user_id: int, prefix: str = "user") -> str:
    return f"{prefix}_{user_id}"

# Permet d'anonymiser le username d'un utilisateur dans notre bdd
def anonymize_username(user_id: int, prefix: str = "user") -> dict[str, str]:
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

# Permet de parcourir tous les utilisateurs et anonymiser ceux avec un username identifiable.
# Afin de réaliser un audit RGPD, cette fonction doit être exécutée par l'API lors du démarrage.
def check_and_fix_all_usernames() -> None:
    anonymized_count = 0
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, anonymized 
            FROM Utilisateur 
            WHERE deleted_at IS NULL
        """)
        users = cur.fetchall()
        
        anonymized_count = 0
        for user_id, username, already_anonymized in users:
            # Anonymiser seulement si username n'a pas été déjà anonymisé et s'il est identifiable
            if not already_anonymized and is_identifiable(username):
                nanonymize_username(user_id)
                anonymized_count += 1
        
    print(f"{anonymized_count} username(s) anonymisé(s)" if anonymized_count else "Tous les usernames sont RGPD conformes")

# Permet de valider le nom d'utilisateur lors de l'inscription et de générer un pseudonyme si le nom d'utilisateur est identifiable. 
def validate_and_fix_username(username: str, user_id: int = None) -> str:
    if is_identifiable(username):
        return generate_pseudonymous_username(user_id) if user_id else f"user_{random.randint(10000, 99999)}"
    return username


## Permet d'anonymiser des sites touristiques
# Permet d'anonymiser le nom d'un site si qu'il pourra conduire à exposer une identité d'une personne

def anonymize_nom_site(site_row: dict) -> str:
    nom_site = site_row.get("nom_site", "")
    type_site = site_row.get("type_site", "")
    site_id = site_row.get("site_id", 0)
    
    # Si site est résidentiel et il contient possiblement un nom de personne, ca permet de détecter
    # s'il y a majuscules multiples suggérant un nom et ensuite d'anonymiser ce nom de site en gardant
    # seulement le type de site et id de site 
    if type_site in Config.RESIDENTIAL_SITE_TYPES and re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", nom_site):
        type_label = type_site.replace("_", " ").title()
        return f"{type_label} #{site_id}"
    
    return nom_site

# Permet de convertir un site pour pouvoir afficher ses données auprès des visiteurs : 
# permet d'anonymiser nom_site si nécessaire, permet de masquer coordonnées GPS pour sites résidentiels et 
# permet d'exclure prestataire_id.
def site_to_public_dict(site_row: dict) -> dict:
    public_data = {
        "site_id": site_row.get("site_id"),
        "nom_site": anonymize_nom_site(site_row),
        "type_site": site_row.get("type_site"),
        "commune_id": site_row.get("commune_id"),
        "nom_commune": site_row.get("nom_commune"),
        "nom_department": site_row.get("nom_department"),
        "description": site_row.get("description"),
        "created_at": site_row.get("created_at")
    }
    
    # On affiche la géolocalisation uniquement pour les sites publics
    if site_row.get("type_site") not in Config.RESIDENTIAL_SITE_TYPES:
        public_data["latitude"] = site_row.get("latitude")
        public_data["longitude"] = site_row.get("longitude")
    else:
        # Pour sites résidentiels on affiche seulement la commune pour assurer la protection de la vie privée des prestataires
        public_data["localisation_approximative"] = site_row.get("nom_commune")
    
    return public_data

# Permet de convertir un site pour l'afficher auprès de son prestataire correspondant
# Cet affichage comprend toutes les données, y compris les coordonnées exactes du prestataire
def site_to_prestataire_dict(site_row: dict) -> dict:
    return {
        "site_id": site_row.get("site_id"),
        "nom_site": site_row.get("nom_site"),
        "type_site": site_row.get("type_site"),
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

# Permet de supprimer définitivement les enregistrements marqués comme supprimés depuis plus de 30 jours.
# Days définit la période de rétention avant suppression définitive à une durée 30 jours.
def cleanup_old_deleted_records(days: int = 30) -> None:
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Permet de supprimer définitivement les utilisateurs supprimés depuis > days
        cur.execute("""
            DELETE FROM Utilisateur 
            WHERE deleted_at IS NOT NULL 
            AND deleted_at < ?
        """, (cutoff_date,))
        deleted_users = cur.rowcount
        
        # Permet de supprimer définitivement les sites supprimés depuis > days
        cur.execute("""
            DELETE FROM Site_Touristique 
            WHERE deleted_at IS NOT NULL 
            AND deleted_at < ?
        """, (cutoff_date,))
        deleted_sites = cur.rowcount
        
        # Permet de supprimer définitivement les parcours supprimés depuis > days
        cur.execute("""
            DELETE FROM Parcours 
            WHERE deleted_at IS NOT NULL 
            AND deleted_at < ?
        """, (cutoff_date,))
        deleted_parcours = cur.rowcount
        
        conn.commit()
        
        print(f"Nettoyage RGPD : {deleted_users} utilisateurs, {deleted_sites} sites, {deleted_parcours} parcours supprimés définitivement")