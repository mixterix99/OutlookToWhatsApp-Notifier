import sys
import os
import json
import win32com.client
from datetime import datetime
from twilio.rest import Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from app.models import db, Remitente, Notificacion
import pythoncom

# Configuración
ARCHIVO_IDS = "ids_procesados.json"
RUTA_ADJUNTOS = "C:/Temp/adjuntos_guardados"
os.makedirs(RUTA_ADJUNTOS, exist_ok=True)

# Twilio
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
numero_twilio = os.getenv("WHATSAPP_FROM")
client = Client(account_sid, auth_token)

# Cargar IDs procesados
if os.path.exists(ARCHIVO_IDS):
    with open(ARCHIVO_IDS, "r") as f:
        ids_procesados = json.load(f)
else:
    ids_procesados = []

def procesar_correos():
    pythoncom.CoInitialize()
    try:
        from app import create_app  # Importar aquí para evitar errores circulares
        app = create_app()
        with app.app_context():
            # Autenticación Google Drive
            gauth = GoogleAuth()
            gauth.LoadCredentialsFile("credentials.json")

            if gauth.credentials is None:
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                gauth.Refresh()
            else:
                gauth.Authorize()

            gauth.SaveCredentialsFile("credentials.json")
            drive = GoogleDrive(gauth)

            # Actualiza estado del servicio
            with open("servicio_status.json", "w") as f:
                json.dump({"ultima_ejecucion": datetime.now().isoformat()}, f)

            print("⏳ Ejecutando verificación de correos...")

            nombres_entrada = ["Inbox", "Bandeja de entrada"]
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

            bandejas_encontradas = []
            for i in range(outlook.Folders.Count):
                buzon = outlook.Folders.Item(i + 1)
                for nombre in nombres_entrada:
                    try:
                        inbox = buzon.Folders[nombre]
                        bandejas_encontradas.append((buzon.Name, inbox))
                        break
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

                    primer_enlace = enlaces_drive[0][1] if enlaces_drive else None
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
                                # Verificar si ya se envió esta notificación
                                notificacion_existente = Notificacion.query.filter_by(
                                    id_remitente=remitente.id,
                                    id_destinatario=destinatario.id,
                                    asunto=asunto,
                                    fecha=fecha
                                ).first()

                                if not notificacion_existente:
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
                                        mensaje=mensaje_whatsapp,
                                        archivo_url= primer_enlace,
                                        estado= "Enviado"
                                    )
                                    db.session.add(notificacion)
                                    db.session.commit()
                                else:
                                    print(f"⏭️ Ya se notificó a {destinatario.nombre} por este correo.")

                        except Exception as e:
                            print(f"❌ Error enviando mensaje a {destinatario.numero}:", e)

                    ids_procesados.append(entry_id)
                    with open(ARCHIVO_IDS, "w") as f:
                        json.dump(ids_procesados, f)

    finally:
        pythoncom.CoUninitialize()
