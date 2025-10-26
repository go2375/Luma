from app import create_app
from app.anonymization_utils import check_and_fix_all_usernames

# On vérifie la conformité RGPD avant le démarrage pour anonymiser les usernames sensibles si nécessaire
print("Vérification automatique RGPD en cours...")
check_and_fix_all_usernames()
print("Vérification RGPD terminée.\n")

# Créer l'application Flask
app = create_app()

if __name__ == '__main__':
    print("API Luméa en cours d'exécution !")
    print("Adresse : http://localhost:5000")
    print("Health check : http://localhost:5000/api/health\n")
    
    # On démarre le serveur web
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000
    )