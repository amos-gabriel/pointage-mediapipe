# Prompts Agent TRAE — Prêts à l'emploi

## Comment utiliser ce fichier
Copier-coller le prompt correspondant dans TRAE, en ajoutant le contexte de code existant si nécessaire.

---

## 🔧 Prompt 1 — Créer le Moteur de Reconnaissance Faciale

```
Contexte : Je développe un système de pointage Flask avec reconnaissance faciale.
Règles du projet dans .trae/rules/project_rules.md et coding_standards.md.

Tâche : Crée le fichier `app/utils/face_engine.py` avec la classe `FaceEngine`.

Exigences :
- Méthode `load_known_faces(directory: str) -> int` : charge les encodages depuis un dossier, 
  retourne le nombre de visages chargés. Les fichiers sont nommés "Prenom_Nom.jpg"
- Méthode `identify(frame: np.ndarray) -> list[dict]` : identifie les visages dans un frame BGR OpenCV.
  Retourne [{"name": str, "location": (top, right, bottom, left), "confidence": float}]
- Méthode `encode_face(image_path: str) -> np.ndarray | None`
- Méthode `count_faces(frame: np.ndarray) -> int` : compte seulement, sans identifier
- Seuil de tolérance configurable (défaut 0.5)
- Encodages mis en cache au chargement initial
- Docstrings en français, type hints obligatoires
- Gestion des erreurs explicite

Fichiers liés existants : config.py (ci-dessous)
[COLLER LE CONTENU DE config.py ICI]
```

---

## 🤚 Prompt 2 — Créer le Moteur de Détection de Geste

```
Contexte : Système de pointage Flask. La reconnaissance faciale est déjà implémentée dans face_engine.py.

Tâche : Crée `app/utils/gesture_engine.py` avec la classe `GestureEngine`.

Exigences :
- Utiliser `mediapipe.solutions.hands` avec max_num_hands=4
- Méthode `detect_raised_hand(frame: np.ndarray) -> list[dict]` :
  Retourne [{"hand_index": int, "is_raised": bool, "wrist_y": float}]
- Logique "main levée" : landmark 0 (poignet) avec coordonnée y normalisée < 0.4
- Méthode `check_gesture_confirmed(person_id: str, is_raised: bool) -> bool` :
  Gère un timer par personne, retourne True uniquement si le geste est maintenu 2 secondes
- Réinitialiser le timer si la main redescend
- Utiliser `time.time()` pour les timers, stocker dans un dict {person_id: start_time}
- Docstrings en français, type hints

Contenu de face_engine.py pour référence :
[COLLER LE CONTENU DE face_engine.py ICI]
```

---

## 📹 Prompt 3 — Créer le Stream Caméra Thread-Safe

```
Contexte : Flask app, face_engine.py et gesture_engine.py sont prêts.

Tâche : Crée `app/utils/camera.py` avec la classe `CameraStream`.

Exigences :
- Thread daemon séparé pour la capture (threading.Thread)
- threading.Lock() pour protéger current_frame
- Méthode `start()` : démarre le thread de capture
- Méthode `stop()` : arrête proprement avec cap.release() dans finally
- Méthode `get_frame() -> bytes | None` : retourne le frame JPEG encodé
- Méthode `get_annotated_frame(face_results, gesture_results) -> bytes` : 
  dessine les overlays (rectangles, noms, icônes geste)
- Couleurs overlay : vert=#00C851 pointé, orange=#FF8800 détecté, rouge=#FF4444 inconnu
- Essayer d'abord camera_index=0, fallback sur 1 si échec
- Target FPS configurable (défaut 15)
- Méthode statique `generate_mjpeg(stream_instance)` : générateur yield pour Flask

Les overlays doivent afficher :
- Rectangle coloré autour du visage
- Nom + confidence en % au-dessus
- "✋ Confirmation..." si geste en cours
- "✅ Pointé" si vient d'être enregistré (pendant 3s)
```

---

## 🗄️ Prompt 4 — Créer les Modèles et le Service de Pointage

