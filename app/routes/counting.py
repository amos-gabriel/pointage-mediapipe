from flask import Blueprint, render_template, Response, jsonify, current_app
from app.utils.camera import CameraStream
from app.utils.face_engine import FaceEngine
from datetime import datetime
import collections

bp = Blueprint('counting', __name__)

# On réutilise les instances si elles existent déjà dans attendance
# Mais pour être sûr, on les initialise ici aussi si besoin
camera_count = None
face_engine_count = None
count_history = collections.deque(maxlen=5) # Pour le lissage

def get_engines():
    global camera_count, face_engine_count
    from app.routes.attendance import camera, face_engine
    
    if camera is not None:
        camera_count = camera
    else:
        if camera_count is None:
            camera_count = CameraStream(camera_index=current_app.config['CAMERA_INDEX'], 
                                       target_fps=current_app.config['TARGET_FPS'])
            camera_count.start()
            
    if face_engine is not None:
        face_engine_count = face_engine
    else:
        if face_engine_count is None:
            face_engine_count = FaceEngine(tolerance=current_app.config['FACE_TOLERANCE'])
            
    return camera_count, face_engine_count

@bp.route('/counting')
def index():
    get_engines()
    return render_template('counting.html')

@bp.route('/video_feed_count')
def video_feed_count():
    cam, face = get_engines()
    return Response(CameraStream.generate_mjpeg(cam, face, mode='counting'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/api/current-count')
def current_count():
    cam, face = get_engines()
    frame = cam.get_frame()
    
    raw_count = face.count_faces(frame) if frame is not None else 0
    
    # Lissage (médiane sur 5 frames)
    count_history.append(raw_count)
    sorted_history = sorted(list(count_history))
    smoothed_count = sorted_history[len(sorted_history)//2]
    
    return jsonify({
        "count": smoothed_count,
        "timestamp": datetime.now().isoformat()
    })
