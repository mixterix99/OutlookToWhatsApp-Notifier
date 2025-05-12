from app import create_app, db
from app.tasks.email_processor import procesar_correos
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = create_app()
scheduler = BackgroundScheduler()

def job_con_contexto():
    with app.app_context():
        procesar_correos()

scheduler.add_job(job_con_contexto, 'interval', seconds=30)
scheduler.start()

print("🔁 Servicio iniciado. Presiona Ctrl+C para detener.")
try:
    while True:
        time.sleep(1)  # evita alto uso de CPU
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
