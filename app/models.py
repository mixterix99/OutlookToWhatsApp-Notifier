from . import db
from flask_login import UserMixin
from datetime import datetime

# Tabla intermedia para relación many-to-many
remitente_destinatario = db.Table('remitente_destinatario',
    db.Column('id_remitente', db.Integer, db.ForeignKey('remitentes.id'), primary_key=True),
    db.Column('id_destinatario', db.Integer, db.ForeignKey('destinatarios.id'), primary_key=True)
)

class Remitente(db.Model):
    __tablename__ = 'remitentes'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    tipo = db.Column(db.String(50), nullable=False)  # puede ser 'correo' o 'dominio'

    destinatarios = db.relationship(
        'Destinatario',
        secondary=remitente_destinatario,
        back_populates='remitentes'
    )

class Destinatario(db.Model):
    __tablename__ = 'destinatarios'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(255), nullable=True)  # ← NUEVO
    nombre = db.Column(db.String(255), nullable=True)

    remitentes = db.relationship(
        'Remitente',
        secondary=remitente_destinatario,
        back_populates='destinatarios'
    )

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    id = db.Column(db.Integer, primary_key=True)
    id_remitente = db.Column(db.Integer, db.ForeignKey('remitentes.id'), nullable=False)
    id_destinatario = db.Column(db.Integer, db.ForeignKey('destinatarios.id'), nullable=False)
    asunto = db.Column(db.String(255))
    fecha = db.Column(db.String(50))
    mensaje = db.Column(db.Text)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    accion = db.Column(db.String(100), nullable=False)
    entidad = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='logs')
