import cv2
import threading
import time
import numpy as np
from typing import Optional, List, Dict, Any

class CameraStream:
    """
    Gestion du flux vidéo OpenCV dans un thread séparé.
    """
    def __init__(self, camera_index: int = 0, target_fps: int = 15):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None
        self.current_frame = None
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        """Démarre le thread de capture."""
        if self.is_running:
            return
        
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            # Fallback sur l'index 1
            self.cap = cv2.VideoCapture(1)
            if not self.cap.isOpened():
                raise RuntimeError("Impossible d'ouvrir la caméra.")

        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Arrête proprement la capture."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()

    def _capture_loop(self):
        """Boucle de capture interne."""
        delay = 1.0 / self.target_fps
        while self.is_running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame.copy()
            
            # Respecter le FPS cible
            elapsed = time.time() - start_time
            if elapsed < delay:
                time.sleep(delay - elapsed)

    def get_frame(self) -> Optional[np.ndarray]:
        """Retourne le dernier frame capturé."""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def get_jpeg_frame(self, frame: Optional[np.ndarray] = None) -> Optional[bytes]:
        """Encode un frame en JPEG."""
        if frame is None:
            frame = self.get_frame()
        
        if frame is not None:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                return buffer.tobytes()
        return None

    @staticmethod
    def draw_overlays(frame: np.ndarray, face_results: List[Dict[str, Any]], gesture_confirmed_ids: List[int] = None):
        """
        Dessine les rectangles et noms sur le frame.
        Couleurs : vert=#00C851 pointé, orange=#FF8800 détecté, rouge=#FF4444 inconnu
        """
        if gesture_confirmed_ids is None:
            gesture_confirmed_ids = []

        for res in face_results:
            top, right, bottom, left = res['location']
            name = res['name']
            user_id = res['user_id']
            
            # Déterminer la couleur
            if user_id in gesture_confirmed_ids:
                color = (81, 200, 0)  # Vert (BGR)
                label = f"{name} - ✅ Pointé"
            elif name != "Unknown":
                color = (0, 136, 255)  # Orange (BGR)
                label = f"{name} ({int(res['confidence']*100)}%)"
            else:
                color = (68, 68, 255)  # Rouge (BGR)
                label = "Inconnu"

            # Dessiner le rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Dessiner le label
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

        return frame

    @staticmethod
    def draw_count_overlay(frame: np.ndarray, count: int):
        """Dessine le compteur sur le frame."""
        h, w, _ = frame.shape
        # Fond semi-transparent pour le texte
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (250, 70), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        cv2.putText(frame, f"Personnes : {count}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    @staticmethod
    def generate_mjpeg(camera_stream, face_engine=None, gesture_engine=None, mode='attendance'):
        """Générateur pour le flux MJPEG Flask."""
        while True:
            frame = camera_stream.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            if mode == 'attendance' and face_engine:
                # Identifier les visages
                face_results = face_engine.identify(frame)
                
                # Détecter les gestes si nécessaire (l'orchestration peut être faite ici ou ailleurs)
                # Pour le flux vidéo, on dessine juste les résultats actuels
                frame = CameraStream.draw_overlays(frame, face_results)
            
            elif mode == 'counting' and face_engine:
                count = face_engine.count_faces(frame)
                frame = CameraStream.draw_count_overlay(frame, count)

            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            time.sleep(0.05) # ~20 FPS pour le stream
