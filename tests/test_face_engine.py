import pytest
import numpy as np
from app.utils.face_engine import FaceEngine

def test_face_engine_empty_frame():
    engine = FaceEngine()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    result = engine.identify(blank)
    assert result == []

def test_face_engine_none_frame():
    engine = FaceEngine()
    with pytest.raises(ValueError):
        engine.identify(None)

def test_face_engine_count_empty():
    engine = FaceEngine()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    assert engine.count_faces(blank) == 0
