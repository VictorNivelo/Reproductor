from Controlador.Controlador import ControladorReproductor
from Vista.Vista import VistaReproductor
from Modelo.Cancion import Biblioteca
import tkinter as tk


def main():
    root = tk.Tk()
    modelo = Biblioteca()
    controlador = ControladorReproductor(modelo, None)
    vista = VistaReproductor(root, controlador)
    controlador.vista = vista
    controlador.iniciar()
    root.mainloop()


if __name__ == "__main__":
    main()
