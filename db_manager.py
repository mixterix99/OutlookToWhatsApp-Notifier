import sqlite3

DB_PATH = "notificador.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# ---------- REMITENTES ----------

def agregar_remitente(email, nombre=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO remitentes (email, nombre) VALUES (?, ?)", (email, nombre))
    conn.commit()
    conn.close()
    print(f"✅ Remitente agregado: {email}")

def listar_remitentes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, nombre, activo FROM remitentes")
    datos = cursor.fetchall()
    conn.close()
    return datos

# ---------- DESTINATARIOS ----------

def agregar_destinatario(id_remitente, numero, nombre=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO destinatarios (id_remitente, numero, nombre) VALUES (?, ?, ?)", (id_remitente, numero, nombre))
    conn.commit()
    conn.close()
    print(f"📱 Destinatario agregado para remitente {id_remitente}: {numero}")

def listar_destinatarios_por_remitente(id_remitente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero, nombre FROM destinatarios WHERE id_remitente = ?", (id_remitente,))
    datos = cursor.fetchall()
    conn.close()
    return datos
