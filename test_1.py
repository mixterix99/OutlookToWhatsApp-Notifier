import win32com.client
import datetime
import pywhatkit as kit

# Conectarse a Outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

# Mostrar todos los buzones configurados
print("Buzones encontrados:")
for i in range(outlook.Folders.Count):
    print(f"{i + 1}: {outlook.Folders.Item(i + 1).Name}")

# Elegir el primer buzón para pruebas
buzon = outlook.Folders.Item(1)  # Puedes cambiar el índice si deseas probar con otro

# Acceder a la bandeja de entrada del buzón
inbox = buzon.Folders["Bandeja de entrada"]  # Usa "Inbox" si Outlook está en inglés
mensajes = inbox.Items
mensajes.Sort("[ReceivedTime]", True)  # Ordena por fecha de recepción descendente

# Configurar remitente a buscar
remitente_diana = "jefe.mantenimiento@qyt.com.co"

# Revisar los últimos 20 correos
mensaje_filtrado = None  # Inicializa una variable para guardar el mensaje correcto

# Revisión de correos
print("\nCorreos recientes del remitente especificado:\n")
for i in range(min(20, mensajes.Count)):
    mensaje = mensajes.Item(i + 1)
    try:
        if mensaje.Class == 43:
            if mensaje.SenderEmailAddress.lower() == remitente_diana:
                print("Asunto:", mensaje.Subject)
                print("Fecha:", mensaje.ReceivedTime.strftime("%Y-%m-%d %H:%M"))
                print("Tiene adjuntos:", "Sí" if mensaje.Attachments.Count > 0 else "No")
                print("-" * 50)
                
                mensaje_filtrado = mensaje  # Guarda el mensaje correcto
                break  # Si solo quieres enviar el primero que coincida
    except Exception as e:
        print("Error al procesar mensaje:", e)

# Solo si encontró un mensaje válido, arma el mensaje de WhatsApp
if mensaje_filtrado:
    asunto = mensaje_filtrado.Subject
    fecha = mensaje_filtrado.ReceivedTime.strftime("%Y-%m-%d %H:%M")
    tiene_adjuntos = "Sí" if mensaje_filtrado.Attachments.Count > 0 else "No"

    mensaje_whatsapp = f"""📩 *Nuevo correo recibido*

🧾 Asunto: {asunto}
📅 Fecha: {fecha}
📎 Tiene adjuntos: {tiene_adjuntos}
"""

    numero_directora = "+573108343555"
    hora = datetime.datetime.now() + datetime.timedelta(minutes=1)
    kit.sendwhatmsg(numero_directora, mensaje_whatsapp, hora.hour, hora.minute)
else:
    print("No se encontró ningún correo del remitente especificado.")
