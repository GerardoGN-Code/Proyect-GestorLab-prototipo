import tkinter as tk
from tkinter import messagebox
from base_datos.operaciones import verificar_credenciales
from vistas.vista_jefe import VentanaJefe
from vistas.vista_admin import VentanaAdmin
from vistas.vista_docente import VentanaDocente

class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("GestorLab - Inicio de Sesion")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        
        self.color_verde = "#11693e"
        self.color_blanco = "#ffffff"
        self.color_gris_texto = "#666666"
        self.color_fondo_input = "#f7f7f7"
        self.color_borde = "#e0e0e0"

        self.centrar_ventana(900, 550)
        self.crear_interfaz()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_interfaz(self):
        panel_izquierdo = tk.Frame(self.root, bg=self.color_verde, width=400)
        panel_izquierdo.pack(side="left", fill="y")
        panel_izquierdo.pack_propagate(False)

        tk.Label(panel_izquierdo, text="TESCHI", font=("Arial", 18, "bold"), bg=self.color_verde, fg="white").pack(anchor="w", padx=40, pady=(40, 0))
        tk.Label(panel_izquierdo, text="Tecnologico de Estudios Superiores de Chimalhuacan", font=("Arial", 9), bg=self.color_verde, fg="#d1e8dd").pack(anchor="w", padx=40)

        frame_bienvenida = tk.Frame(panel_izquierdo, bg=self.color_verde)
        frame_bienvenida.place(x=40, rely=0.5, anchor="w")
        tk.Label(frame_bienvenida, text="Bienvenido a\nGestorLab", font=("Arial", 28, "bold"), bg=self.color_verde, fg="white", justify="left").pack(anchor="w")


        panel_derecho = tk.Frame(self.root, bg=self.color_blanco)
        panel_derecho.pack(side="right", fill="both", expand=True)

        frame_form = tk.Frame(panel_derecho, bg=self.color_blanco)
        frame_form.place(relx=0.1, rely=0.5, anchor="w", width=380)

        tk.Label(frame_form, text="Iniciar sesion", font=("Arial", 22, "bold"), bg=self.color_blanco, fg="#333333").pack(anchor="w")

        frame_usuario = tk.Frame(frame_form, bg=self.color_blanco)
        frame_usuario.pack(fill="x", pady=(20, 5))
        tk.Label(frame_usuario, text="Usuario", font=("Arial", 9, "bold"), bg=self.color_blanco, fg="#333333").pack(side="left")
        
        self.entry_matricula = tk.Entry(frame_form, font=("Arial", 11), bg=self.color_fondo_input, relief="solid", highlightbackground=self.color_borde, highlightthickness=1, bd=0)
        self.entry_matricula.pack(fill="x", ipady=8)

        frame_pass = tk.Frame(frame_form, bg=self.color_blanco)
        frame_pass.pack(fill="x", pady=(20, 5))
        tk.Label(frame_pass, text="Contraseña", font=("Arial", 9, "bold"), bg=self.color_blanco, fg="#333333").pack(side="left")
        
        self.entry_contrasena = tk.Entry(frame_form, font=("Arial", 11), bg=self.color_fondo_input, relief="solid", highlightbackground=self.color_borde, highlightthickness=1, bd=0)
        self.entry_contrasena.pack(fill="x", ipady=8)

        btn_ingresar = tk.Button(frame_form, text="Iniciar sesion", font=("Arial", 11, "bold"), bg=self.color_verde, fg="white", activebackground="#0e5934", activeforeground="white", relief="flat", cursor="hand2", command=self.validar_acceso)
        btn_ingresar.pack(fill="x", pady=(30, 20), ipady=10)

    def validar_acceso(self):
        matricula = self.entry_matricula.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        if not matricula or not contrasena:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa tu matrícula y contraseña.")
            return

        usuario = verificar_credenciales(matricula, contrasena)

        if usuario:
            mat, nombre_completo, rol = usuario
            messagebox.showinfo("Acceso Concedido", f"Bienvenido, {nombre_completo}")
            self.root.destroy()
            self.abrir_panel(mat, nombre_completo, rol)
        else:
            messagebox.showerror("Error de Acceso", "Matrícula o contraseña incorrectos.")

    def abrir_panel(self, matricula, nombre_completo, rol):
        nueva_ventana = tk.Tk()
        if rol == 'Administrador':
            app = VentanaAdmin(nueva_ventana, matricula, nombre_completo)
        elif rol == 'Jefe_Carrera':
            app = VentanaJefe(nueva_ventana, matricula, nombre_completo)
        elif rol == 'Docente':
            app = VentanaDocente(nueva_ventana, matricula, nombre_completo)