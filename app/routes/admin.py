import os
import cv2
import face_recognition
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from app.models.user import User
from app import db
import app.routes.attendance as attendance

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def index():
    users = User.query.all()
    return render_template('admin.html', users=users)

@bp.route('/admin/register', methods=['POST'])
def register():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    matricule = request.form.get('matricule')

    if not all([nom, prenom, matricule]):
        return jsonify({"success": False, "message": "Tous les champs sont requis."}), 400

    if User.query.filter_by(matricule=matricule).first():
        return jsonify({"success": False, "message": "Ce matricule existe déjà."}), 400

    # Utiliser la caméra déjà ouverte par le stream si possible, sinon en ouvrir une temporairement
    # Pour simplifier et éviter les conflits de thread, on demande à l'utilisateur de capturer via le stream existant
    # Mais ici on va implémenter une capture directe pour l'interface admin
    
    # On récupère le frame actuel du stream global
    if attendance.camera is None:
        return jsonify({"success": False, "message": "La caméra n'est pas active. Allez sur la page de pointage d'abord."}), 400
    
    frame = attendance.camera.get_frame()
    if frame is None:
        return jsonify({"success": False, "message": "Impossible de capturer une image."}), 400

    # Détection et encodage
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if len(face_locations) == 0:
        return jsonify({"success": False, "message": "Aucun visage détecté. Assurez-vous d'être bien devant la caméra."}), 400
    if len(face_locations) > 1:
        return jsonify({"success": False, "message": "Plusieurs visages détectés. Un seul visage requis."}), 400

    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if not encodings:
        return jsonify({"success": False, "message": "Erreur lors de l'encodage du visage."}), 400

    encoding = encodings[0]

    # Sauvegarde de l'image
    photo_dir = current_app.config['KNOWN_FACES_DIR']
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)
    
    photo_filename = f"{prenom}_{nom}_{matricule}.jpg"
    photo_path = os.path.join(photo_dir, photo_filename)
    cv2.imwrite(photo_path, frame)

    # Création de l'utilisateur
    user = User(nom=nom, prenom=prenom, matricule=matricule, photo_path=photo_path)
    user.set_encoding(encoding)
    
    db.session.add(user)
    db.session.commit()

    # Recharger les visages dans le moteur
    if attendance.face_engine:
        attendance.face_engine.load_known_faces()

    return jsonify({"success": True, "message": f"Utilisateur {prenom} {nom} enregistré avec succès !"})

@bp.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Supprimer le fichier photo s'il existe
    if user.photo_path and os.path.exists(user.photo_path):
        try:
            os.remove(user.photo_path)
        except Exception as e:
            print(f"Erreur suppression fichier: {e}")

    db.session.delete(user)
    db.session.commit()

    # Recharger les visages dans le moteur
    if attendance.face_engine:
        attendance.face_engine.load_known_faces()

    return redirect(url_for('admin.index'))
