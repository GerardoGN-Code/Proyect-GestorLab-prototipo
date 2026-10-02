from base_datos.conexion import conectar

def verificar_credenciales(matricula, contrasena):

    conexion = conectar()
    if not conexion:
        return None

    try:
        cursor = conexion.cursor()

        query = """
            SELECT matricula, nombre_completo, rol 
            FROM usuarios 
            WHERE matricula = ? AND contrasena = ?
        """

        cursor.execute(query, (matricula, contrasena))

        usuario = cursor.fetchone()

        return usuario

    except Exception as e:
        print(f"Error al verificar credenciales: {e}")
        return None
    finally:
        conexion.close()