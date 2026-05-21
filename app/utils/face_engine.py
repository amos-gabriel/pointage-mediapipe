import face_recognition
import numpy as np
import cv2
import os
from typing import List, Dict, Any, Optional
from app.models.user import User

class FaceEngine:
    """
    Moteur de reconnaissance faciale utilisant face_recognition.
    """
    def __init__(self, tolerance: float = 0.5):
        self.tolerance = tolerance
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []

    def load_known_faces(self) -> int:
        """
        Charge les visages connus depuis la base de données.
        Retourne le nombre de visages chargés.
        """
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        
        users = User.query.filter(User.face_encoding != None).all()
        for user in users:
            encoding = user.get_encoding()
            if encoding is not None:
                self.known_encodings.append(encoding)
                self.known_names.append(f"{user.prenom} {user.nom}")
                self.known_ids.append(user.id)
        
        return len(self.known_encodings)

    def identify(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Identifie les visages dans un frame BGR OpenCV.
        Retourne [{"name": str, "location": (top, right, bottom, left), "confidence": float, "user_id": int}]
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame invalide fournie à identify")

        # Convertir BGR (OpenCV) en RGB (face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Détecter les visages
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            user_id = None
            confidence = 0.0
            
            if self.known_encodings:
                # Comparer avec les visages connus
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if face_distances[best_match_index] <= self.tolerance:
                    name = self.known_names[best_match_index]
                    user_id = self.known_ids[best_match_index]
                    confidence = 1.0 - face_distances[best_match_index]
            
            results.append({
                "name": name,
                "location": (top, right, bottom, left),
                "confidence": float(confidence),
                "user_id": user_id
            })
            
        return results

    def encode_face(self, image_path: str) -> Optional[np.ndarray]:
        """Génère un encodage pour une image donnée."""
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            return encodings[0]
        return None

    def count_faces(self, frame: np.ndarray) -> int:
        """Compte le nombre de visages sans identification."""
        if frame is None or frame.size == 0:
            return 0
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        return len(face_locations)
