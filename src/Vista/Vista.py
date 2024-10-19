from customtkinter import CTkScrollableFrame, CTkButton, CTkImage
from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk


class VistaReproductor:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self.root.title("Reproductor de Música")
        self.root.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._crear_widgets()
        self._configurar_listas_personalizadas()

    def _crear_widgets(self):
        self.frame_principal = ctk.CTkFrame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_izquierdo = ctk.CTkFrame(self.frame_principal, width=300)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        self.frame_derecho = ctk.CTkFrame(self.frame_principal)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._crear_widgets_izquierdos()
        self._crear_widgets_derechos()

    def _crear_widgets_izquierdos(self):
        self.caratula = ctk.CTkLabel(self.frame_izquierdo, text="")
        self.caratula.pack(pady=10)
        self.titulo = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.titulo.pack()
        self.artista = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=14))
        self.artista.pack()
        self.album = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=12))
        self.album.pack()
        self.barra_progreso = ctk.CTkProgressBar(self.frame_izquierdo, width=250)
        self.barra_progreso.pack(pady=10)
        self.frame_tiempo = ctk.CTkFrame(self.frame_izquierdo)
        self.frame_tiempo.pack(fill=tk.X, pady=5)
        self.tiempo_actual = ctk.CTkLabel(self.frame_tiempo, text="0:00")
        self.tiempo_actual.pack(side=tk.LEFT, padx=10)
        self.tiempo_total = ctk.CTkLabel(self.frame_tiempo, text="0:00")
        self.tiempo_total.pack(side=tk.RIGHT, padx=10)
        self.frame_controles = ctk.CTkFrame(self.frame_izquierdo)
        self.frame_controles.pack(pady=10)
        self.boton_anterior = ctk.CTkButton(self.frame_controles, text="⏮", width=40)
        self.boton_anterior.pack(side=tk.LEFT, padx=5)
        self.boton_retroceder = ctk.CTkButton(self.frame_controles, text="⏪", width=40)
        self.boton_retroceder.pack(side=tk.LEFT, padx=5)
        self.boton_reproducir_pausar = ctk.CTkButton(self.frame_controles, text="▶", width=40)
        self.boton_reproducir_pausar.pack(side=tk.LEFT, padx=5)
        self.boton_adelantar = ctk.CTkButton(self.frame_controles, text="⏩", width=40)
        self.boton_adelantar.pack(side=tk.LEFT, padx=5)
        self.boton_siguiente = ctk.CTkButton(self.frame_controles, text="⏭", width=40)
        self.boton_siguiente.pack(side=tk.LEFT, padx=5)
        self.frame_controles_adicionales = ctk.CTkFrame(self.frame_izquierdo)
        self.frame_controles_adicionales.pack(pady=5)
        self.boton_aleatorio = ctk.CTkButton(self.frame_controles_adicionales, text="🔀", width=40)
        self.boton_aleatorio.pack(side=tk.LEFT, padx=5)
        self.boton_repetir = ctk.CTkButton(self.frame_controles_adicionales, text="🔁", width=40)
        self.boton_repetir.pack(side=tk.LEFT, padx=5)
        self.boton_favorito = ctk.CTkButton(self.frame_controles_adicionales, text="⭐", width=40)
        self.boton_favorito.pack(side=tk.LEFT, padx=5)
        self.boton_me_gusta = ctk.CTkButton(self.frame_controles_adicionales, text="❤", width=40)
        self.boton_me_gusta.pack(side=tk.LEFT, padx=5)
        self.boton_mostrar_cola = ctk.CTkButton(self.frame_controles_adicionales, text="👁", width=40)
        self.boton_mostrar_cola.pack(side=tk.LEFT, padx=5)
        self.boton_agregar_cola = ctk.CTkButton(self.frame_controles_adicionales, text="➕", width=40)
        self.boton_agregar_cola.pack(side=tk.LEFT, padx=5)
        self.frame_volumen = ctk.CTkFrame(self.frame_izquierdo)
        self.frame_volumen.pack(pady=10, fill=tk.X)
        self.boton_mute = ctk.CTkButton(self.frame_volumen, text="🔊", width=40)
        self.boton_mute.pack(side=tk.LEFT, padx=5)
        self.volumen_slider = ctk.CTkSlider(self.frame_volumen, from_=0, to=100)
        self.volumen_slider.set(100)
        self.volumen_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _crear_widgets_derechos(self):
        self.frame_busqueda = ctk.CTkFrame(self.frame_derecho)
        self.frame_busqueda.pack(fill=tk.X, pady=10)
        self.entrada_busqueda = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Buscar canción...")
        self.entrada_busqueda.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar_cancion)
        self.frame_ordenar = ctk.CTkFrame(self.frame_derecho)
        self.frame_ordenar.pack(fill=tk.X, pady=10)
        self.label_ordenar = ctk.CTkLabel(self.frame_ordenar, text="Ordenar por:")
        self.label_ordenar.pack(side=tk.LEFT, padx=(0, 10))
        opciones_ordenar = ["Título", "Artista", "Álbum", "Año"]
        self.combobox_ordenar = ctk.CTkComboBox(
            self.frame_ordenar, values=opciones_ordenar, command=self._ordenar_canciones
        )
        self.combobox_ordenar.pack(side=tk.LEFT)
        self.notebook = ctk.CTkTabview(self.frame_derecho)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tab_todas = self.notebook.add("Todas")
        self.tab_me_gusta = self.notebook.add("Me gusta")
        self.tab_favoritos = self.notebook.add("Favoritos")
        self.tab_personalizadas = self.notebook.add("Listas personalizadas")
        self._crear_lista_canciones(self.tab_todas, "lista_canciones")
        self._crear_lista_canciones(self.tab_me_gusta, "lista_me_gusta")
        self._crear_lista_canciones(self.tab_favoritos, "lista_favoritos")
        self._crear_listas_personalizadas(self.tab_personalizadas)
        self.frame_botones_inferiores = ctk.CTkFrame(self.frame_derecho)
        self.frame_botones_inferiores.pack(fill=tk.X, pady=10)
        self.boton_seleccionar_carpeta = ctk.CTkButton(self.frame_botones_inferiores, text="Seleccionar carpeta")
        self.boton_seleccionar_carpeta.pack(side=tk.LEFT, padx=5)
        self.boton_importar = ctk.CTkButton(self.frame_botones_inferiores, text="Importar lista")
        self.boton_importar.pack(side=tk.LEFT, padx=5)
        self.boton_exportar = ctk.CTkButton(self.frame_botones_inferiores, text="Exportar lista")
        self.boton_exportar.pack(side=tk.LEFT, padx=5)
        self.boton_seleccionar_carpeta.configure(command=self.controlador.seleccionar_carpeta)
        self.boton_importar.configure(command=self.controlador.importar_lista)
        self.boton_exportar.configure(command=self.controlador.exportar_lista)

    def _crear_lista_canciones(self, parent, nombre):
        lista = ctk.CTkScrollableFrame(parent, height=300)
        lista.pack(fill=tk.BOTH, expand=True)
        setattr(self, nombre, lista)

    def _crear_listas_personalizadas(self, parent):
        self.frame_listas_personalizadas = ctk.CTkFrame(parent)
        self.frame_listas_personalizadas.pack(fill=tk.BOTH, expand=True)
        self.lista_personalizadas = CTkScrollableFrame(self.frame_listas_personalizadas, height=250)
        self.lista_personalizadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_botones_listas = ctk.CTkFrame(self.frame_listas_personalizadas)
        self.frame_botones_listas.pack(side=tk.RIGHT, fill=tk.Y)
        self.boton_nueva_lista = ctk.CTkButton(self.frame_botones_listas, text="Nueva lista")
        self.boton_nueva_lista.pack(pady=5)
        self.boton_eliminar_lista = ctk.CTkButton(self.frame_botones_listas, text="Eliminar lista")
        self.boton_eliminar_lista.pack(pady=5)
        self.boton_modificar_lista = ctk.CTkButton(self.frame_botones_listas, text="Modificar lista")
        self.boton_modificar_lista.pack(pady=5)
        self.botones_listas_personalizadas = []

    def actualizar_lista_canciones(self, canciones, lista_nombre="lista_canciones"):
        lista = getattr(self, lista_nombre)
        for widget in lista.winfo_children():
            widget.destroy()
        for cancion in canciones:
            boton_cancion = ctk.CTkButton(
                lista,
                text=f"{cancion.titulo} - {cancion.artista}",
                anchor="w",
                command=lambda c=cancion: self.controlador.reproducir_cancion(c),
            )
            boton_cancion.pack(fill=tk.X, pady=2)

    def actualizar_cancion(self, cancion):
        self.titulo.configure(text=cancion.titulo)
        self.artista.configure(text=cancion.artista)
        self.album.configure(text=cancion.album)
        duracion = f"{int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}"
        self.tiempo_total.configure(text=duracion)
        if cancion.caratula:
            img = CTkImage(light_image=cancion.caratula, size=(200, 200))
            self.caratula.configure(image=img)
        else:
            self.caratula.configure(image=None, text="Sin carátula")
        self.barra_progreso.set(0)
        self.tiempo_actual.configure(text="0:00")

    def actualizar_listas_personalizadas(self, listas):
        for widget in self.lista_personalizadas.winfo_children():
            widget.destroy()
        self.botones_listas_personalizadas = []
        for nombre in listas.keys():
            boton = CTkButton(
                self.lista_personalizadas,
                text=nombre,
                command=lambda n=nombre: self.controlador.seleccionar_lista_personalizada(n),
            )
            boton.pack(fill=tk.X, pady=2)
            self.botones_listas_personalizadas.append(boton)

    def actualizar_progreso(self, valor, tiempo_actual):
        self.barra_progreso.set(valor)
        minutos, segundos = divmod(int(tiempo_actual), 60)
        self.tiempo_actual.configure(text=f"{minutos}:{segundos:02d}")

    def actualizar_boton_reproducir_pausar(self, reproduciendo, pausado):
        self.boton_reproducir_pausar.configure(text="⏸" if reproduciendo and not pausado else "▶")

    def actualizar_boton_aleatorio(self, activo):
        self.boton_aleatorio.configure(fg_color="#22559b" if activo else "transparent")

    def actualizar_boton_repetir(self, activo):
        self.boton_repetir.configure(fg_color="#22559b" if activo else "transparent")

    def actualizar_boton_me_gusta(self, activo):
        self.boton_me_gusta.configure(fg_color="#22559b" if activo else "transparent")

    def actualizar_icono_volumen(self, volumen):
        if volumen == 0:
            self.boton_mute.configure(text="🔇")
        elif volumen < 0.5:
            self.boton_mute.configure(text="🔉")
        else:
            self.boton_mute.configure(text="🔊")

    def seleccionar_directorio(self):
        return ctk.filedialog.askdirectory()

    def mostrar_dialogo_nueva_lista(self):
        return ctk.CTkInputDialog(text="Nombre de la lista:", title="Nueva lista").get_input()

    def mostrar_dialogo_modificar_lista(self, nombre_actual):
        return ctk.CTkInputDialog(text="Nuevo nombre de la lista:", title="Modificar lista").get_input()

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def mostrar_info(self, mensaje):
        messagebox.showinfo("Información", mensaje)

    def seleccionar_ruta_abrir(self):
        return ctk.filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("TXT", "*.txt")])

    def seleccionar_ruta_guardar(self, extension):
        return ctk.filedialog.asksaveasfilename(
            defaultextension=f".{extension}",
            filetypes=[(extension.upper(), f"*.{extension}")],
            initialdir=".",
            title="Guardar lista como",
        )

    def mostrar_dialogo_formato(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Exportar Lista")
        dialog.geometry("300x200")
        dialog.grab_set()
        frame = ctk.CTkFrame(dialog)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Seleccione formato de exportación:").pack(pady=10)
        formato = tk.StringVar(value="txt")
        ctk.CTkRadioButton(frame, text="TXT", variable=formato, value="txt").pack(pady=5)
        ctk.CTkRadioButton(frame, text="JSON", variable=formato, value="json").pack(pady=5)
        result = tk.StringVar()

        def on_accept():
            result.set(formato.get())
            dialog.destroy()

        def on_cancel():
            result.set("")
            dialog.destroy()

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Aceptar", command=on_accept).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT, padx=5)
        dialog.wait_window()
        return result.get() if result.get() else None

    def _buscar_cancion(self, event):
        self.controlador.buscar_cancion(self.entrada_busqueda.get())

    def _ordenar_canciones(self, criterio):
        self.controlador.ordenar_canciones(criterio.lower())

    def mostrar_cola(self, cola):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Cola de Reproducción")
        dialog.geometry("400x300")
        dialog.grab_set()
        frame = ctk.CTkScrollableFrame(dialog)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        if not cola:
            ctk.CTkLabel(frame, text="La cola está vacía").pack(pady=10)
        else:
            for cancion in cola:
                ctk.CTkLabel(frame, text=f"{cancion.titulo} - {cancion.artista}").pack(pady=2, anchor="w")
        ctk.CTkButton(dialog, text="Cerrar", command=dialog.destroy).pack(pady=10)

    def _configurar_listas_personalizadas(self):
        self.lista_personalizadas.bind("<Double-1>", self.controlador.seleccionar_lista_personalizada)
