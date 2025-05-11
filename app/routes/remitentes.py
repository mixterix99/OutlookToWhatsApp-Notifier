from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import request, redirect, url_for, flash
from  app.models  import Remitente, db, Log
from datetime import  datetime


remitentes_bp = Blueprint('remitentes', __name__, url_prefix="/remitentes")

@remitentes_bp.route("/")
@login_required
def lista_remitentes():
    remitentes =  Remitente.query.filter_by(activo=True).all()
    return render_template("remitentes/remitentes.html", remitentes=remitentes)

@remitentes_bp.route("/agregar", methods=["GET", "POST"])
@login_required

def agregar_remitente():
    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        activo = True if "activo" in request.form else False

        nuevo_remitente = Remitente(email=email, nombre=nombre, tipo=tipo, activo=activo)
        db.session.add(nuevo_remitente)
        # Log
        log = Log(
            usuario_id=current_user.id,
            accion="agregar",
            entidad="remitente",
            detalle = f"Remitente '{nombre or email}' agregado (tipo: {tipo})",
            fecha=datetime.now()
        )
        db.session.add(log)
        db.session.commit()

        flash("✅ Remitente agregado con éxito")
        return redirect(url_for("remitentes.lista_remitentes"))

    return render_template("remitentes/agregar.html")

@remitentes_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_remitente(id):
    remitente = Remitente.query.get(id)
    if not remitente:
        flash("Remitente no encontrado.")
        return redirect(url_for("remitentes.lista_remitentes"))

    if request.method == "POST":
        remitente.email = request.form["email"]
        remitente.nombre = request.form["nombre"]
        remitente.activo = True if request.form.get("activo") == "on" else False
        remitente.tipo = request.form["tipo"]

        db.session.commit()

        # Registro en log
        nuevo_log = Log(
            usuario_id=current_user.id,
            accion="editar",
            entidad="remitente",
            detalle=f"{remitente.nombre or remitente.email} (id: {remitente.id}, tipo: {remitente.tipo})",
            fecha=datetime.now()
        )
        db.session.add(nuevo_log)
        db.session.commit()

        flash("Remitente actualizado.")
        return redirect(url_for("remitentes.lista_remitentes"))

    return render_template("remitentes/editar.html", remitente=remitente)
@remitentes_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_remitente_route(id):
    remitente = Remitente.query.get(id)
    if remitente:
        detalle = f"{remitente.nombre or remitente.email} (id: {remitente.id}, tipo: {remitente.tipo})"
        db.session.delete(remitente)
        db.session.commit()

        # Log
        log = Log(
            usuario_id=current_user.id,
            accion="eliminar",
            entidad="remitente",
            detalle=detalle,
            fecha=datetime.now()
        )
        db.session.add(log)
        db.session.commit()

        flash("Remitente eliminado correctamente.")
    else:
        flash("Remitente no encontrado.")

    return redirect(url_for("remitentes.lista_remitentes"))


