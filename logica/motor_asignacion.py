from base_datos.conexion import conectar

def ejecutar_asignacion_automatica(datos_horario):
    conexion = conectar()
    if not conexion:
        return False

    cursor = conexion.cursor()
    asignaciones_exitosas = 0

    try:
        cursor.execute("DELETE FROM asignaciones")

        for clase in datos_horario:
            cursor.execute("SELECT horas_laboratorio, software_requerido FROM reticula_isc WHERE clave_materia = ?", (clase['materia'],))
            materia_info = cursor.fetchone()

            if not materia_info:
                continue

            query_disponibilidad = """
                SELECT id_lab FROM laboratorios 
                WHERE id_lab NOT IN (
                    SELECT id_lab FROM asignaciones 
                    WHERE dia_semana = ? AND (
                        (hora_inicio < ? AND hora_fin > ?) -- El horario se empalma
                    )
                )
            """
            cursor.execute(query_disponibilidad, (clase['dia'], clase['fin'], clase['inicio']))
            labs_disponibles = cursor.fetchall()

            if labs_disponibles:
                id_lab_asignado = labs_disponibles[0][0]

                query_insert = """
                    INSERT INTO asignaciones 
                    (matricula_docente, clave_materia, grupo, id_lab, dia_semana, hora_inicio, hora_fin)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query_insert, (
                    clase['docente'], clase['materia'], clase['grupo'], 
                    id_lab_asignado, clase['dia'], clase['inicio'], clase['fin']
                ))
                asignaciones_exitosas += 1

        conexion.commit()
        return asignaciones_exitosas

    except Exception as e:
        print(f"Error en el motor de asignación: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()
        