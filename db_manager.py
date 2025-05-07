from app import db
from app.models import Remitente, Destinatario
from sqlalchemy.exc import SQLAlchemyError

# ---------- REMITENTES ----------

def agregar_remitente(email, nombre, activo, tipo):
    try:
        nuevo = Remitente(email=email, nombre=nombre, activo=bool(activo), tipo=tipo)
        db.session.add(nuevo)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def listar_remitentes():
    return Remitente.query.filter_by(activo=True).all()

def obtener_remitente(id_remitente):
    return Remitente.query.get(id_remitente)

def editar_remitente(id_remitente, email, nombre, activo, tipo):
    remitente = Remitente.query.get(id_remitente)
    if remitente:
        remitente.email = email
        remitente.nombre = nombre
        remitente.activo = bool(activo)
        remitente.tipo = tipo
        db.session.commit()

def eliminar_remitente(id_remitente):
    remitente = Remitente.query.get(id_remitente)
    if remitente:
        db.session.delete(remitente)
        db.session.commit()

# ---------- DESTINATARIOS ----------

def agregar_destinatario(numero, nombre, remitente_ids):
    try:
        nuevo = Destinatario(numero=numero, nombre=nombre)
        for id_rem in remitente_ids:
            remitente = Remitente.query.get(id_rem)
            if remitente:
                nuevo.remitentes.append(remitente)
        db.session.add(nuevo)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def listar_destinatarios():
    return Destinatario.query.all()

def listar_destinatarios_por_remitente(id_remitente):
    remitente = Remitente.query.get(id_remitente)
    return remitente.destinatarios if remitente else []
