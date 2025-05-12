from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models import Usuario, db, Log
from datetime import datetime, timedelta
from app import login_manager
import json


main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('main.panel'))
        flash("Usuario o contraseña incorrectos", category="login")
    return render_template('login.html')

@main.route('/panel')
@login_required
def panel():
    logs = Log.query.order_by(Log.fecha.desc()).limit(10).all()

    servicio_activo = False
    try:
        with open("servicio_status.json", "r") as f:
            data = json.load(f)
            ultima = datetime.fromisoformat(data["ultima_ejecucion"])
            servicio_activo = (datetime.now() - ultima) < timedelta(minutes=1)
    except:
        pass  # archivo no existe o está corrupto

    return render_template("panel.html", logs=logs, servicio_activo=servicio_activo)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
