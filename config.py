import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "data", "attendance.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Vision
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    TARGET_FPS = int(os.environ.get('TARGET_FPS', 15))
    FACE_TOLERANCE = float(os.environ.get('FACE_TOLERANCE', 0.4))
    GESTURE_CONFIRM_SECONDS = float(os.environ.get('GESTURE_CONFIRM_SECONDS', 2.0))
    KNOWN_FACES_DIR = os.path.join(BASE_DIR, 'app', 'static', 'known_faces')
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
