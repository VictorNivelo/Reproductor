import customtkinter as ctk
from Controlador.Controlador import ControladorReproductor
from Vista.Vista import VistaReproductor
from Modelo.Cancion import Biblioteca


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    modelo = Biblioteca()
    vista = VistaReproductor(root)
    controlador = ControladorReproductor(modelo, vista)
    controlador.iniciar()
    root.mainloop()


if __name__ == "__main__":
    main()
