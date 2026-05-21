# 📋 Référence Rapide — Pointage Facial

## Commandes Essentielles

```bash
# Démarrer l'app
python run.py

# Enrôler une personne
python scripts/register_face.py --nom "Nom" --prenom "Prenom" --matricule "ID"

# Lancer les tests
pytest tests/ -v

# Couverture de tests
pytest tests/ --cov=app --cov-report=term-missing

# Initialiser/migrer la BDD
flask db init       # une seule fois
flask db migrate    # après changement de modèle
flask db upgrade    # appliquer les migrations
```

## URLs de l'Application

| URL | Description |
|---|---|
| `http://localhost:5000/` | Page d'accueil |
| `http://localhost:5000/attendance` | Interface 1 : Pointage |
| `http://localhost:5000/video_feed` | Flux vidéo brut (MJPEG) |
| `http://localhost:5000/counting` | Interface 2 : Comptage |
| `http://localhost:5000/video_feed_count` | Flux vidéo comptage |
| `http://localhost:5000/admin` | Administration |
| `http://localhost:5000/api/today-attendance` | API JSON présences |
| `http://localhost:5000/api/current-count` | API JSON comptage |

## Bibliothèques Clés & Leur Rôle

| Bibliothèque | Usage |
|---|---|
| `face_recognition` | Encodage + comparaison de visages (dlib backend) |
| `mediapipe` | Détection des landmarks de la main |
| `opencv-python` | Capture caméra, dessin overlays, encodage JPEG |
| `flask-sqlalchemy` | ORM pour SQLite |
| `threading` | Thread caméra non-bloquant |

## Seuils & Paramètres

```python
FACE_TOLERANCE = 0.5          # Plus bas = plus strict (0.4 à 0.6)
GESTURE_CONFIRM_SECONDS = 2.0  # Durée de maintien du geste
TARGET_FPS = 15                # FPS du thread caméra
RAISED_HAND_THRESHOLD = 0.4    # y normalisé < 0.4 = main levée
MAX_HANDS = 4                  # MediaPipe max_num_hands
SMOOTHING_FRAMES = 5           # Frames pour lissage du comptage
```

## Structure d'un Résultat d'Identification

```python
# Retour de FaceEngine.identify(frame)
[
  {
    "name": "Alice Dupont",      # "Unknown" si non reconnu
    "location": (50, 200, 150, 100),  # (top, right, bottom, left)
    "confidence": 0.87,          # 1 - distance (plus proche de 1 = meilleur)
    "user_id": 3                 # None si Unknown
  }
]
```

## Structure d'un Résultat de Geste

```python
# Retour de GestureEngine.detect_raised_hand(frame)
[
  {
    "hand_index": 0,
    "is_raised": True,
    "wrist_y": 0.23,       # coordonnée y normalisée (0=haut, 1=bas)
    "confirmed": False     # True si maintenu > GESTURE_CONFIRM_SECONDS
  }
]
```

## Débogage Courant

```bash
# Tester la caméra directement
python -c "import cv2; cap=cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'ERREUR')"

# Tester face_recognition
python -c "import face_recognition; print('face_recognition OK')"

# Tester mediapipe
python -c "import mediapipe as mp; print('mediapipe OK')"

# Voir la BDD
sqlite3 data/attendance.db ".tables"
sqlite3 data/attendance.db "SELECT * FROM attendance ORDER BY timestamp DESC LIMIT 10;"
```
