import sqlite3
import os

def construir():
    if os.path.exists("repuestos.db"):
        os.remove("repuestos.db")
        print("-> Base de datos anterior eliminada.")

    conn = sqlite3.connect("repuestos.db")
    cursor = conn.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    print("✓ Esquema y Vista Pública creados.")

    with open("seed.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    print("✓ Datos de prueba insertados.")

    conn.commit()
    conn.close()
    print("¡Base de datos 'repuestos.db' generada exitosamente!")

if __name__ == "__main__":
    construir()