```
Contexte : Flask app avec SQLAlchemy. Voir config.py et la structure des modèles dans docs/architecture.md.

Tâche : Crée les fichiers suivants :

1. `app/models/user.py` — classe User (SQLAlchemy Model)
   - id, nom, prenom, matricule (unique), face_encoding (LargeBinary), photo_path, created_at
   - Méthode `get_encoding()` : désérialise le BLOB en np.ndarray via pickle
   - Méthode `set_encoding(encoding: np.ndarray)` : sérialise via pickle

2. `app/models/attendance.py` — classe Attendance
   - id, user_id (FK), timestamp, status, confidence_score
   - Index sur (user_id, timestamp)
   - Méthode de classe `get_today(user_id)` : retourne le pointage du jour si existe
   - Méthode de classe `get_all_today()` : tous les pointages du jour

3. `app/utils/attendance_service.py` — classe AttendanceService
   - Méthode statique `mark_present(user_id: int, confidence: float) -> Attendance | None`
     → Vérifie si déjà pointé aujourd'hui, si non crée l'entrée, retourne None si doublon
   - Méthode statique `get_today_summary() -> list[dict]`
   - Méthode statique `export_csv(date: str) -> str` : retourne le CSV comme string

Utiliser pickle pour sérialiser les np.ndarray (face_encoding).
```

---

## 🌐 Prompt 5 — Créer les Routes Flask Interface 1 (Pointage)

```
Contexte : Tous les utils et modèles sont prêts. Voir le code dans app/utils/ et app/models/.

Tâche : Crée `app/routes/attendance.py` — Blueprint Flask "attendance"

Routes à implémenter :
- GET  /attendance           → render_template('attendance.html')
- GET  /video_feed           → Response MJPEG depuis CameraStream
- GET  /api/today-attendance → JSON liste des présences du jour
- POST /api/mark-present     → body: {user_id, confidence} → enregistre via AttendanceService

Le thread d'orchestration (dans ce fichier ou app/__init__.py) :
- Tourne en arrière-plan
- Chaque frame : face_engine.identify() → gesture_engine.detect_raised_hand()
- Si geste confirmé ET pas déjà pointé → AttendanceService.mark_present()
- Met à jour current_detections (protégé par lock)

Template attendance.html doit avoir :
- <img src="/video_feed" style="width:100%">
- Div liste rafraîchie toutes les 3s par fetch('/api/today-attendance')
- Design Bootstrap 5, couleurs : bleu marine #1a237e, accent vert #00C851
```

---

## 🔢 Prompt 6 — Créer l'Interface Comptage

```
Contexte : Interface 1 (pointage) est fonctionnelle.

Tâche : Crée `app/routes/counting.py` et `app/templates/counting.html`

Routes :
- GET /counting           → render_template('counting.html')
- GET /video_feed_count   → MJPEG avec compteur dessiné sur le frame
- GET /api/current-count  → JSON {"count": N, "timestamp": "ISO"}

Logique comptage :
- Utiliser face_recognition.face_locations() seulement (pas d'identification)
- Lissage : conserver les 5 derniers counts, retourner la médiane
- Écrire le compteur sur le frame : gros texte blanc avec fond noir semi-transparent

Template counting.html :
- Flux vidéo à gauche
- Grand compteur numérique à droite (style dashboard)
- Graphique Chart.js ligne (polling /api/current-count toutes les 2s)
- Historique des 20 dernières mesures dans le graphique
- Même header/footer que attendance.html (extends base.html)
```

---

## 🧪 Prompt 7 — Générer les Tests Unitaires

```
Contexte : Tous les fichiers utils sont prêts (face_engine.py, gesture_engine.py, camera.py).

Tâche : Crée les fichiers de tests suivants :

1. `tests/test_face_engine.py`
   - Test : frame vide → retourne []
   - Test : frame None → lève ValueError
   - Test : identify avec visage mock → vérifie structure du retour
   - Test : load_known_faces sur dossier vide → retourne 0

2. `tests/test_gesture_engine.py`
   - Test : main levée (landmark y=0.2) → is_raised=True
   - Test : main basse (landmark y=0.7) → is_raised=False
   - Test : check_gesture_confirmed avant 2s → retourne False
   - Test : réinitialisation timer si main baisse

3. `tests/test_attendance_service.py`
   - Test : mark_present → entrée créée en BDD
   - Test : double pointage même jour → retourne None au 2e appel
   - Test : get_today_summary → liste correcte

Utiliser pytest, fixtures pour la BDD de test (SQLite in-memory), 
mocks pour OpenCV et mediapipe (éviter dépendances hardware dans les tests).
```

---

## 🐛 Prompt Debug — Résoudre un Problème

```
Contexte : Système de pointage Flask avec face_recognition et mediapipe.

Problème : [DÉCRIRE L'ERREUR ICI]

Traceback complet :
[COLLER LE TRACEBACK ICI]

Fichiers concernés :
[COLLER LE CODE DU/DES FICHIER(S) ICI]

Règles du projet : voir .trae/rules/project_rules.md

Analyser l'erreur et proposer un fix minimal qui respecte l'architecture existante.
Ne pas réécrire les fichiers entiers sauf si nécessaire.
```
