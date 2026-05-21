from datetime import datetime
from app import db

class Attendance(db.Model):
    """
    Modèle représentant un pointage de présence.
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')
    confidence_score = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

    @classmethod
    def get_today(cls, user_id: int):
        """Retourne le pointage du jour pour un utilisateur si existant."""
        today = datetime.utcnow().date()
        return cls.query.filter(
            cls.user_id == user_id,
            db.func.date(cls.timestamp) == today
        ).first()

    @classmethod
    def get_all_today(cls):
        """Retourne tous les pointages du jour."""
        today = datetime.utcnow().date()
        return cls.query.filter(db.func.date(cls.timestamp) == today).all()

    def __repr__(self):
        return f'<Attendance User:{self.user_id} Time:{self.timestamp}>'
