from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notificador.db'

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.main import main as main_blueprint
    from app.routes.remitentes import remitentes_bp
    from app.routes.destinatarios import destinatarios_bp

    app.register_blueprint(main_blueprint)
    app.register_blueprint(remitentes_bp)
    app.register_blueprint(destinatarios_bp)

    return app
