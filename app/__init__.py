from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Factory Flask pour initialiser l'application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Enregistrement des Blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp)

    from app.routes.counting import bp as counting_bp
    app.register_blueprint(counting_bp)

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    return app
