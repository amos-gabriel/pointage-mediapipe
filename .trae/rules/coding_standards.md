# Standards de Code & Conventions

## Nommage

| Élément | Convention | Exemple |
|---|---|---|
| Fichiers Python | snake_case | `face_engine.py` |
| Classes | PascalCase | `FaceEngine`, `AttendanceModel` |
| Fonctions/méthodes | snake_case | `detect_face()`, `mark_present()` |
| Variables | snake_case | `known_encodings`, `frame_count` |
| Constantes | UPPER_SNAKE | `TOLERANCE_THRESHOLD = 0.5` |
| Routes Flask | kebab-case | `/video-feed`, `/mark-present` |
| Templates HTML | snake_case | `attendance.html` |

## Structure d'une Fonction Type

```python
def detect_and_identify(frame: np.ndarray) -> list[dict]:
    """
    Détecte et identifie les visages dans une frame vidéo.
    
    Args:
        frame: Image BGR provenant d'OpenCV (np.ndarray).
    
    Returns:
        Liste de dicts : [{"name": str, "location": tuple, "confidence": float}]
    
    Raises:
        ValueError: Si la frame est None ou vide.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Frame invalide fournie à detect_and_identify")
    
    # Corps de la fonction...
    results = []
    return results
```

## Structure d'une Route Flask Type

```python
@bp.route('/mark-present', methods=['POST'])
def mark_present():
    """Enregistre le pointage d'un utilisateur identifié."""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id manquant"}), 400
    
    try:
        attendance = AttendanceService.mark(user_id=data['user_id'])
        return jsonify({"success": True, "attendance_id": attendance.id}), 201
    except UserNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Erreur pointage: {e}")
        return jsonify({"error": "Erreur interne"}), 500
```

## Gestion des Erreurs — Classes Personnalisées

```python
# app/utils/exceptions.py
class FaceNotDetectedError(Exception):
    """Levée quand aucun visage n'est détecté dans la frame."""
    pass

class UserNotFoundError(Exception):
    """Levée quand l'utilisateur n'existe pas en base."""
    pass

class GestureTimeoutError(Exception):
    """Levée quand le geste n'est pas maintenu assez longtemps."""
    pass
```

## Logging

```python
import logging
logger = logging.getLogger(__name__)

# Usage
logger.info("Visage détecté : %s (confiance: %.2f)", name, confidence)
logger.warning("Caméra index 0 indisponible, tentative index 1")
logger.error("Erreur encodage visage pour %s: %s", user_id, str(e))
```

## Configuration (`config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/attendance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Vision
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    TARGET_FPS = int(os.environ.get('TARGET_FPS', 15))
    FACE_TOLERANCE = float(os.environ.get('FACE_TOLERANCE', 0.5))
    GESTURE_CONFIRM_SECONDS = float(os.environ.get('GESTURE_CONFIRM_SECONDS', 2.0))
    KNOWN_FACES_DIR = os.environ.get('KNOWN_FACES_DIR', 'data/known_faces')
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
```

## Tests

```python
# tests/test_face_engine.py
import pytest
import numpy as np
from app.utils.face_engine import FaceEngine

class TestFaceEngine:
    def test_returns_unknown_for_blank_frame(self):
        engine = FaceEngine()
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        result = engine.identify(blank)
        assert result == []

    def test_raises_on_none_frame(self):
        engine = FaceEngine()
        with pytest.raises(ValueError):
            engine.identify(None)
```

## Git Commit Messages (en français)

```
feat: ajouter détection de geste main levée
fix: corriger fuite mémoire dans le thread caméra
refactor: extraire logique d'encodage dans FaceEngine
test: ajouter tests unitaires pour gesture_engine
docs: mettre à jour README avec instructions install
chore: mettre à jour requirements.txt
```
