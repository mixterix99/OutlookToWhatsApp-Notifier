from flask import Blueprint, render_template
from flask_login import login_required
from db_managerOLD import listar_remitentes
from db_managerOLD import agregar_remitente
from flask import request, redirect, url_for, flash
from db_managerOLD import conectar
from db_managerOLD import obtener_remitente, editar_remitente, eliminar_remitente

remitentes_bp = Blueprint('remitentes', __name__, url_prefix="/remitentes")

@remitentes_bp.route("/")
@login_required
def lista_remitentes():
    datos = listar_remitentes()
    print("Remitentes encontrados:", datos)
    return render_template("remitentes/remitentes.html", remitentes=datos)

@remitentes_bp.route("/agregar", methods=["GET", "POST"])
@login_required

def agregar_remitente():
    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        activo = 1 if "activo" in request.form else 0
        tipo = request.form["tipo"]
        

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO remitentes (email, nombre, activo, tipo) VALUES (?, ?, ?, ?)", (email, nombre, activo, tipo))
        conn.commit()
        conn.close()
        flash("✅ Remitente agregado con éxito")
        return redirect(url_for("remitentes.lista_remitentes"))

    return render_template("remitentes/agregar.html")

@remitentes_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_remitente(id):
    remitente = obtener_remitente(id)
    if not remitente:
        flash("Remitente no encontrado.")
        return redirect(url_for("remitentes.lista_remitentes"))

    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        activo = 1 if request.form.get("activo") == "on" else 0
        tipo = request.form["tipo"]
        editar_remitente(id, email, nombre, activo, tipo)
        flash("Remitente actualizado.")
        return redirect(url_for("remitentes.lista_remitentes"))

    return render_template("remitentes/editar.html", remitente=remitente)

@remitentes_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_remitente_route(id):
    eliminar_remitente(id)
    flash("Remitente eliminado correctamente.")
    return redirect(url_for("remitentes.lista_remitentes"))

