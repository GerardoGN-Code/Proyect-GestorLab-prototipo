import sqlite3
import os

def conectar():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))

    ruta_db = os.path.join(directorio_actual, "GestorLab.db")

    try:
        conexion = sqlite3.connect(ruta_db)
        return conexion
    except sqlite3.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None