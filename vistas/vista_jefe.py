import tkinter as tk
from tkinter import filedialog, messagebox
from logica.procesador_horario import procesar_y_guardar_horario

class VentanaJefe:
    def __init__(self, root, matricula, nombre_completo):
        self.root = root
        self.matricula = matricula
        self.nombre_completo = nombre_completo
        
        self.root.title(f"GestorLab - Panel Jefatura ({self.nombre_completo})")
        self.root.geometry("800x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f9")
        
        self.color_verde = "#11693e"
        self.color_blanco = "#ffffff"
        
        self.centrar_ventana(800, 500)
        self.crear_interfaz()

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def crear_interfaz(self):
        frame_header = tk.Frame(self.root, bg=self.color_verde, height=80)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)

        tk.Label(frame_header, text="Jefatura de Carrera ISC", font=("Arial", 16, "bold"), bg=self.color_verde, fg="white").pack(side="left", padx=20)
        
        btn_salir = tk.Button(frame_header, text="Cerrar Sesion", font=("Arial", 9, "bold"), bg="#c82333", fg="white", activebackground="#bd2130", activeforeground="white", relief="flat", cursor="hand2", command=self.cerrar_sesion)
        btn_salir.pack(side="right", padx=20)

        tk.Label(frame_header, text=f"Usuario: {self.nombre_completo}", font=("Arial", 10), bg=self.color_verde, fg="#d1e8dd").pack(side="right", padx=15)

        frame_cuerpo = tk.Frame(self.root, bg="#f4f6f9")
        frame_cuerpo.pack(fill="both", expand=True, padx=40, pady=40)

        tarjeta = tk.Frame(frame_cuerpo, bg=self.color_blanco, relief="solid", bd=1)
        tarjeta.place(relx=0.5, rely=0.4, anchor="center", width=500, height=250)

        tk.Label(tarjeta, text="Cargar Horario Semestral", font=("Arial", 14, "bold"), bg=self.color_blanco, fg="#333333").pack(pady=(30, 10))
        
        instrucciones = "Sube el documento oficial de horarios en formato PDF"
        tk.Label(tarjeta, text=instrucciones, font=("Arial", 10), bg=self.color_blanco, fg="#666666", justify="center").pack(pady=(0, 25))

        btn_subir = tk.Button(tarjeta, text="Seleccionar Archivo PDF", font=("Arial", 11, "bold"), bg=self.color_verde, fg="white", activebackground="#0e5934", activeforeground="white", relief="flat", cursor="hand2", command=self.cargar_pdf)
        btn_subir.pack(ipady=8, ipadx=15)

    def cargar_pdf(self):
        ruta_pdf = filedialog.askopenfilename(
            title="Seleccionar Horario",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if ruta_pdf:
            messagebox.showinfo("Procesando", "El documento se está escaneando\nEsto puede tardar unos segundos dependiendo del tamaño del PDF")
            
            exito, mensaje = procesar_y_guardar_horario(ruta_pdf)
            
            if exito:
                messagebox.showinfo("Asignacion Exitosa", mensaje)
            else:
                messagebox.showerror("Error en el Proceso", mensaje)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesion", "¿Estás seguro de que deseas cerrar tu sesion?"):
            self.root.destroy()
            
            from vistas.login import VentanaLogin 
            
            nueva_raiz = tk.Tk()
            app = VentanaLogin(nueva_raiz)
            nueva_raiz.mainloop()