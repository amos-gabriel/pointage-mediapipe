# Plan d'Implémentation — Tâches Agent TRAE

## Mode d'utilisation
Ce fichier est lu par l'agent TRAE pour exécuter les tâches dans l'ordre.
Chaque tâche est **atomique** : l'agent doit la compléter avant de passer à la suivante.
Statuts : `[ ]` À faire · `[→]` En cours · `[x]` Terminé · `[!]` Bloqué

---

## Phase 0 — Initialisation du Projet
- [ ] **T0.1** Créer l'environnement virtuel Python : `python -m venv venv`
- [ ] **T0.2** Installer les dépendances de base (voir `requirements.txt`)
- [ ] **T0.3** Créer la structure de dossiers complète définie dans `project_rules.md`
- [ ] **T0.4** Initialiser la base SQLite et les migrations Flask-Migrate
- [ ] **T0.5** Vérifier que `python run.py` démarre sans erreur

## Phase 1 — Modèles de Données
- [ ] **T1.1** Créer `app/models/user.py` avec le modèle `User`
  - Champs : id, nom, prenom, matricule (unique, indexed), face_encoding (LargeBinary), created_at
- [ ] **T1.2** Créer `app/models/attendance.py` avec le modèle `Attendance`
  - Champs : id, user_id (FK→users.id), timestamp, status, confidence_score
  - Index composite sur (user_id, timestamp)
- [ ] **T1.3** Générer et appliquer la migration initiale
- [ ] **T1.4** Tester la création / lecture en BDD avec un script de vérification

## Phase 2 — Moteur de Reconnaissance Faciale
- [ ] **T2.1** Créer `app/utils/face_engine.py` — classe `FaceEngine`
  - Méthode `load_known_faces(directory: str)` : charge tous les encodages depuis `data/known_faces/`
  - Méthode `identify(frame: np.ndarray) -> list[dict]` : retourne les personnes détectées
  - Méthode `encode_face(image_path: str) -> np.ndarray | None`
- [ ] **T2.2** Créer `scripts/register_face.py` : script CLI pour enrôler une nouvelle personne
  - Prend une photo via webcam ou chemin d'image
  - Enregistre l'encodage en BDD ET la photo dans `data/known_faces/`
- [ ] **T2.3** Tester avec 2-3 visages connus, vérifier identification correcte

## Phase 3 — Moteur de Détection de Geste
- [ ] **T3.1** Créer `app/utils/gesture_engine.py` — classe `GestureEngine`
  - Méthode `init_hands()` : initialise `mp.solutions.hands`
  - Méthode `detect_raised_hand(frame: np.ndarray, face_locations: list) -> list[bool]`
  - Logique : poignet landmark 0 avec y < 0.4 (relatif au frame) = main levée
  - Timer de confirmation : 2 secondes maintenues → retourne `True`
- [ ] **T3.2** Tester la détection indépendamment avec un script de test visuel

## Phase 4 — Gestion du Flux Vidéo
- [ ] **T4.1** Créer `app/utils/camera.py` — classe `CameraStream`
  - Thread dédié pour la capture (évite le blocage Flask)
  - Méthode `get_frame() -> bytes` : retourne le frame JPEG encodé
  - Méthode `get_annotated_frame() -> bytes` : frame avec overlays dessinés
  - `start()` / `stop()` avec gestion `finally` pour `cap.release()`
- [ ] **T4.2** Créer le generator Flask pour MJPEG streaming
- [ ] **T4.3** Tester le streaming sur `http://localhost:5000/video_feed`

## Phase 5 — Interface 1 : Pointage
- [ ] **T5.1** Créer `app/routes/attendance.py`
  - `GET /attendance` : page principale interface pointage
  - `GET /video_feed` : stream MJPEG avec overlays
  - `POST /api/mark-present` : enregistre un pointage (appelé automatiquement)
  - `GET /api/today-attendance` : liste des présences du jour (JSON)
- [ ] **T5.2** Créer `app/templates/attendance.html`
  - Zone vidéo (balise `<img>` pointant vers `/video_feed`)
  - Liste temps réel des personnes pointées (rafraîchie toutes les 3s)
  - Indicateur visuel : vert = pointé, orange = détecté mais pas de geste
  - Pas de bouton manuel : tout est automatique
- [ ] **T5.3** Implémenter la logique d'orchestration dans le thread caméra :
  - Frame → FaceEngine.identify() → pour chaque visage → GestureEngine.detect_raised_hand()
  - Si main levée + personne identifiée + pas déjà pointé aujourd'hui → POST /api/mark-present
- [ ] **T5.4** Tester scénario complet : personne connue + main levée → présent en BDD

## Phase 6 — Interface 2 : Comptage
- [ ] **T6.1** Créer `app/routes/counting.py`
  - `GET /counting` : page interface comptage
  - `GET /video_feed_count` : stream MJPEG avec compteur dessiné
  - `GET /api/current-count` : JSON `{"count": N, "timestamp": "..."}`
- [ ] **T6.2** Créer `app/templates/counting.html`
  - Grand compteur numérique affiché en overlay ET dans l'UI
  - Graphique temps réel (Chart.js) de l'évolution du nombre
  - Pas d'identification des personnes dans cette interface
- [ ] **T6.3** Implémenter le comptage : `len(face_locations)` par frame, lissage sur 5 frames
- [ ] **T6.4** Tester avec 1, 2, 3 personnes devant la caméra

## Phase 7 — Interface d'Administration (Bonus)
- [ ] **T7.1** `GET /admin` : liste tous les utilisateurs enrôlés
- [ ] **T7.2** `GET /admin/history` : historique complet des pointages (filtrable par date)
- [ ] **T7.3** Export CSV des présences du jour

## Phase 8 — Tests & Qualité
- [ ] **T8.1** Tests unitaires `tests/test_face_engine.py`
- [ ] **T8.2** Tests unitaires `tests/test_gesture_engine.py`
- [ ] **T8.3** Test d'intégration : enrôlement → détection → pointage → BDD
- [ ] **T8.4** `pytest --cov=app tests/` — couverture > 60%

## Phase 9 — Préparation Démo
- [ ] **T9.1** Enrôler 3 personnes minimum dans le système
- [ ] **T9.2** Vérifier que l'interface fonctionne sans crash pendant 10 minutes
- [ ] **T9.3** Préparer le script de démo (voir `docs/demo_script.md`)
- [ ] **T9.4** Enregistrer la vidéo de démo (OBS Studio recommandé, 1080p)

---

## Dépendances entre Tâches

```
T0 → T1 → T2 → T4 → T5
              ↘ T3 ↗
T5 → T6 → T7 → T8 → T9
```

## Contexte à Fournir à l'Agent pour Chaque Tâche

Avant de demander à l'agent de réaliser une tâche, inclure :
1. Le contenu de `project_rules.md` et `coding_standards.md`
2. Le code existant des fichiers dépendants
3. Le message d'erreur exact si c'est un bug fix
