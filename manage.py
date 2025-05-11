from flask_migrate import Migrate
from app import create_app
from app.models import db

app = create_app()
migrate = Migrate(app, db)
