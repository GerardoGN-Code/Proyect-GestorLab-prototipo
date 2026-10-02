import tkinter as tk
from vistas.login import VentanaLogin

def iniciar_aplicacion():

    root = tk.Tk()

    app = VentanaLogin(root)

    root.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()