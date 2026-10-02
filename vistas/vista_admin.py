import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from base_datos.conexion import conectar
from logica.generador_pdf import exportar_horario_pdf

class VentanaAdmin:
    def __init__(self, root, matricula, nombre_completo):
        self.root = root
        self.matricula = matricula
        self.nombre_completo = nombre_completo
        
        self.root.title(f"GestorLab - Panel Administrador ({self.nombre_completo})")
        self.root.geometry("1000x600")
        self.root.minsize(900, 500)
        
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)
            
        self.root.configure(bg="#f4f6f9")
        
        self.color_verde = "#11693e"
        self.color_blanco = "#ffffff"
        
        self.crear_interfaz()
        self.cargar_opciones_filtros()
        self.cargar_datos()

    def crear_interfaz(self):
        frame_header = tk.Frame(self.root, bg=self.color_verde, height=70)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="Panel de Administrador", font=("Arial", 16, "bold"), bg=self.color_verde, fg="white").pack(side="left", padx=20)
        
        btn_salir = tk.Button(frame_header, text="Cerrar Sesion", font=("Arial", 9, "bold"), bg="#c82333", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", cursor="hand2", command=self.cerrar_sesion)
        btn_salir.pack(side="right", padx=20)

        tk.Label(frame_header, text=f"Administrador: {self.nombre_completo}", font=("Arial", 10), bg=self.color_verde, fg="#d1e8dd").pack(side="right", padx=15)

        frame_controles = tk.Frame(self.root, bg="#f4f6f9")
        frame_controles.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(frame_controles, text="Horarios Generales de Laboratorios", font=("Arial", 12, "bold"), bg="#f4f6f9", fg="#333").pack(side="left")

        btn_exportar = tk.Button(frame_controles, text="Exportar a PDF", font=("Arial", 10, "bold"), bg="#c82333", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", cursor="hand2", command=self.exportar_pdf)
        btn_exportar.pack(side="right", padx=5, ipadx=10, ipady=3)

        btn_actualizar = tk.Button(frame_controles, text="Actualizar Tabla", font=("Arial", 10, "bold"), bg=self.color_verde, fg="white", activebackground="#0e5934", activeforeground="white", relief="flat", cursor="hand2", command=self.cargar_datos)
        btn_actualizar.pack(side="right", padx=5, ipadx=10, ipady=3)
        
        btn_editar = tk.Button(frame_controles, text="Editar Seleccionado", font=("Arial", 10, "bold"), bg="#ffc107", fg="#333", activebackground="#e0a800", relief="flat", cursor="hand2", command=self.abrir_edicion)
        btn_editar.pack(side="right", padx=5, ipadx=10, ipady=3)

        frame_filtros = tk.Frame(self.root, bg="#e9ecef", bd=1, relief="solid")
        frame_filtros.pack(fill="x", padx=20, pady=(0, 15), ipady=5)

        tk.Label(frame_filtros, text="Filtrar por:", font=("Arial", 10, "bold"), bg="#e9ecef").pack(side="left", padx=10)

        tk.Label(frame_filtros, text="Docente:", bg="#e9ecef").pack(side="left")
        self.combo_docente = ttk.Combobox(frame_filtros, state="readonly", width=35)
        self.combo_docente.pack(side="left", padx=(5, 15))

        tk.Label(frame_filtros, text="Laboratorio:", bg="#e9ecef").pack(side="left")
        self.combo_lab = ttk.Combobox(frame_filtros, state="readonly", width=25)
        self.combo_lab.pack(side="left", padx=(5, 15))

        tk.Label(frame_filtros, text="Hora Inicio:", bg="#e9ecef").pack(side="left")
        self.combo_hora = ttk.Combobox(frame_filtros, state="readonly", width=10)
        self.combo_hora.pack(side="left", padx=(5, 15))

        btn_buscar = tk.Button(frame_filtros, text="Buscar", font=("Arial", 9, "bold"), bg="#0052cc", fg="white", relief="flat", cursor="hand2", command=self.aplicar_filtros)
        btn_buscar.pack(side="left", padx=5, ipadx=10)

        btn_limpiar = tk.Button(frame_filtros, text="Limpiar Filtros", font=("Arial", 9), bg="#6c757d", fg="white", relief="flat", cursor="hand2", command=self.limpiar_filtros)
        btn_limpiar.pack(side="left", padx=5, ipadx=10)

        frame_tabla = tk.Frame(self.root, bg=self.color_blanco, bd=1, relief="solid")
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e9ecef", foreground="#333")
        style.configure("Treeview", font=("Arial", 9), rowheight=25)
        style.map("Treeview", background=[("selected", self.color_verde)])

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        columnas = ("id", "grupo", "materia", "docente", "dia", "inicio", "fin", "laboratorio")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", yscrollcommand=scroll_y.set)
        
        scroll_y.config(command=self.tabla.yview)

        self.tabla.heading("id", text="ID")
        self.tabla.column("id", width=0, stretch=tk.NO)
        
        self.tabla.heading("grupo", text="Grupo")
        self.tabla.column("grupo", width=80, anchor="center")
        
        self.tabla.heading("materia", text="Materia")
        self.tabla.column("materia", width=250, anchor="w")
        
        self.tabla.heading("docente", text="Docente")
        self.tabla.column("docente", width=200, anchor="w")
        
        self.tabla.heading("dia", text="Día")
        self.tabla.column("dia", width=100, anchor="center")
        
        self.tabla.heading("inicio", text="Inicio")
        self.tabla.column("inicio", width=70, anchor="center")
        
        self.tabla.heading("fin", text="Fin")
        self.tabla.column("fin", width=70, anchor="center")
        
        self.tabla.heading("laboratorio", text="Laboratorio Asignado")
        self.tabla.column("laboratorio", width=200, anchor="w")

        self.tabla.pack(fill="both", expand=True)

    def cargar_opciones_filtros(self):
        conexion = conectar()
        if not conexion: return
        cursor = conexion.cursor()
        
        cursor.execute("SELECT DISTINCT u.nombre_completo FROM asignaciones a JOIN usuarios u ON a.matricula_docente = u.matricula ORDER BY u.nombre_completo")
        self.combo_docente['values'] = ["Todos"] + [fila[0] for fila in cursor.fetchall()]
        self.combo_docente.current(0)
        
        cursor.execute("SELECT DISTINCT l.nombre_lab FROM asignaciones a JOIN laboratorios l ON a.id_lab = l.id_lab ORDER BY l.nombre_lab")
        self.combo_lab['values'] = ["Todos"] + [fila[0] for fila in cursor.fetchall()]
        self.combo_lab.current(0)
        
        cursor.execute("SELECT DISTINCT hora_inicio FROM asignaciones ORDER BY hora_inicio")
        self.combo_hora['values'] = ["Todas"] + [fila[0] for fila in cursor.fetchall()]
        self.combo_hora.current(0)
        
        conexion.close()

    def aplicar_filtros(self):
        self.cargar_datos(self.combo_docente.get(), self.combo_lab.get(), self.combo_hora.get())

    def limpiar_filtros(self):
        self.combo_docente.current(0)
        self.combo_lab.current(0)
        self.combo_hora.current(0)
        self.cargar_datos()

    def cargar_datos(self, filtro_docente="Todos", filtro_lab="Todos", filtro_hora="Todas"):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        conexion = conectar()
        if not conexion: return
            
        try:
            cursor = conexion.cursor()
            query = """
                SELECT 
                    a.id_asignacion,
                    a.grupo, 
                    r.nombre_materia, 
                    u.nombre_completo, 
                    a.dia_semana, 
                    a.hora_inicio, 
                    a.hora_fin, 
                    l.nombre_lab
                FROM asignaciones a
                JOIN reticula_isc r ON a.clave_materia = r.clave_materia
                JOIN usuarios u ON a.matricula_docente = u.matricula
                JOIN laboratorios l ON a.id_lab = l.id_lab
                WHERE 1=1
            """
            
            parametros = []
            if filtro_docente != "Todos":
                query += " AND u.nombre_completo = ?"
                parametros.append(filtro_docente)
            if filtro_lab != "Todos":
                query += " AND l.nombre_lab = ?"
                parametros.append(filtro_lab)
            if filtro_hora != "Todas":
                query += " AND a.hora_inicio = ?"
                parametros.append(filtro_hora)
            
            query += """ ORDER BY 
                    a.grupo ASC,
                    CASE a.dia_semana 
                        WHEN 'Lunes' THEN 1 WHEN 'Martes' THEN 2 WHEN 'Miércoles' THEN 3 
                        WHEN 'Jueves' THEN 4 WHEN 'Viernes' THEN 5 ELSE 6 
                    END,
                    a.hora_inicio ASC
            """
            
            cursor.execute(query, parametros)
            filas = cursor.fetchall()
            
            self.tabla.tag_configure('impar', background='#f9f9f9')
            self.tabla.tag_configure('par', background='#ffffff')
            
            for index, fila in enumerate(filas):
                tag = 'par' if index % 2 == 0 else 'impar'
                self.tabla.insert("", "end", values=fila, tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
        finally:
            conexion.close()

    def abrir_edicion(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla para editar")
            return

        valores = self.tabla.item(seleccion)['values']
        id_asignacion = valores[0]
        materia = valores[2]
        dia_actual = valores[4]
        inicio_actual = valores[5]
        fin_actual = valores[6]
        lab_actual = valores[7]

        ventana_edit = tk.Toplevel(self.root)
        ventana_edit.title("Editar Horario")
        
        ancho = 400
        alto = 400
        pantalla_ancho = ventana_edit.winfo_screenwidth()
        pantalla_alto = ventana_edit.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        
        ventana_edit.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana_edit.resizable(False, False)
        ventana_edit.configure(bg=self.color_blanco)
        ventana_edit.transient(self.root)
        ventana_edit.grab_set()

        tk.Label(ventana_edit, text="Editar Asignación", font=("Arial", 14, "bold"), bg=self.color_blanco).pack(pady=15)
        tk.Label(ventana_edit, text=f"Materia: {materia[:40]}...", font=("Arial", 9, "italic"), bg=self.color_blanco).pack(pady=(0, 15))

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_lab, nombre_lab FROM laboratorios")
        lista_labs = cursor.fetchall()
        conexion.close()
        
        nombres_labs = [lab[1] for lab in lista_labs]
        diccionario_labs = {lab[1]: lab[0] for lab in lista_labs} 

        frame_form = tk.Frame(ventana_edit, bg=self.color_blanco)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="Día:", font=("Arial", 10), bg=self.color_blanco).grid(row=0, column=0, sticky="e", pady=10, padx=5)
        combo_edit_dia = ttk.Combobox(frame_form, values=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"], state="readonly")
        combo_edit_dia.set(dia_actual)
        combo_edit_dia.grid(row=0, column=1, pady=10)

        tk.Label(frame_form, text="Hora Inicio:", font=("Arial", 10), bg=self.color_blanco).grid(row=1, column=0, sticky="e", pady=10, padx=5)
        combo_edit_inicio = ttk.Combobox(frame_form, values=[f"{str(i).zfill(2)}:00" for i in range(7, 21)], state="readonly")
        combo_edit_inicio.set(inicio_actual)
        combo_edit_inicio.grid(row=1, column=1, pady=10)

        tk.Label(frame_form, text="Hora Fin:", font=("Arial", 10), bg=self.color_blanco).grid(row=2, column=0, sticky="e", pady=10, padx=5)
        combo_edit_fin = ttk.Combobox(frame_form, values=[f"{str(i).zfill(2)}:00" for i in range(8, 22)], state="readonly")
        combo_edit_fin.set(fin_actual)
        combo_edit_fin.grid(row=2, column=1, pady=10)

        tk.Label(frame_form, text="Laboratorio:", font=("Arial", 10), bg=self.color_blanco).grid(row=3, column=0, sticky="e", pady=10, padx=5)
        combo_edit_lab = ttk.Combobox(frame_form, values=nombres_labs, state="readonly", width=25)
        combo_edit_lab.set(lab_actual)
        combo_edit_lab.grid(row=3, column=1, pady=10)

        def guardar_cambios():
            nuevo_dia = combo_edit_dia.get()
            nuevo_inicio = combo_edit_inicio.get()
            nuevo_fin = combo_edit_fin.get()
            nuevo_lab_nombre = combo_edit_lab.get()
            nuevo_lab_id = diccionario_labs[nuevo_lab_nombre]

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 1 FROM asignaciones 
                WHERE id_lab = ? AND dia_semana = ? AND id_asignacion != ?
                AND (hora_inicio < ? AND hora_fin > ?)
            """, (nuevo_lab_id, nuevo_dia, id_asignacion, nuevo_fin, nuevo_inicio))
            
            if cursor.fetchone():
                messagebox.showerror("Empalme Detectado", "El laboratorio seleccionado ya está ocupado en ese horario por otro grupo")
                conn.close()
                return

            try:
                cursor.execute("""
                    UPDATE asignaciones 
                    SET dia_semana = ?, hora_inicio = ?, hora_fin = ?, id_lab = ? 
                    WHERE id_asignacion = ?
                """, (nuevo_dia, nuevo_inicio, nuevo_fin, nuevo_lab_id, id_asignacion))
                conn.commit()
                messagebox.showinfo("Éxito", "El horario ha sido actualizado correctamente")
                ventana_edit.destroy()
                self.cargar_datos() 
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
            finally:
                conn.close()

        tk.Button(ventana_edit, text="Guardar Cambios", font=("Arial", 10, "bold"), bg=self.color_verde, fg="white", cursor="hand2", relief="flat", command=guardar_cambios).pack(pady=20, ipadx=10, ipady=5)

    def exportar_pdf(self):
        registros = self.tabla.get_children()
        if not registros:
            messagebox.showwarning("Tabla vacia", "No hay datos para exportar Ajusta los filtros")
            return
            
        datos_para_pdf = []
        for reg in registros:
            valores = self.tabla.item(reg)['values']
            datos_formateados = (valores[1], valores[2], valores[4], valores[5], valores[6], valores[7])
            datos_para_pdf.append(datos_formateados)
            
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile="Reporte_General_Laboratorios.pdf",
            title="Guardar Reporte",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if ruta_guardado:
            try:
                exportar_horario_pdf(datos_para_pdf, ruta_guardado, "REPORTE GENERAL DE ASIGNACIONES")
                messagebox.showinfo("Éxito", f"El PDF se guardó en:\n{ruta_guardado}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar el PDF: {e}")

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesion", "¿Estás seguro de que deseas cerrar tu sesion?"):
            self.root.destroy()
            from vistas.login import VentanaLogin 
            nueva_raiz = tk.Tk()
            app = VentanaLogin(nueva_raiz)
            nueva_raiz.mainloop()