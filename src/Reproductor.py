from Controlador.Controlador import ControladorReproductor
from Vista.Vista import VistaReproductor
from Modelo.Cancion import Biblioteca
import tkinter as tk


def iniciar_aplicacion():
    ventana_principal = tk.Tk()
    biblioteca = Biblioteca()
    controlador = ControladorReproductor(biblioteca, None)
    vista = VistaReproductor(ventana_principal, controlador)
    controlador.vista = vista
    controlador.iniciar()
    ventana_principal.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()
