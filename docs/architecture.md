# Architecture Technique — Système de Pointage Facial

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────┐
│                     NAVIGATEUR WEB                      │
│   ┌──────────────────┐    ┌──────────────────────────┐  │
│   │  Interface 1     │    │  Interface 2             │  │
│   │  /attendance     │    │  /counting               │  │
│   │                  │    │                          │  │
│   │  [Flux Vidéo]    │    │  [Flux Vidéo + Compteur] │  │
│   │  [Liste Présents]│    │  [Graphique Evolution]   │  │
│   └────────┬─────────┘    └────────────┬─────────────┘  │
└────────────┼─────────────────────────┼──────────────────┘
             │ MJPEG Stream            │ MJPEG Stream
             │ AJAX Polling            │ AJAX Polling
┌────────────▼─────────────────────────▼──────────────────┐
│                   FLASK APPLICATION                      │
│                                                          │
│  Routes: /attendance  /counting  /api/*  /admin         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION THREAD                │   │
│  │                                                  │   │
│  │  CameraStream ──► FaceEngine ──► GestureEngine   │   │
│  │       │               │               │         │   │
│  │  Frame capturée   Identités      Main levée?    │   │
│  │                       └───────────────┘         │   │
│  │                               │                 │   │
│  │                       AttendanceService         │   │
│  │                       (mark_present)            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────┐  ┌────────────────────────────┐    │
│  │   SQLAlchemy    │  │    face_recognition         │    │
│  │   SQLite DB     │  │    MediaPipe Hands          │    │
│  │                 │  │    OpenCV                   │    │
│  └─────────────────┘  └────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    WEBCAM (USB)    │
                    └────────────────────┘
```

## Flux de Données — Interface Pointage

```
Webcam
  │
  ▼
CameraStream.get_frame()          [Thread séparé, 15 FPS]
  │
  ├─► Resize frame (640x480)
  │
  ▼
FaceEngine.identify(frame)
  │  - Convertit BGR → RGB
  │  - face_recognition.face_locations()
  │  - face_recognition.face_encodings()
  │  - Compare avec known_encodings (distance euclidienne < 0.5)
  │
  ▼
[{name: "Dupont", location: (y1,x2,y2,x1), confidence: 0.82}, ...]
  │
  ▼
GestureEngine.detect_raised_hand(frame, face_locations)
  │  - mp.solutions.hands.process(frame)
  │  - Pour chaque main détectée : landmark[0].y < 0.4 ?
  │  - Timer : maintenu > 2 secondes ?
  │
  ▼
[True, False, ...]   (une valeur par visage détecté)
  │
  ▼
Pour chaque (person, hand_raised):
  Si hand_raised ET pas déjà pointé aujourd'hui:
    AttendanceService.mark_present(user_id, confidence)
    → INSERT INTO attendance (user_id, timestamp, status, confidence_score)
  │
  ▼
draw_overlays(frame, persons, hand_states)
  │  - Rectangle autour du visage (vert=pointé, orange=détecté, rouge=inconnu)
  │  - Nom au-dessus du rectangle
  │  - Icône ✋ si main levée en cours de confirmation
  │
  ▼
JPEG encode → yield → MJPEG response → <img src="/video_feed">
```

## Flux de Données — Interface Comptage

```
Webcam
  │
  ▼
CameraStream.get_frame()
  │
  ▼
FaceEngine.count_faces(frame)     [Pas d'identification, juste localisation]
  │  - face_recognition.face_locations()
  │  - Retourne len(locations)
  │
  ▼
Lissage : moyenne glissante sur 5 frames
  │
  ▼
draw_count_overlay(frame, count)
  │  - Grand texte : "Personnes : N"
  │  - Rectangle de fond semi-transparent
  │
  ▼
JPEG encode → MJPEG response
  │
  ▼
API /api/current-count → JSON {count, timestamp}
  │
  ▼
Chart.js (polling toutes les 2s) → Graphique évolution
```

## Modèle de Données

```sql
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         VARCHAR(100) NOT NULL,
    prenom      VARCHAR(100) NOT NULL,
    matricule   VARCHAR(50)  NOT NULL UNIQUE,
    face_encoding BLOB,           -- pickle(np.ndarray) de 128 floats
    photo_path  VARCHAR(255),     -- chemin relatif vers data/known_faces/
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    status          VARCHAR(20) DEFAULT 'present',
    confidence_score FLOAT,
    INDEX idx_user_date (user_id, timestamp)
);
```

## Gestion de la Concurrence

Le threading est critique dans ce projet :

```
Thread Principal Flask
    │
    ├── Thread Caméra (daemon=True)
    │       │ Lock: frame_lock (threading.Lock)
    │       └── Lit frames, met à jour: current_frame, current_detections
    │
    ├── Request Thread 1 (/video_feed)
    │       └── Lit current_frame (protégé par frame_lock)
    │
    └── Request Thread 2 (/api/today-attendance)
            └── Lit SQLite (thread-safe avec scoped_session)
```

**Règle** : utiliser `threading.Lock()` pour protéger `current_frame` et `current_detections`.

## Performance et Limites

| Métrique | Cible | Maximum toléré |
|---|---|---|
| FPS caméra | 15 | 30 |
| Latence identification | < 200ms | 500ms |
| Latence geste → pointage | 2s (intentionnel) | 3s |
| RAM consommée | < 500 MB | 1 GB |
| Personnes simultanées | 4 | 6 |

## Dépendances Python

```
flask==3.0.x
flask-sqlalchemy==3.1.x
flask-migrate==4.0.x
opencv-python==4.9.x
face_recognition==1.3.x        # nécessite cmake + dlib
mediapipe==0.10.x
numpy==1.26.x
pillow==10.x
python-dotenv==1.0.x
pytest==8.x
pytest-cov==5.x
```

> ⚠️ `face_recognition` nécessite `dlib` qui nécessite `cmake` et un compilateur C++.
> Sur Windows : installer CMake + Visual Studio Build Tools avant `pip install dlib`.
> Sur Linux/Mac : `sudo apt install cmake` ou `brew install cmake`.
