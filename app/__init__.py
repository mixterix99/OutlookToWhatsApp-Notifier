from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from app.extensiones import db, login_manager

migrate = Migrate()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notificador.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Importar y registrar Blueprints
    from app.routes.main import main as main_blueprint
    from app.routes.remitentes import remitentes_bp
    from app.routes.destinatarios import destinatarios_bp
    from app.routes.notificaciones import notificaciones_bp

    app.register_blueprint(main_blueprint)
    app.register_blueprint(remitentes_bp)
    app.register_blueprint(destinatarios_bp)
    app.register_blueprint(notificaciones_bp)

    return app
