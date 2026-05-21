import os
import sys
import argparse

# Ajouter le répertoire racine au path pour importer app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import face_recognition
from app import create_app, db
from app.models.user import User

def register_face(nom: str, prenom: str, matricule: str):
    """
    Enrôle une nouvelle personne via la webcam.
    """
    app = create_app()
    with app.app_context():
        # Vérifier si le matricule existe déjà
        if User.query.filter_by(matricule=matricule).first():
            print(f"Erreur : Le matricule {matricule} existe déjà.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Erreur : Impossible d'ouvrir la caméra.")
            return

        print("Appuyez sur 's' pour capturer la photo, ou 'q' pour quitter.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow("Enregistrement - Appuyez sur 's'", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                # Détecter le visage dans la capture
                # Apply FACE_TOLERANCE configuration setting to face_recognition.face_locations
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame, model="hog", tolerance=app.config['FACE_TOLERANCE'])
                
                if len(face_locations) == 0:
                    print("Aucun visage détecté. Réessayez.")
                    continue
                if len(face_locations) > 1:
                    print("Plusieurs visages détectés. Un seul visage requis.")
                    continue
                
                # Encodage
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                if encodings:
                    encoding = encodings[0]
                    
                    # Sauvegarder l'image
                    photo_dir = app.config['KNOWN_FACES_DIR']
                    if not os.path.exists(photo_dir):
                        os.makedirs(photo_dir)
                    
                    photo_filename = f"{prenom}_{nom}_{matricule}.jpg"
                    photo_path = os.path.join(photo_dir, photo_filename)
                    cv2.imwrite(photo_path, frame)
                    
                    # Créer l'utilisateur
                    user = User(nom=nom, prenom=prenom, matricule=matricule, photo_path=photo_path)
                    user.set_encoding(encoding)
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    print(f"Utilisateur {prenom} {nom} enregistré avec succès !")
                    break
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrôler une personne")
    parser.add_argument("--nom", required=True, help="Nom de la personne")
    parser.add_argument("--prenom", required=True, help="Prénom de la person")
    parser.add_argument("--matricule", required=True, help="Matricule unique")
    
    args = parser.parse_args()
    
    register_face(args.nom, args.prenom, args.matricule)
