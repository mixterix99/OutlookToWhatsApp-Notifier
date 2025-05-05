from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db_manager import listar_destinatarios  # Asegúrate que existe esta función

destinatarios_bp = Blueprint("destinatarios", __name__, url_prefix="/destinatarios")

@destinatarios_bp.route("/")
@login_required
def lista_destinatarios():
    datos = listar_destinatarios()
    return render_template("destinatarios/destinatarios.html", destinatarios=datos)
