import win32com.client
import os
import json
from twilio.rest import Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

from db_managerOLD import listar_remitentes, listar_destinatarios_por_remitente

# ========== CARGAR VARIABLES DE ENTORNO ==========
load_dotenv()
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
numero_twilio = os.getenv("WHATSAPP_FROM")

ARCHIVO_IDS = "ids_procesados.json"
ruta_adjuntos = "C:/Temp/adjuntos_guardados"
os.makedirs(ruta_adjuntos, exist_ok=True)

# ========== GOOGLE DRIVE ==========
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# ========== CARGAR IDS ==========
if os.path.exists(ARCHIVO_IDS):
    with open(ARCHIVO_IDS, "r") as f:
        ids_procesados = json.load(f)
else:
    ids_procesados = []

# ========== CONEXIÓN OUTLOOK ==========
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
buzon = outlook.Folders.Item(1)
inbox = buzon.Folders["Inbox"]
mensajes = inbox.Items
mensajes.Sort("[ReceivedTime]", True)

# ========== BUSCAR CORREOS DE REMITENTES ==========
remitentes = listar_remitentes()

for id_rem, email_rem, nombre_rem, activo in remitentes:
    if not activo:
        continue

    print(f"\n🔎 Buscando correos de: {email_rem}")
    mensaje_filtrado = None

    for i in range(min(20, mensajes.Count)):
        mensaje = mensajes.Item(i + 1)
        try:
            if mensaje.Class == 43:
                entry_id = mensaje.EntryID

                if entry_id in ids_procesados:
                    continue

                if mensaje.SenderEmailAddress.lower() == email_rem.lower():
                    mensaje_filtrado = mensaje
                    id_a_guardar = entry_id
                    break
        except Exception as e:
            print("Error leyendo mensaje:", e)

    # ========== SI SE ENCONTRÓ UN CORREO ==========
    if mensaje_filtrado:
        asunto = mensaje_filtrado.Subject
        fecha = mensaje_filtrado.ReceivedTime.strftime("%Y-%m-%d %H:%M")
        tiene_adjuntos = "Sí" if mensaje_filtrado.Attachments.Count > 0 else "No"

        # Guardar adjuntos
        lista_adjuntos = []
        for adjunto in mensaje_filtrado.Attachments:
            nombre_archivo = adjunto.FileName
            ruta_completa = os.path.join(ruta_adjuntos, nombre_archivo)
            try:
                adjunto.SaveAsFile(ruta_completa)
                lista_adjuntos.append(nombre_archivo)
                print("📁 Adjunto guardado:", nombre_archivo)
            except Exception as e:
                print("❌ Error guardando adjunto:", nombre_archivo, "|", e)

        # Subir a Drive
        enlaces_adjuntos = []
        for archivo in lista_adjuntos:
            ruta = os.path.join(ruta_adjuntos, archivo)
            try:
                file_drive = drive.CreateFile({'title': archivo})
                file_drive.SetContentFile(ruta)
                file_drive.Upload()
                file_drive.InsertPermission({
                    'type': 'anyone',
                    'value': 'anyone',
                    'role': 'reader'
                })
                link = file_drive['alternateLink']
                enlaces_adjuntos.append((archivo, link))
                print(f"🔗 Subido: {archivo} → {link}")
            except Exception as e:
                print("❌ Error en Drive:", archivo, "|", e)

        # Crear mensaje
        mensaje_whatsapp = f"""📩 *Nuevo correo recibido*

🧾 Asunto: {asunto}
📅 Fecha: {fecha}
📎 Tiene adjuntos: {tiene_adjuntos}
"""

        if enlaces_adjuntos:
            mensaje_whatsapp += "\n📎 Archivos adjuntos:\n"
            for nombre, enlace in enlaces_adjuntos:
                mensaje_whatsapp += f"• {nombre}: {enlace}\n"
        else:
            mensaje_whatsapp += "\n📎 Archivos adjuntos: Ninguno"

        # Enviar a todos los destinatarios
        client = Client(account_sid, auth_token)
        destinatarios = listar_destinatarios_por_remitente(id_rem)
        for id_dest, numero, nombre in destinatarios:
            try:
                client.messages.create(
                    body=mensaje_whatsapp,
                    from_=numero_twilio,
                    to="whatsapp:" + numero
                )
                print(f"✅ Enviado a {nombre} ({numero})")
            except Exception as e:
                print(f"❌ Error enviando a {numero}:", e)

        # Registrar ID procesado
        ids_procesados.append(id_a_guardar)
        with open(ARCHIVO_IDS, "w") as f:
            json.dump(ids_procesados, f)

    else:
        print("📭 No se encontraron correos nuevos.")
