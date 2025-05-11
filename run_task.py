from app import create_app, db
from app.tasks.email_processor import procesar_correos

app = create_app()

with app.app_context():
    procesar_correos()
