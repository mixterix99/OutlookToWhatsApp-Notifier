import sqlite3
import os

os.makedirs(os.path.join("app","instance"),exist_ok=True)

DB_PATH = os.path.join("instance", "notificador.db")


def conectar():
    return sqlite3.connect(DB_PATH)

# ---------- REMITENTES ----------

def agregar_remitente(email, nombre, activo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO remitentes (email, nombre, activo) VALUES (?, ?, ?)",
                   (email, nombre, activo))
    conn.commit()
    conn.close()


def listar_remitentes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, activo FROM remitentes WHERE activo = 1")
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

def listar_destinatarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.numero, d.nombre, r.email
        FROM destinatarios d
        JOIN remitentes r ON d.id_remitente = r.id
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos

def listar_destinatarios_por_remitente(id_remitente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero, nombre FROM destinatarios WHERE id_remitente = ?", (id_remitente,))
    datos = cursor.fetchall()
    conn.close()
    return datos
