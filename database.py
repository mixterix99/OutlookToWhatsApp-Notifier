import sqlite3

def crear_bd():
    conn = sqlite3.connect('notificador.db')
    c = conn.cursor()

    # Tabla de remitentes a monitorear
    c.execute('''
        CREATE TABLE IF NOT EXISTS remitentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            nombre TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')

    # Tabla de destinatarios (pueden haber varios por remitente)
    c.execute('''
        CREATE TABLE IF NOT EXISTS destinatarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_remitente INTEGER,
            numero TEXT NOT NULL,
            nombre TEXT,
            FOREIGN KEY (id_remitente) REFERENCES remitentes(id)
        )
    ''')

    # Tabla de notificaciones enviadas
    c.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asunto TEXT,
            fecha_correo TEXT,
            entry_id TEXT,
            archivos TEXT,
            enlaces_drive TEXT,
            resultado TEXT,
            timestamp_envio TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_bd()
    print("✅ Base de datos creada correctamente.")
