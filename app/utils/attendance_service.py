from app.models.attendance import Attendance
from app.models.user import User
from app import db
from typing import List, Dict, Any, Optional

class AttendanceService:
    """
    Service pour gérer les opérations de pointage.
    """
    @staticmethod
    def mark_present(user_id: int, confidence: float) -> Optional[Attendance]:
        """
        Enregistre le pointage d'un utilisateur s'il n'a pas déjà pointé aujourd'hui.
        """
        if user_id is None:
            return None

        # Vérifier si déjà pointé aujourd'hui
        existing = Attendance.get_today(user_id)
        if existing:
            return None

        # Créer le pointage
        attendance = Attendance(
            user_id=user_id,
            confidence_score=confidence,
            status='present'
        )
        
        db.session.add(attendance)
        db.session.commit()
        return attendance

    @staticmethod
    def get_today_summary() -> List[Dict[str, Any]]:
        """Retourne la liste des présences du jour avec les infos utilisateur."""
        attendances = Attendance.get_all_today()
        summary = []
        for att in attendances:
            user = User.query.get(att.user_id)
            summary.append({
                "id": att.id,
                "user_id": att.user_id,
                "nom": user.nom,
                "prenom": user.prenom,
                "matricule": user.matricule,
                "timestamp": att.timestamp.strftime("%H:%M:%S"),
                "confidence": att.confidence_score
            })
        # Trier par timestamp décroissant
        summary.sort(key=lambda x: x['timestamp'], reverse=True)
        return summary
