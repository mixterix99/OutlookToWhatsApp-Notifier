import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import os
import json
import win32com.client
from datetime import datetime
from twilio.rest import Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from flask import current_app
from app.models import db, Remitente, Destinatario, Notificacion

# Configuración
ARCHIVO_IDS = "ids_procesados.json"
RUTA_ADJUNTOS = "C:/Temp/adjuntos_guardados"
os.makedirs(RUTA_ADJUNTOS, exist_ok=True)

# Twilio
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
numero_twilio = os.getenv("WHATSAPP_FROM")
client = Client(account_sid, auth_token)

# Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Cargar IDs procesados
if os.path.exists(ARCHIVO_IDS):
    with open(ARCHIVO_IDS, "r") as f:
        ids_procesados = json.load(f)
else:
    ids_procesados = []

def procesar_correos():
    print("⏳ Ejecutando verificación de correos...")

    # Cargar Outlook y buscar todas las bandejas válidas
    nombres_entrada = ["Inbox", "Bandeja de entrada"]
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    bandejas_encontradas = []
    for i in range(outlook.Folders.Count):
        buzon = outlook.Folders.Item(i + 1)
        for nombre in nombres_entrada:
            try:
                inbox = buzon.Folders[nombre]
                bandejas_encontradas.append((buzon.Name, inbox))
                break  # Solo una carpeta por buzón
            except:
                continue

    if not bandejas_encontradas:
        print("❌ No se encontraron bandejas de entrada.")
        return

    remitentes = Remitente.query.filter_by(activo=True).all()

    for nombre_buzon, inbox in bandejas_encontradas:
        print(f"\n📥 Revisando bandeja: {nombre_buzon} ({inbox.Name})")

        mensajes = inbox.Items
        mensajes.Sort("[ReceivedTime]", True)

        for remitente in remitentes:
            print(f"🔎 Buscando correos de: {remitente.email}")
            mensaje_filtrado = None

            for i in range(min(20, mensajes.Count)):
                mensaje = mensajes.Item(i + 1)
                try:
                    if mensaje.Class != 43:
                        continue

                    entry_id = mensaje.EntryID
                    if entry_id in ids_procesados:
                        continue

                    sender = mensaje.SenderEmailAddress.lower()
                    email_valido = (
                        remitente.tipo == 'correo' and sender == remitente.email.lower()
                    ) or (
                        remitente.tipo == 'dominio' and sender.endswith(remitente.email.lower())
                    )
                    print("Remitente del correo:", mensaje.SenderName)
                    print("Dirección del remitente:", mensaje.SenderEmailAddress)

                    if email_valido:
                        mensaje_filtrado = mensaje
                        break

                except Exception as e:
                    print("⚠️ Error leyendo mensaje:", e)

            if not mensaje_filtrado:
                print("📭 No se encontraron correos nuevos para este remitente.")
                continue

            asunto = mensaje_filtrado.Subject
            fecha = mensaje_filtrado.ReceivedTime.strftime("%Y-%m-%d %H:%M")
            entry_id = mensaje_filtrado.EntryID

            lista_adjuntos = []
            for adjunto in mensaje_filtrado.Attachments:
                ruta = os.path.join(RUTA_ADJUNTOS, adjunto.FileName)
                try:
                    adjunto.SaveAsFile(ruta)
                    lista_adjuntos.append(ruta)
                    print("📁 Adjunto guardado:", adjunto.FileName)
                except Exception as e:
                    print("❌ Error guardando adjunto:", e)

            enlaces_drive = []
            for ruta in lista_adjuntos:
                try:
                    archivo = drive.CreateFile({'title': os.path.basename(ruta)})
                    archivo.SetContentFile(ruta)
                    archivo.Upload()
                    archivo.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
                    enlace = archivo['alternateLink']
                    enlaces_drive.append((os.path.basename(ruta), enlace))
                except Exception as e:
                    print("❌ Error subiendo a Drive:", e)

            remitente_nombre = mensaje_filtrado.SenderName
            remitente_correo = mensaje_filtrado.SenderEmailAddress

            mensaje_whatsapp = (
                f"📩 *Nuevo correo recibido*\n\n"
                f"✉️ Remitente: *{remitente_nombre}* ({remitente_correo})\n"
                f"🧾 Asunto: {asunto}\n"
                f"📅 Fecha: {fecha}\n"
                f"📎 Adjuntos: {'Sí' if enlaces_drive else 'No'}\n"
            )
            if enlaces_drive:
                mensaje_whatsapp += "\n📎 Archivos adjuntos:\n"
                for nombre, link in enlaces_drive:
                    mensaje_whatsapp += f"• {nombre}: {link}\n"

            for destinatario in remitente.destinatarios:
                try:
                    if destinatario.numero:
                        client.messages.create(
                            body=mensaje_whatsapp,
                            from_=numero_twilio,
                            to=f"whatsapp:+57{destinatario.numero}"
                        )
                        print(f"✅ Enviado a {destinatario.nombre} ({destinatario.numero})")

                        notificacion = Notificacion(
                            id_remitente=remitente.id,
                            id_destinatario=destinatario.id,
                            asunto=asunto,
                            fecha=fecha,
                            mensaje=mensaje_whatsapp
                        )
                        db.session.add(notificacion)
                        db.session.commit()
                except Exception as e:
                    print(f"❌ Error enviando mensaje a {destinatario.numero}:", e)

            ids_procesados.append(entry_id)
            with open(ARCHIVO_IDS, "w") as f:
                json.dump(ids_procesados, f)