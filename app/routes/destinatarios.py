from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Destinatario, Remitente
from sqlalchemy.exc import SQLAlchemyError

destinatarios_bp = Blueprint('destinatarios', __name__, url_prefix='/destinatarios')

@destinatarios_bp.route('/')
@login_required
def lista_destinatarios():
    destinatarios = Destinatario.query.all()
    return render_template("destinatarios/destinatarios.html", destinatarios=destinatarios)

@destinatarios_bp.route('/agregar', methods=["GET", "POST"])
@login_required
def agregar_destinatario():
    if request.method == "POST":
        try:
            numero = request.form["numero"]
            nombre = request.form.get("nombre")
            correo = request.form.get("correo")
            remitente_ids = request.form.getlist("remitentes")

            nuevo = Destinatario(numero=numero, nombre=nombre, correo=correo)

            for id_rem in remitente_ids:
                remitente = Remitente.query.get(int(id_rem))
                if remitente:
                    nuevo.remitentes.append(remitente)

            db.session.add(nuevo)
            db.session.commit()
            flash("Destinatario agregado con éxito", "destinatario")
            return redirect(url_for('destinatarios.lista_destinatarios'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al guardar destinatario: {str(e)}", "destinatario")

    remitentes = Remitente.query.all()
    return render_template("destinatarios/agregar.html", remitentes=remitentes)

@destinatarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_destinatario(id):
    destinatario = Destinatario.query.get_or_404(id)
    if request.method == "POST":
        try:
            destinatario.numero = request.form["numero"]
            destinatario.nombre = request.form.get("nombre")
            destinatario.correo = request.form.get("correo")

            # Limpiar remitentes anteriores
            destinatario.remitentes.clear()

            # Agregar nuevos remitentes seleccionados
            remitente_ids = request.form.getlist("remitentes")
            for id_rem in remitente_ids:
                remitente = Remitente.query.get(int(id_rem))
                if remitente:
                    destinatario.remitentes.append(remitente)

            db.session.commit()
            flash("Destinatario actualizado", "destinatario")
            return redirect(url_for('destinatarios.lista_destinatarios'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "destinatario")

    remitentes = Remitente.query.all()
    return render_template("destinatarios/editar.html", destinatario=destinatario, remitentes=remitentes)

@destinatarios_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_destinatario(id):
    destinatario = Destinatario.query.get_or_404(id)
    try:
        db.session.delete(destinatario)
        db.session.commit()
        flash("Destinatario eliminado correctamente", "destinatario")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al eliminar destinatario: {str(e)}", "destinatario")
    
    return redirect(url_for('destinatarios.lista_destinatarios'))

