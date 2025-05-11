from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from  datetime import datetime
from app.models import db, Destinatario, Remitente, Log
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
          

            log = Log(
                usuario_id=current_user.id,
                accion="agregar",
                entidad="destinatario",
                detalle=f"{numero} ({nombre}) con {len(nuevo.remitentes)} remitente(s) asociado(s)",
                fecha=datetime.now()
            )
            db.session.add(log)
            db.session.commit()

            if not numero:
                flash("El número de destinatario es obligatorio.")
                return redirect(url_for('destinatarios.agregar_destinatario'))

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
        destinatario.numero = request.form["numero"]
        destinatario.nombre = request.form.get("nombre")
        destinatario.correo = request.form.get("correo")

        remitente_ids = list(map(int, request.form.getlist("remitentes")))
        destinatario.remitentes = Remitente.query.filter(Remitente.id.in_(remitente_ids)).all()

        db.session.commit()

        log = Log(
            usuario_id=current_user.id,
            accion="editar",
            entidad="destinatario",
            detalle=f"{destinatario.numero} ({destinatario.nombre}) actualizado con {len(remitente_ids)} remitente(s)",
            fecha=datetime.now()
        )
        db.session.add(log)
        db.session.commit()

        flash("Destinatario actualizado correctamente.")
        return redirect(url_for("destinatarios.lista_destinatarios"))

    remitentes = Remitente.query.all()
    return render_template("destinatarios/editar.html", destinatario=destinatario, remitentes=remitentes)

@destinatarios_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_destinatario(id):
    destinatario = Destinatario.query.get(id)
    if destinatario:
        detalle = f"{destinatario.numero} ({destinatario.nombre})"
        db.session.delete(destinatario)
        db.session.commit()

        log = Log(
            usuario_id=current_user.id,
            accion="eliminar",
            entidad="destinatario",
            detalle=detalle,
            fecha=datetime.now()
        )
        db.session.add(log)
        db.session.commit()

        flash("Destinatario eliminado correctamente.")
    else:
        flash("Destinatario no encontrado.")

    return redirect(url_for("destinatarios.lista_destinatarios"))