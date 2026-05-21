from datetime import datetime
import pickle
import numpy as np
from app import db

class User(db.Model):
    """
    Modèle représentant un utilisateur (étudiant ou personnel).
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    matricule = db.Column(db.String(50), unique=True, nullable=False, index=True)
    face_encoding = db.Column(db.LargeBinary, nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_encoding(self, encoding: np.ndarray) -> None:
        """Sérialise l'encodage numpy en BLOB."""
        self.face_encoding = pickle.dumps(encoding)

    def get_encoding(self) -> np.ndarray | None:
        """Désérialise le BLOB en np.ndarray."""
        if self.face_encoding:
            return pickle.loads(self.face_encoding)
        return None

    @property
    def photo_filename(self) -> str | None:
        """Retourne uniquement le nom du fichier photo."""
        if self.photo_path:
            import os
            return os.path.basename(self.photo_path)
        return None

    def __repr__(self):
        return f'<User {self.prenom} {self.nom}>'
