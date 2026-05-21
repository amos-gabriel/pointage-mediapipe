# Règles Projet — Système de Pointage Facial & Gestuel

## 🎯 Contexte du Projet
Projet de Master 2 — Système de pointage automatique basé sur :
1. **Reconnaissance faciale** : identification de la personne
2. **Détection de geste** : levée de main = marquage présent
3. **Comptage de personnes** : interface dédiée au comptage temps réel

Stack principale : **Python + Flask + OpenCV + MediaPipe + face_recognition + SQLite**

---

## 📐 Architecture Imposée

```
pointage-facial/
├── app/
│   ├── __init__.py          # Factory Flask (create_app)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # Modèle utilisateur / étudiant
│   │   └── attendance.py    # Modèle pointage
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # Routes principales
│   │   ├── attendance.py    # Interface 1 : pointage
│   │   └── counting.py      # Interface 2 : comptage
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── face_engine.py   # Reconnaissance faciale (face_recognition)
│   │   ├── gesture_engine.py# Détection geste main levée (MediaPipe)
│   │   └── camera.py        # Gestion flux vidéo OpenCV
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── attendance.html  # Interface 1
│       └── counting.html    # Interface 2
├── data/
│   ├── known_faces/         # Photos d'enregistrement (une par personne)
│   └── attendance.db        # Base SQLite
├── tests/
├── scripts/
│   └── register_face.py     # Script d'enrôlement
├── config.py
├── run.py
├── requirements.txt
└── .env.example
```

---

## 🧠 Règles de Code

### Python / Flask
- Python **3.10+** obligatoire
- Utiliser **Flask Application Factory** (`create_app()`)
- **SQLAlchemy** pour l'ORM, migrations via **Flask-Migrate**
- Séparation stricte : logique métier dans `utils/`, routes minces dans `routes/`
- Toutes les fonctions doivent avoir des **docstrings** en français
- **Type hints** obligatoires sur toutes les fonctions
- Gestion des erreurs avec `try/except` explicite, jamais de `except: pass`
- Variables d'environnement via `.env` (python-dotenv), jamais de secrets en dur

### OpenCV / Traitement Vidéo
- Le flux caméra doit tourner dans un **thread dédié** (`threading.Thread`)
- Utiliser `cv2.VideoCapture(0)` avec fallback sur index 1
- Frame rate cible : **15 FPS** pour ne pas surcharger le CPU
- **Toujours libérer** la caméra (`cap.release()`) dans un bloc `finally`
- Les frames MJPEG pour le streaming Flask : `yield` via generator

### Reconnaissance Faciale (`face_engine.py`)
- Bibliothèque : `face_recognition` (dlib backend)
- Encodages pré-calculés au **démarrage** de l'app (pas à chaque frame)
- Seuil de tolérance : **0.5** (ajustable dans `config.py`)
- Si plusieurs visages détectés, traiter **chacun indépendamment**
- Retourner `Unknown` si aucun match, ne jamais lever d'exception silencieuse
- Mise en cache des encodages dans un dictionnaire `{nom: encoding}`

### Détection de Geste (`gesture_engine.py`)
- Bibliothèque : `mediapipe` (Hands solution)
- Geste "main levée" = poignet (**landmark 0**) au-dessus de l'épaule détectée OU haut du frame (y < 0.4)
- Logique de confirmation : geste maintenu **2 secondes consécutives** avant pointage
- Utiliser un timer par personne détectée pour éviter les faux positifs
- `mp.solutions.hands` avec `max_num_hands=4`

### Base de Données
- SQLite pour le développement, PostgreSQL-compatible en production
- Table `users` : id, nom, prenom, matricule (unique), face_encoding (BLOB), created_at
- Table `attendance` : id, user_id (FK), timestamp, status ('present'), confidence_score
- **Index** sur `user_id` et `timestamp` dans attendance
- Ne jamais stocker d'images dans la BDD, seulement les encodages

### Interface Web
- **Interface 1 (Pointage)** : flux vidéo temps réel, overlay des noms détectés, confirmation visuelle quand main levée, liste des présences du jour
- **Interface 2 (Comptage)** : flux vidéo, compteur en temps réel (nombre de personnes dans le frame), historique
- Streaming vidéo via **Server-Sent Events (SSE)** ou **MJPEG stream** (`/video_feed`)
- UI responsive, Bootstrap 5 ou Tailwind CSS
- Rafraîchissement de la liste des présences : **polling AJAX toutes les 3 secondes**

---

## 🚫 Interdictions Strictes

- Ne jamais bloquer le thread principal Flask avec OpenCV
- Ne jamais commit des fichiers `.env` ou `attendance.db`
- Ne pas utiliser `flask run` en production (utiliser `gunicorn`)
- Ne pas mélanger la logique de détection dans les routes Flask
- Ne pas stocker les mots de passe en clair (même si pas d'auth dans ce projet)
- Ne jamais ignorer les erreurs de caméra non disponible

---

## ✅ Checklist Avant Commit

- [ ] `requirements.txt` à jour (`pip freeze > requirements.txt`)
- [ ] Aucune clé / secret dans le code source
- [ ] Tests unitaires pour `face_engine` et `gesture_engine`
- [ ] README à jour avec instructions d'installation
- [ ] Flux vidéo testé avec 2+ personnes simultanées
- [ ] Pointage bien enregistré en BDD et visible dans l'interface

---

## 🎬 Démo Vidéo (5 min max)
Scénario à couvrir :
1. (0:00-0:30) Lancer l'application, montrer les 2 interfaces
2. (0:30-2:00) Interface Pointage : personne connue détectée → lève la main → confirmé présent
3. (2:00-2:30) Interface Pointage : personne détectée mais ne lève PAS la main → non pointé
4. (2:30-3:30) Interface Comptage : montrer le comptage dynamique avec 1, 2, 3 personnes
5. (3:30-5:00) Base de données : afficher les enregistrements, montrer la liste des présences
