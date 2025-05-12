from flask import Blueprint, render_template, request
from app.models import Notificacion, Remitente, Destinatario
from app import db

notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notificaciones', methods=['GET'])
def notificaciones():
    fecha = request.args.get('fecha')
    remitente = request.args.get('remitente')
    destinatario = request.args.get('destinatario')

    query = db.session.query(Notificacion).join(Remitente).join(Destinatario)

    if fecha:
        query = query.filter(Notificacion.fecha.contains(fecha))
    if remitente:
        query = query.filter(Remitente.email.contains(remitente))
    if destinatario:
        query = query.filter(Destinatario.nombre.contains(destinatario))

    notificaciones = query.order_by(Notificacion.fecha.desc()).all()

    return render_template("notificaciones/notificaciones.html", notificaciones=notificaciones)
