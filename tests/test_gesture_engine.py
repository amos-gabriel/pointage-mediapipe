import pytest
import time
from app.utils.gesture_engine import GestureEngine

def test_gesture_engine_timer():
    engine = GestureEngine(confirm_seconds=0.1)
    user_id = 1
    
    # Pas de geste au début
    assert engine.check_gesture_confirmed(user_id, False) == False
    
    # Geste commence
    assert engine.check_gesture_confirmed(user_id, True) == False
    
    # Attendre un peu
    time.sleep(0.15)
    
    # Geste confirmé
    assert engine.check_gesture_confirmed(user_id, True) == True
    
    # Geste s'arrête
    assert engine.check_gesture_confirmed(user_id, False) == False
    assert user_id not in engine.timers
