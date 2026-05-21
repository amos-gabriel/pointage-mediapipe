# 🎓 Système de Pointage Facial & Gestuel
### Projet Master 2 — Traitement d'Images & IA

Système de présence automatique combinant **reconnaissance faciale** et **détection de geste** (main levée), développé avec Flask, OpenCV, MediaPipe et face_recognition.

---

## ✨ Fonctionnalités

| Feature | Statut |
|---|---|
| Détection et identification de visages en temps réel | ✅ |
| Pointage automatique par levée de main | ✅ |
| Interface de comptage de personnes | ✅ |
| Enregistrement en base de données SQLite | ✅ |
| Flux vidéo MJPEG avec overlays | ✅ |
| Historique et export CSV | ✅ |

---

## 🛠️ Stack Technologique

- **Backend** : Python 3.10+, Flask 3.0
- **Vision** : OpenCV 4.9, MediaPipe 0.10, face_recognition 1.3
- **Base de données** : SQLite (SQLAlchemy + Flask-Migrate)
- **Frontend** : HTML/CSS/JS, Bootstrap 5, Chart.js

---

## 🚀 Installation

### Prérequis Système
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install cmake build-essential python3-dev

# macOS
brew install cmake

# Windows — Installer CMake depuis https://cmake.org + Visual Studio Build Tools
```

### Installation Python
```bash
# 1. Cloner le projet
git clone <repo-url>
cd pointage-facial

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env selon vos besoins

# 5. Initialiser la base de données
flask db upgrade

# 6. Lancer l'application
python run.py
```

Ouvrir `http://localhost:5000` dans le navigateur.

---

## 👤 Enrôlement d'une Personne

```bash
python scripts/register_face.py --nom "Dupont" --prenom "Alice" --matricule "M2-001"
# La webcam s'ouvre → regarder droit → appuyer sur 'c' pour capturer
```

Ou avec une photo existante :
```bash
python scripts/register_face.py --nom "Dupont" --prenom "Alice" --matricule "M2-001" --photo chemin/photo.jpg
```

---

## 📱 Interfaces

### Interface 1 — Pointage (`/attendance`)
- Détecte les visages et les identifie
- Attend que la personne **lève la main** pendant **2 secondes**
- Enregistre automatiquement la présence
- Affiche en temps réel la liste des personnes pointées

### Interface 2 — Comptage (`/counting`)
- Compte le nombre de personnes visibles (sans identification)
- Affiche un graphique d'évolution en temps réel
- Utile pour la gestion de capacité de salle

### Administration (`/admin`)
- Liste des utilisateurs enrôlés
- Historique des pointages
- Export CSV

---

## ⚙️ Configuration (`.env`)

```env
SECRET_KEY=votre-cle-secrete-ici
DATABASE_URL=sqlite:///data/attendance.db
CAMERA_INDEX=0
TARGET_FPS=15
FACE_TOLERANCE=0.5
GESTURE_CONFIRM_SECONDS=2.0
KNOWN_FACES_DIR=data/known_faces
```

---

## 🧪 Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

---

## 📁 Structure du Projet

```
pointage-facial/
├── .trae/rules/          # Règles et tâches pour l'agent TRAE
├── app/
│   ├── models/           # Modèles SQLAlchemy
│   ├── routes/           # Routes Flask
│   ├── utils/            # Moteurs vision (face, gesture, camera)
│   ├── templates/        # Templates Jinja2
│   └── static/           # CSS, JS
├── data/
│   ├── known_faces/      # Photos d'enrôlement
│   └── attendance.db     # Base SQLite (auto-créée)
├── docs/                 # Documentation technique
├── scripts/              # Scripts utilitaires
├── tests/                # Tests unitaires
├── config.py
├── run.py
└── requirements.txt
```

---

## 🎬 Démo

Voir `docs/demo_script.md` pour le script détaillé de la vidéo de démonstration (5 minutes).

---

## 👥 Auteurs

Projet réalisé dans le cadre du Master 2 — Année 2024-2025

---

## 📄 Licence

Usage académique uniquement.
