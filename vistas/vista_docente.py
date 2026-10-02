import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from base_datos.conexion import conectar
from logica.generador_pdf import exportar_horario_pdf

class VentanaDocente:
    def __init__(self, root, matricula, nombre_completo):
        self.root = root
        self.matricula = matricula
        self.nombre_completo = nombre_completo
        
        self.root.title(f"GestorLab - Panel Docente ({self.nombre_completo})")
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
        self.cargar_grupos()
        self.cargar_datos()

    def crear_interfaz(self):
        frame_header = tk.Frame(self.root, bg=self.color_verde, height=70)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="Panel de Horarios - Docente", font=("Arial", 16, "bold"), bg=self.color_verde, fg="white").pack(side="left", padx=20)
        
        btn_salir = tk.Button(frame_header, text="Cerrar SesioSn", font=("Arial", 9, "bold"), bg="#c82333", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", cursor="hand2", command=self.cerrar_sesion)
        btn_salir.pack(side="right", padx=20)

        tk.Label(frame_header, text=f"Bienvenido, {self.nombre_completo}", font=("Arial", 10), bg=self.color_verde, fg="#d1e8dd").pack(side="right", padx=15)

        frame_controles = tk.Frame(self.root, bg="#f4f6f9")
        frame_controles.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(frame_controles, text="Mis Laboratorios Asignados", font=("Arial", 12, "bold"), bg="#f4f6f9", fg="#333").pack(side="left")

        btn_exportar = tk.Button(frame_controles, text="Exportar Mi Horario a PDF", font=("Arial", 10, "bold"), bg="#c82333", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", cursor="hand2", command=self.exportar_pdf)
        btn_exportar.pack(side="right", padx=5, ipadx=10, ipady=3)

        btn_actualizar = tk.Button(frame_controles, text="Refrescar", font=("Arial", 10, "bold"), bg=self.color_verde, fg="white", activebackground="#0e5934", activeforeground="white", relief="flat", cursor="hand2", command=self.cargar_datos)
        btn_actualizar.pack(side="right", padx=5, ipadx=10, ipady=3)

        frame_filtros = tk.Frame(self.root, bg="#e9ecef", bd=1, relief="solid")
        frame_filtros.pack(fill="x", padx=20, pady=(0, 15), ipady=5)

        tk.Label(frame_filtros, text="Filtrar por Grupo:", font=("Arial", 10, "bold"), bg="#e9ecef").pack(side="left", padx=10)
        self.combo_grupo = ttk.Combobox(frame_filtros, state="readonly", width=15)
        self.combo_grupo.pack(side="left", padx=(5, 15))

        btn_buscar = tk.Button(frame_filtros, text="Filtrar", font=("Arial", 9, "bold"), bg="#0052cc", fg="white", relief="flat", cursor="hand2", command=self.aplicar_filtro)
        btn_buscar.pack(side="left", padx=5, ipadx=10)

        btn_limpiar = tk.Button(frame_filtros, text="Ver Todos", font=("Arial", 9), bg="#6c757d", fg="white", relief="flat", cursor="hand2", command=self.limpiar_filtro)
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

        columnas = ("grupo", "materia", "dia", "inicio", "fin", "laboratorio")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tabla.yview)

        self.tabla.heading("grupo", text="Grupo")
        self.tabla.column("grupo", width=100, anchor="center")
        
        self.tabla.heading("materia", text="Materia")
        self.tabla.column("materia", width=300, anchor="w")
        
        self.tabla.heading("dia", text="Día")
        self.tabla.column("dia", width=120, anchor="center")
        
        self.tabla.heading("inicio", text="Inicio")
        self.tabla.column("inicio", width=80, anchor="center")
        
        self.tabla.heading("fin", text="Fin")
        self.tabla.column("fin", width=80, anchor="center")
        
        self.tabla.heading("laboratorio", text="Laboratorio Asignado")
        self.tabla.column("laboratorio", width=250, anchor="w")

        self.tabla.pack(fill="both", expand=True)

    def cargar_grupos(self):
        conexion = conectar()
        if not conexion: return
        cursor = conexion.cursor()
        
        cursor.execute("SELECT DISTINCT grupo FROM asignaciones WHERE matricula_docente = ? ORDER BY grupo", (self.matricula,))
        grupos = [fila[0] for fila in cursor.fetchall()]
        
        self.combo_grupo['values'] = ["Todos"] + grupos
        self.combo_grupo.current(0)
        conexion.close()

    def aplicar_filtro(self):
        grupo_seleccionado = self.combo_grupo.get()
        self.cargar_datos(filtro_grupo=grupo_seleccionado)

    def limpiar_filtro(self):
        self.combo_grupo.current(0)
        self.cargar_datos()

    def cargar_datos(self, filtro_grupo="Todos"):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        conexion = conectar()
        if not conexion: return
            
        try:
            cursor = conexion.cursor()
            query = """
                SELECT 
                    a.grupo, 
                    r.nombre_materia, 
                    a.dia_semana, 
                    a.hora_inicio, 
                    a.hora_fin, 
                    l.nombre_lab
                FROM asignaciones a
                JOIN reticula_isc r ON a.clave_materia = r.clave_materia
                JOIN laboratorios l ON a.id_lab = l.id_lab
                WHERE a.matricula_docente = ?
            """
            parametros = [self.matricula]
            
            if filtro_grupo != "Todos":
                query += " AND a.grupo = ?"
                parametros.append(filtro_grupo)
            
            query += """ ORDER BY 
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

    def exportar_pdf(self):
        registros = self.tabla.get_children()
        if not registros:
            messagebox.showwarning("Tabla vacia", "No tienes horarios asignados para exportar")
            return
            
        datos_para_pdf = []
        for reg in registros:
            valores = self.tabla.item(reg)['values']
            datos_para_pdf.append(valores)
            
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Mi_Horario_Laboratorio_{self.matricula}.pdf",
            title="Guardar Mi Horario",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if ruta_guardado:
            try:
                exportar_horario_pdf(
                    datos=datos_para_pdf, 
                    ruta_salida=ruta_guardado,  
                    titulo_documento="REPORTE INDIVIDUAL DE ASIGNACIONES DE LABORATORIO",
                    nombre_docente=self.nombre_completo
                )
                messagebox.showinfo("Éxito", f"El PDF se guardo correctamente en:\n{ruta_guardado}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar el PDF: {e}")

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesion", "¿Estás seguro de que deseas cerrar tu sesion?"):
            self.root.destroy()
            from vistas.login import VentanaLogin 
            nueva_raiz = tk.Tk()
            app = VentanaLogin(nueva_raiz)
            nueva_raiz.mainloop()