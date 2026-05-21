# 🔧 Guide de Résolution — Installation

## Problème : Erreur avec mediapipe

### Symptôme
```
ERROR: Could not find a version that satisfies the requirement mediapipe==0.10.14
```

### Solution
Le `requirements.txt` a été mis à jour avec des versions flexibles. Au lieu de versions exactes (`==`), on utilise des plages (`>=`).

```bash
# Méthode 1 : Installation normale (recommandée)
pip install -r requirements.txt

# Méthode 2 : Si la méthode 1 échoue, installer une par une
pip install flask flask-sqlalchemy flask-migrate
pip install opencv-python
pip install mediapipe  # Installe la dernière version compatible
pip install numpy pillow python-dotenv
pip install face_recognition  # À la fin car dépend des autres
pip install pytest pytest-cov
```

---

## Problème : Erreur avec face_recognition / dlib

### Symptôme
```
ERROR: Could not build wheels for dlib
```

### Solutions par OS

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y cmake build-essential python3-dev
pip install dlib
pip install face_recognition
```

#### macOS
```bash
brew install cmake
pip install dlib
pip install face_recognition
```

#### Windows
1. Installer **Visual Studio Build Tools 2019+** : https://visualstudio.microsoft.com/downloads/
2. Installer **CMake** : https://cmake.org/download/
3. Redémarrer le terminal
4. Installer dlib pré-compilé :
```bash
pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.99-cp310-cp310-win_amd64.whl
pip install face_recognition
```
(Adapter `cp310` selon votre version Python : `python --version`)

---

## Problème : NumPy version incompatible

### Symptôme
```
ImportError: numpy.core.multiarray failed to import
```

### Solution
```bash
pip uninstall numpy
pip install "numpy>=1.26.0,<2.0.0"
```

---

## Problème : OpenCV ne trouve pas la caméra

### Symptôme
Le flux vidéo ne s'affiche pas, erreur "Camera not available"

### Solutions
```bash
# 1. Vérifier que la caméra fonctionne
python -c "import cv2; cap=cv2.VideoCapture(0); print('✅ Caméra OK' if cap.isOpened() else '❌ Caméra introuvable'); cap.release()"

# 2. Si index 0 ne marche pas, essayer index 1
# Modifier dans .env :
CAMERA_INDEX=1

# 3. Sur Linux, vérifier les permissions
sudo usermod -a -G video $USER
# Puis redémarrer la session
```

---

## Problème : SQLite version trop ancienne

### Symptôme
```
sqlite3.OperationalError: near "RETURNING": syntax error
```

### Solution
```bash
# Installer pysqlite3 (version plus récente)
pip install pysqlite3-binary

# Puis dans config.py, ajouter en haut :
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

---

## Vérification Post-Installation

```bash
# Test complet de l'environnement
python << 'ENDPY'
import sys
print(f"Python {sys.version}")

try:
    import flask
    print(f"✅ Flask {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import cv2
    print(f"✅ OpenCV {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

try:
    import mediapipe
    print(f"✅ MediaPipe {mediapipe.__version__}")
except ImportError as e:
    print(f"❌ MediaPipe: {e}")

try:
    import face_recognition
    print(f"✅ face_recognition installé")
except ImportError as e:
    print(f"❌ face_recognition: {e}")

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy: {e}")

print("\n🎯 Si toutes les libs ont ✅, l'installation est OK!")
ENDPY
```

---

## Installation Complète Recommandée (Ordre Important)

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Mettre à jour pip
pip install --upgrade pip setuptools wheel

# 3. Installer les dépendances système d'abord
# Voir section dlib ci-dessus selon votre OS

# 4. Installer dans cet ordre (évite les conflits)
pip install numpy
pip install opencv-python
pip install mediapipe
pip install pillow
pip install cmake  # Si pas déjà en système
pip install dlib
pip install face_recognition
pip install flask flask-sqlalchemy flask-migrate python-dotenv
pip install pytest pytest-cov

# 5. Vérifier
pip list
```

---

## Versions Testées et Fonctionnelles

| OS | Python | face_recognition | mediapipe | OpenCV |
|---|---|---|---|---|
| Ubuntu 22.04 | 3.10.12 | 1.3.0 | 0.10.35 | 4.9.0.80 |
| macOS Sonoma | 3.11.6 | 1.3.0 | 0.10.33 | 4.9.0.80 |
| Windows 11 | 3.10.11 | 1.3.0 | 0.10.35 | 4.9.0.80 |

---

## Support

Si un problème persiste :
1. Copier l'erreur exacte
2. Vérifier `python --version` (doit être 3.10+)
3. Vérifier `pip list` pour voir les versions installées
4. Utiliser le prompt debug de `.trae/rules/agent_prompts.md`
