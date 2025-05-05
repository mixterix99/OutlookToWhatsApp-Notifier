from . import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
class Remitentes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nombre = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    destinatarios = db.relationship('Destinatarios', backref='remitentes', cascade="all, delete-orphan")

class Destinatarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(255), nullable=True)
    id_remitente = db.Column(db.Integer, db.ForeignKey('remitentes.id'), nullable=False)

class Notificaciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_remitente = db.Column(db.Integer, db.ForeignKey('remitentes.id'), nullable=False)
    id_destinatario = db.Column(db.Integer, db.ForeignKey('destinatarios.id'), nullable=False)
    asunto = db.Column(db.String(255))
    fecha = db.Column(db.String(50))
    mensaje = db.Column(db.Text)