import win32com.client
from twilio.rest import Client
import json
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Autenticación con Google Drive (solo la primera vez abre navegador)
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Abre navegador para autenticar
drive = GoogleDrive(gauth)


ARCHIVO_IDS = "ids_procesados.json"

# Cargar IDs previamente guardados
if os.path.exists(ARCHIVO_IDS):
    with open(ARCHIVO_IDS, "r") as f:
        ids_procesados = json.load(f)
else:
    ids_procesados = []

# ========== CONFIGURACIÓN ==========
remitente_diana = "diegopolo14@gmail.com"

account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")
numero_twilio = os.getenv("WHATSAPP_FROM")
numero_destino = os.getenv("WHATSAPP_TO")  # Cambia al tuyo validado

# ========== OUTLOOK ==========
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
print("Buzones encontrados:")
for i in range(outlook.Folders.Count):
    print(f"{i + 1}: {outlook.Folders.Item(i + 1).Name}")

buzon = outlook.Folders.Item(1)
inbox = buzon.Folders["Bandeja de entrada"]
mensajes = inbox.Items
mensajes.Sort("[ReceivedTime]", True)


# ========== FILTRO DE MENSAJE ==========
mensaje_filtrado = None

print("\nCorreos recientes del remitente especificado:\n")
for i in range(min(20, mensajes.Count)):
    mensaje = mensajes.Item(i + 1)
    try:
        if mensaje.Class == 43:
            entry_id = mensaje.EntryID  # ← Captura el EntryID del mensaje

            if entry_id in ids_procesados:
                continue  # Ya fue procesado antes

            if mensaje.SenderEmailAddress.lower() == remitente_diana:
                print("Asunto:", mensaje.Subject)
                print("Fecha:", mensaje.ReceivedTime.strftime("%Y-%m-%d %H:%M"))
                print("Tiene adjuntos:", "Sí" if mensaje.Attachments.Count > 0 else "No")
                print("-" * 50)

                mensaje_filtrado = mensaje
                id_a_guardar = entry_id  # ← Guarda el EntryID para agregarlo luego
                break
    except Exception as e:
        print("Error al procesar mensaje:", e)



# ========== ENVÍO POR TWILIO ==========
if mensaje_filtrado:

    ruta_adjuntos = "C:/Temp/adjuntos_guardados"
    os.makedirs(ruta_adjuntos, exist_ok=True)
    # Guardar adjuntos del mensaje
    lista_adjuntos = []  # Para registrar los nombres de archivos guardados

    for adjunto in mensaje_filtrado.Attachments:
        nombre_archivo = adjunto.FileName
        ruta_completa = os.path.join(ruta_adjuntos, nombre_archivo)

        try:
            adjunto.SaveAsFile(ruta_completa)
            lista_adjuntos.append(nombre_archivo)
            print("📁 Adjunto guardado:", ruta_completa)
        except Exception as e:
            print("❌ Error guardando adjunto:", nombre_archivo, "|", e)

    asunto = mensaje_filtrado.Subject
    fecha = mensaje_filtrado.ReceivedTime.strftime("%Y-%m-%d %H:%M")
    tiene_adjuntos = "Sí" if mensaje_filtrado.Attachments.Count > 0 else "No"

    mensaje_whatsapp = f"""📩 *Nuevo correo recibido*

            🧾 Asunto: {asunto}
            📅 Fecha: {fecha}
            📎 Tiene adjuntos: {tiene_adjuntos}
            """

    # Subir los archivos a Google Drive
    enlaces_adjuntos = []

    for archivo in lista_adjuntos:
        ruta = os.path.join(ruta_adjuntos, archivo)
        try:
            file_drive = drive.CreateFile({'title': archivo})
            file_drive.SetContentFile(ruta)
            file_drive.Upload()

            # Hacer público el archivo
            file_drive.InsertPermission({
                'type': 'anyone',
                'value': 'anyone',
                'role': 'reader'
            })

            link = file_drive['alternateLink']
            enlaces_adjuntos.append((archivo, link))
            print(f"🔗 Subido y compartido: {archivo} -> {link}")
        except Exception as e:
            print("❌ Error subiendo a Drive:", archivo, "|", e)

    # Agregar los enlaces al mensaje
    if enlaces_adjuntos:
        mensaje_whatsapp += "\n📎 Archivos adjuntos:\n"
        for nombre, enlace in enlaces_adjuntos:
            mensaje_whatsapp += f"• {nombre}: {enlace}\n"
    else:
        mensaje_whatsapp += "\n📎 Archivos adjuntos: Ninguno"

    # Enviar por Twilio
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=mensaje_whatsapp,
        from_=numero_twilio,
        to=numero_destino
    )

    # Guardar el EntryID para evitar repetir el mensaje
    ids_procesados.append(id_a_guardar)
    with open(ARCHIVO_IDS, "w") as f:
        json.dump(ids_procesados, f)

    print("✅ Mensaje enviado y EntryID registrado:", id_a_guardar)

else:
    print("❌ No se encontró un correo nuevo para enviar.")
