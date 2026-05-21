import mediapipe as mp
import cv2
import time
import numpy as np
from typing import List, Dict, Any

class GestureEngine:
    """
    Moteur de détection de geste utilisant MediaPipe Hands.
    """
    def __init__(self, max_hands: int = 4, confirm_seconds: float = 2.0):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.confirm_seconds = confirm_seconds
        self.timers = {}  # {user_id: start_time}

    def detect_raised_hand(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Détecte les mains levées dans un frame.
        Logique : poignet (landmark 0) y < 0.4.
        """
        if frame is None or frame.size == 0:
            return []

        # Convertir BGR en RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        raised_hands = []
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Landmark 0 est le poignet
                wrist_y = hand_landmarks.landmark[0].y
                is_raised = wrist_y < 0.5
                
                print(f"Main {i} détectée - Poignet Y: {wrist_y:.2f} - Levée: {is_raised}")
                
                raised_hands.append({
                    "hand_index": i,
                    "is_raised": is_raised,
                    "wrist_y": float(wrist_y)
                })
                
        return raised_hands

    def check_gesture_confirmed(self, user_id: int, is_raised: bool) -> bool:
        """
        Gère un timer par utilisateur pour confirmer le geste.
        Retourne True si le geste est maintenu pendant confirm_seconds.
        """
        if user_id is None:
            return False

        now = time.time()
        
        if is_raised:
            if user_id not in self.timers:
                self.timers[user_id] = now
            
            elapsed = now - self.timers[user_id]
            if elapsed >= self.confirm_seconds:
                # Geste confirmé, on peut réinitialiser ou laisser pour éviter les doublons immédiats
                # Ici on retourne True, l'appelant gérera le pointage unique
                return True
        else:
            # Si la main redescend, on réinitialise le timer
            if user_id in self.timers:
                del self.timers[user_id]
                
        return False

    def reset_timer(self, user_id: int):
        """Réinitialise le timer pour un utilisateur."""
        if user_id in self.timers:
            del self.timers[user_id]
