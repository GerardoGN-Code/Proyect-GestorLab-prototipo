import pdfplumber
import re
import unicodedata
import difflib
from logica.motor_asignacion import ejecutar_asignacion_automatica
from base_datos.conexion import conectar

USUARIOS_DB = []
RETICULA_DB = []

def cargar_catalogos():
    global USUARIOS_DB, RETICULA_DB
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT matricula, nombre_completo FROM usuarios")
        USUARIOS_DB = cursor.fetchall()
        
        cursor.execute("SELECT clave_materia, nombre_materia, horas_laboratorio FROM reticula_isc")
        RETICULA_DB = cursor.fetchall()
        conexion.close()

def normalizar(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('utf-8')
    return texto.upper().replace('\n', ' ').strip()

def obtener_claves_inteligentes(nombre_docente, nombre_materia):
    docente_norm = normalizar(nombre_docente)
    materia_norm = normalizar(nombre_materia)
    
    matricula_match = None
    mejor_ratio_doc = 0.0
    for doc in USUARIOS_DB:
        ratio = difflib.SequenceMatcher(None, docente_norm, normalizar(doc[1])).ratio()
        if ratio > 0.75 and ratio > mejor_ratio_doc:  
            mejor_ratio_doc = ratio
            matricula_match = doc[0]
            
    clave_mat_match = None
    limite_horas = 0
    mejor_ratio_mat = 0.0
    for mat in RETICULA_DB:
        ratio = difflib.SequenceMatcher(None, materia_norm, normalizar(mat[1])).ratio()
        if ratio > 0.80 and ratio > mejor_ratio_mat: 
            mejor_ratio_mat = ratio
            clave_mat_match = mat[0]
            limite_horas = mat[2]
            
    return matricula_match, clave_mat_match, limite_horas

def extraer_datos_pdf(ruta_pdf):
    cargar_catalogos()
    clases_extraidas = []
    
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_pagina = pagina.extract_text() or ""
                
                texto_limpio = texto_pagina.upper().replace(' ', '')
                match_grupo = re.search(r'([1-9]ISC[0-9]{2})', texto_limpio)
                grupo = match_grupo.group(1) if match_grupo else f"G_PAGINA_{i+1}"
                
                tablas = pagina.extract_tables()
                docentes_por_materia = {}
                
                for tabla in tablas:
                    for fila in tabla:
                        if not fila or fila[0] is None:
                            continue
                        
                        materia_dir = str(fila[0]).replace('\n', ' ').strip()
                        docente_dir = ""
                        for celda in fila[1:]:
                            if celda and isinstance(celda, str) and "@" not in celda:
                                docente_dir = celda.replace('\n', ' ').strip()
                                break
                                
                        if materia_dir and docente_dir and "ASIGNATURA" not in materia_dir.upper():
                            docentes_por_materia[normalizar(materia_dir)] = docente_dir
                
                for tabla in tablas:
                    for fila in tabla:
                        if not fila or fila[0] is None:
                            continue
                            
                        hora_cruda = str(fila[0])
                        
                        tiempos = re.findall(r'\d{2}:\d{2}', hora_cruda)
                        
                        if len(tiempos) >= 2:
                            inicio = tiempos[0]
                            fin = tiempos[1]
                            dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                            
                            for idx_dia, dia in enumerate(dias_semana):
                                if len(fila) > idx_dia + 1: 
                                    materia_celda = str(fila[idx_dia+1]).replace('\n', ' ').strip()
                                    
                                    if not materia_celda or "TUTORIA" in materia_celda.upper():
                                        continue
                                        
                                    docente_asignado = None
                                    materia_celda_norm = normalizar(materia_celda)
                                    
                                    for mat_dir_norm, doc_dir in docentes_por_materia.items():
                                        if difflib.SequenceMatcher(None, materia_celda_norm, mat_dir_norm).ratio() > 0.8:
                                            docente_asignado = doc_dir
                                            break
                                            
                                    if docente_asignado:
                                        matricula_doc, clave_mat, limite = obtener_claves_inteligentes(docente_asignado, materia_celda)
                                        
                                        if clave_mat and matricula_doc:
                                            clases_extraidas.append({
                                                'docente': matricula_doc, 
                                                'materia': clave_mat,     
                                                'grupo': grupo,
                                                'dia': dia,
                                                'inicio': inicio,
                                                'fin': fin,
                                                'limite_lab': limite
                                            })
                                            
        return clases_extraidas
    except Exception as e:
        print(f"Error al procesar el archivo PDF: {e}")
        return []

def procesar_y_guardar_horario(ruta_pdf):
    print("Escaneando documento de forma inteligente...")
    datos = extraer_datos_pdf(ruta_pdf)
    
    if not datos:
        return False, "No se encontraron asignaturas de carrera."
        
    datos_filtrados_lab = []
    conteo_horas = {} 
    
    for clase in datos:
        llave_conteo = f"{clase['grupo']}_{clase['materia']}"
        limite = clase['limite_lab']
        
        if limite == 0:
            continue
            
        if llave_conteo not in conteo_horas:
            conteo_horas[llave_conteo] = 0
            
        if conteo_horas[llave_conteo] < limite:
            datos_filtrados_lab.append(clase)
            conteo_horas[llave_conteo] += 1
            
    asignaciones_exitosas = ejecutar_asignacion_automatica(datos_filtrados_lab)
    
    if asignaciones_exitosas is not False:
        return True, f"Asignación completa. Se asignaron {asignaciones_exitosas} horas respetando la retícula."
    else:
        return False, "Error al guardar en base de datos."