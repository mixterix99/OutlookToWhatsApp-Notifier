from db_manager import agregar_remitente, agregar_destinatario, listar_remitentes

# 👉 Agrega un remitente (correo desde el que recibes correos importantes)
agregar_remitente("diegopolo14@gmail.com", "Correo de prueba")

# 👉 Verifica qué ID se le asignó (importante para los destinatarios)
remitentes = listar_remitentes()
for r in remitentes:
    print(f"ID: {r[0]} | Email: {r[1]} | Nombre: {r[2]} | Activo: {r[3]}")

agregar_destinatario(1, "+573118926101", "Directora")
agregar_destinatario(1, "+573108343555", "Gerente")