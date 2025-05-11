from .main import main
from .remitentes import remitentes_bp
from flask_migrate import Migrate
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # o como sea que estés configurando
    db.init_app(app)

    # 🔽 Agrega esta línea
    Migrate(app, db)

    # Registra blueprints y otros
    return app