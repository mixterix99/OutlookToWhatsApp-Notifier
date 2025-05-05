from flask import Blueprint, render_template
from flask_login import login_required
from db_manager import listar_remitentes
from db_manager import agregar_remitente
from flask import request, redirect, url_for, flash
from db_manager import conectar


remitentes_bp = Blueprint('remitentes', __name__, url_prefix="/remitentes")

@remitentes_bp.route("/")
@login_required
def lista_remitentes():
    datos = listar_remitentes()
    return render_template("remitentes/remitentes.html", remitentes=datos)

@remitentes_bp.route("/agregar", methods=["GET", "POST"])
@login_required

def agregar_remitente():
    if request.method == "POST":
        email = request.form["email"]
        nombre = request.form["nombre"]
        activo = 1 if "activo" in request.form else 0

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO remitentes (email, nombre, activo) VALUES (?, ?, ?)", (email, nombre, activo))
        conn.commit()
        conn.close()
        flash("✅ Remitente agregado con éxito")
        return redirect(url_for("remitentes.lista_remitentes"))

    return render_template("remitentes/agregar.html")
