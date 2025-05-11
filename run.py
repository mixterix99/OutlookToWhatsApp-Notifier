from app import create_app
from flask import Flask
from flask_migrate import Migrate
from app.models import db  # tus modelos
from app import create_app  # tu factory



app = create_app()

migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run(debug=True)

