from flask import Blueprint, render_template, Response, jsonify, current_app
from app.utils.camera import CameraStream
from app.utils.face_engine import FaceEngine
from app.utils.gesture_engine import GestureEngine
from app.utils.attendance_service import AttendanceService
import threading
import time

bp = Blueprint('attendance', __name__)

# Initialisation globale (sera faite au premier accès ou via factory)
camera = None
face_engine = None
gesture_engine = None
orchestration_thread = None
is_running = False

def start_engines():
    global camera, face_engine, gesture_engine, orchestration_thread, is_running
    if is_running:
        return

    face_engine = FaceEngine(tolerance=current_app.config['FACE_TOLERANCE'])
    face_engine.load_known_faces()
    
    gesture_engine = GestureEngine(confirm_seconds=current_app.config['GESTURE_CONFIRM_SECONDS'])
    
    camera = CameraStream(camera_index=current_app.config['CAMERA_INDEX'], 
                         target_fps=current_app.config['TARGET_FPS'])
    camera.start()
    
    is_running = True
    orchestration_thread = threading.Thread(target=orchestration_loop, daemon=True)
    orchestration_thread.start()

def orchestration_loop():
    """Boucle de fond pour identifier et pointer."""
    global camera, face_engine, gesture_engine, is_running
    
    # On a besoin d'un app context pour la BDD
    from run import app
    with app.app_context():
        while is_running:
            frame = camera.get_frame()
            if frame is not None:
                # 1. Identifier les visages
                results = face_engine.identify(frame)
                
                # 2. Détecter les mains levées
                hands = gesture_engine.detect_raised_hand(frame)
                
                # 3. Associer et confirmer (simplifié : si une main est levée, on vérifie les visages détectés)
                # Dans un système réel, on associerait la position de la main au visage.
                # Ici, si un visage connu est détecté ET qu'une main est levée, on lance le timer.
                any_hand_raised = any(h['is_raised'] for h in hands)
                
                for res in results:
                    user_id = res['user_id']
                    if user_id:
                        print(f"Utilisateur identifié: {res['name']} (ID: {user_id})")
                        # Si main levée, on vérifie la confirmation
                        if any_hand_raised:
                            if gesture_engine.check_gesture_confirmed(user_id, True):
                                print(f"!!! GESTE CONFIRMÉ pour {res['name']} !!!")
                                AttendanceService.mark_present(user_id, res['confidence'])
                                gesture_engine.reset_timer(user_id)
                            else:
                                elapsed = time.time() - gesture_engine.timers.get(user_id, time.time())
                                print(f"Geste en cours pour {res['name']}... ({elapsed:.1f}s)")
                        else:
                            gesture_engine.check_gesture_confirmed(user_id, False)
            
            time.sleep(0.1)

@bp.route('/attendance')
def index():
    start_engines()
    return render_template('attendance.html')

@bp.route('/video_feed')
def video_feed():
    start_engines()
    return Response(CameraStream.generate_mjpeg(camera, face_engine, mode='attendance'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/api/today-attendance')
def today_attendance():
    summary = AttendanceService.get_today_summary()
    return jsonify(summary)
