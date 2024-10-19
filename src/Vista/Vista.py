from customtkinter import CTkScrollableFrame, CTkButton, CTkImage
from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk


class VistaReproductor:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self.root.title("Music Player")
        self.root.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._crear_widgets()
        self._configurar_listas_personalizadas()

    def _crear_widgets(self):
        self.frame_principal = ctk.CTkFrame(self.root, fg_color="#121212")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_izquierdo = ctk.CTkFrame(self.frame_principal, width=600, corner_radius=12, fg_color="#1E1E1E")
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(20, 10), pady=20)
        self.frame_derecho = ctk.CTkFrame(self.frame_principal, width=350, corner_radius=12, fg_color="#1E1E1E")
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 20), pady=20)
        self._crear_widgets_izquierdos()
        self._crear_widgets_derechos()

    def _crear_widgets_izquierdos(self):
        self.caratula = ctk.CTkLabel(self.frame_izquierdo, text="", width=300, height=300)
        self.caratula.pack(pady=15)
        self.titulo = ctk.CTkLabel(
            self.frame_izquierdo, text="", font=ctk.CTkFont(family="Roboto", size=20, weight="bold")
        )
        self.titulo.pack()
        self.artista = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(family="Roboto", size=16))
        self.artista.pack()
        self.album = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(family="Roboto", size=14))
        self.album.pack()
        self.barra_progreso = ctk.CTkProgressBar(
            self.frame_izquierdo, width=300, height=5, corner_radius=2, fg_color="#333333", progress_color="#1DB954"
        )
        self.barra_progreso.pack(pady=15)
        self.frame_tiempo = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_tiempo.pack(fill=tk.X, pady=2)
        self.tiempo_actual = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=("Roboto", 10))
        self.tiempo_actual.pack(side=tk.LEFT, padx=40)
        self.tiempo_total = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=("Roboto", 10))
        self.tiempo_total.pack(side=tk.RIGHT, padx=40)
        self.frame_controles = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_controles.pack(pady=15)
        botones_control = [
            ("⏮", "anterior", 35),
            ("⏪", "retroceder", 35),
            ("▶", "reproducir_pausar", 45),
            ("⏩", "adelantar", 35),
            ("⏭", "siguiente", 35),
        ]
        for texto, nombre, tamaño in botones_control:
            btn = ctk.CTkButton(
                self.frame_controles,
                text=texto,
                width=tamaño,
                height=tamaño,
                font=("Roboto", 16),
                fg_color="#282828",
                hover_color="#383838",
                corner_radius=tamaño // 2,
            )
            setattr(self, f"boton_{nombre}", btn)
            btn.pack(side=tk.LEFT, padx=3)
        self.boton_reproducir_pausar.configure(fg_color="#1DB954", hover_color="#1ed760", font=("Roboto", 18))
        self.frame_controles_adicionales = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_controles_adicionales.pack(pady=15)
        botones_adicionales = [
            ("🔀", "aleatorio"),
            ("🔁", "repetir"),
            ("⭐", "favorito"),
            ("❤", "me_gusta"),
            ("👁", "mostrar_cola"),
            ("➕", "agregar_cola"),
        ]
        for texto, nombre in botones_adicionales:
            btn = ctk.CTkButton(
                self.frame_controles_adicionales,
                text=texto,
                width=30,
                height=30,
                font=("Roboto", 14),
                corner_radius=15,
                fg_color="#282828",
                hover_color="#383838",
            )
            setattr(self, f"boton_{nombre}", btn)
            btn.pack(side=tk.LEFT, padx=3)
        self.frame_volumen = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_volumen.pack(pady=15, fill=tk.X, padx=35)
        self.boton_mute = ctk.CTkButton(
            self.frame_volumen,
            text="🔊",
            width=30,
            height=30,
            font=("Roboto", 14),
            fg_color="#282828",
            hover_color="#383838",
            corner_radius=15,
        )
        self.boton_mute.pack(side=tk.LEFT, padx=5)
        self.volumen_slider = ctk.CTkSlider(
            self.frame_volumen,
            from_=0,
            to=100,
            height=12,
            fg_color="#333333",
            progress_color="#1DB954",
            button_color="#1DB954",
            button_hover_color="#1ed760",
        )
        self.volumen_slider.set(100)
        self.volumen_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _crear_widgets_derechos(self):
        self.frame_busqueda = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_busqueda.pack(fill=tk.X, pady=12, padx=15)
        self.entrada_busqueda = ctk.CTkEntry(
            self.frame_busqueda,
            placeholder_text="Buscar...",
            height=35,
            font=("Roboto", 12),
            fg_color="#282828",
            border_color="#1DB954",
            border_width=2,
        )
        self.entrada_busqueda.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar_cancion)
        self.frame_ordenar = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_ordenar.pack(fill=tk.X, pady=6, padx=15)
        self.label_ordenar = ctk.CTkLabel(self.frame_ordenar, text="Ordenar por:", font=("Roboto", 12))
        self.label_ordenar.pack(side=tk.LEFT, padx=(0, 8))
        self.combobox_ordenar = ctk.CTkComboBox(
            self.frame_ordenar,
            values=["Título", "Artista", "Álbum", "Año"],
            command=self._ordenar_canciones,
            height=30,
            font=("Roboto", 12),
            fg_color="#282828",
            button_color="#1DB954",
            border_color="#1DB954",
            button_hover_color="#1ed760",
            dropdown_fg_color="#282828",
        )
        self.combobox_ordenar.pack(side=tk.LEFT)
        self.notebook = ctk.CTkTabview(
            self.frame_derecho,
            height=450,
            fg_color="#282828",
            segmented_button_fg_color="#1E1E1E",
            segmented_button_selected_color="#1DB954",
            segmented_button_unselected_color="#282828",
        )
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        for tab in ["Todas", "Me gusta", "Favoritos", "Listas personalizadas"]:
            self.notebook.add(tab)
        self._crear_lista_canciones(self.notebook.tab("Todas"), "lista_canciones")
        self._crear_lista_canciones(self.notebook.tab("Me gusta"), "lista_me_gusta")
        self._crear_lista_canciones(self.notebook.tab("Favoritos"), "lista_favoritos")
        self._crear_listas_personalizadas(self.notebook.tab("Listas personalizadas"))
        self.frame_botones_inferiores = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_botones_inferiores.pack(fill=tk.X, pady=12, padx=15)
        botones_config = [
            ("Seleccionar carpeta", "seleccionar_carpeta"),
            ("Importar lista", "importar"),
            ("Exportar lista", "exportar"),
        ]
        for texto, nombre in botones_config:
            btn = ctk.CTkButton(
                self.frame_botones_inferiores,
                text=texto,
                height=35,
                font=("Roboto", 12),
                fg_color="#282828",
                hover_color="#383838",
                corner_radius=6,
            )
            setattr(self, f"boton_{nombre}", btn)
            btn.pack(side=tk.LEFT, padx=4)
        self.boton_importar.configure(command=self.controlador.importar_lista)
        self.boton_exportar.configure(command=self.controlador.exportar_lista)

    def _crear_lista_canciones(self, parent, nombre):
        lista = ctk.CTkScrollableFrame(parent, height=300, fg_color="#1E1E1E", corner_radius=6)
        lista.pack(fill=tk.BOTH, expand=True)
        setattr(self, nombre, lista)

    def _crear_listas_personalizadas(self, parent):
        self.frame_listas_personalizadas = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame_listas_personalizadas.pack(fill=tk.BOTH, expand=True)
        self.lista_personalizadas = CTkScrollableFrame(
            self.frame_listas_personalizadas, height=250, fg_color="#1E1E1E", corner_radius=6
        )
        self.lista_personalizadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_botones_listas = ctk.CTkFrame(self.frame_listas_personalizadas, fg_color="transparent")
        self.frame_botones_listas.pack(side=tk.RIGHT, fill=tk.Y, padx=8)
        for texto in ["Nueva lista", "Eliminar lista", "Modificar lista"]:
            btn = ctk.CTkButton(
                self.frame_botones_listas,
                text=texto,
                width=100,
                height=30,
                font=("Roboto", 12),
                fg_color="#282828",
                hover_color="#383838",
                corner_radius=6,
            )
            setattr(self, f"boton_{texto.lower().replace(' ', '_')}", btn)
            btn.pack(pady=4)
        self.botones_listas_personalizadas = []

    def actualizar_lista_canciones(self, canciones, lista_nombre="lista_canciones"):
        lista = getattr(self, lista_nombre)
        for widget in lista.winfo_children():
            widget.destroy()
        for cancion in canciones:
            btn = ctk.CTkButton(
                lista,
                text=f"{cancion.titulo} - {cancion.artista}",
                anchor="w",
                command=lambda c=cancion: self.controlador.reproducir_cancion(c),
                fg_color="#282828",
                hover_color="#383838",
                height=35,
                corner_radius=6,
                font=("Roboto", 12),
            )
            btn.pack(fill=tk.X, pady=2, padx=4)

    def actualizar_cancion(self, cancion):
        self.titulo.configure(text=cancion.titulo)
        self.artista.configure(text=cancion.artista)
        self.album.configure(text=cancion.album)
        duracion = f"{int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}"
        self.tiempo_total.configure(text=duracion)
        if cancion.caratula:
            img = CTkImage(light_image=cancion.caratula, size=(250, 250))
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

    def _crear_dialogo_personalizado(self, titulo, mensaje):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(titulo)
        dialog.geometry("400x250")
        dialog.grab_set()
        frame = ctk.CTkFrame(dialog, fg_color="#1E1E1E")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        ctk.CTkLabel(frame, text=mensaje, font=("Roboto", 14)).pack(pady=15)
        return dialog, frame

    def mostrar_dialogo_formato(self):
        dialog, frame = self._crear_dialogo_personalizado("Exportar Lista", "Seleccione formato de exportación:")
        formato = tk.StringVar(value="txt")
        for valor in ["txt", "json"]:
            ctk.CTkRadioButton(
                frame,
                text=valor.upper(),
                variable=formato,
                value=valor,
                font=("Roboto", 13),
                fg_color="#1DB954",
                border_color="#1DB954",
            ).pack(pady=5)
        result = tk.StringVar()

        def on_accept():
            result.set(formato.get())
            dialog.destroy()

        def on_cancel():
            result.set("")
            dialog.destroy()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        for texto, comando in [("Aceptar", on_accept), ("Cancelar", on_cancel)]:
            ctk.CTkButton(
                btn_frame,
                text=texto,
                command=comando,
                width=100,
                height=35,
                font=("Roboto", 13),
                fg_color="#282828",
                hover_color="#383838",
            ).pack(side=tk.LEFT, padx=5)
        dialog.wait_window()
        return result.get() if result.get() else None

    def _buscar_cancion(self, event):
        self.controlador.buscar_cancion(self.entrada_busqueda.get())

    def _ordenar_canciones(self, criterio):
        self.controlador.ordenar_canciones(criterio.lower())

    def mostrar_cola(self, cola):
        dialog, frame = self._crear_dialogo_personalizado("Cola de Reproducción", "Canciones en cola:")
        lista_frame = ctk.CTkScrollableFrame(frame, height=200, fg_color="#282828", corner_radius=8)
        lista_frame.pack(fill="both", expand=True, pady=10)
        if not cola:
            ctk.CTkLabel(lista_frame, text="La cola está vacía", font=("Roboto", 13)).pack(pady=10)
        else:
            for cancion in cola:
                ctk.CTkLabel(
                    lista_frame, text=f"{cancion.titulo} - {cancion.artista}", font=("Roboto", 13), anchor="w"
                ).pack(pady=2, padx=10, anchor="w")
        ctk.CTkButton(
            dialog,
            text="Cerrar",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Roboto", 13),
            fg_color="#282828",
            hover_color="#383838",
        ).pack(pady=10)

    def _configurar_listas_personalizadas(self):
        self.lista_personalizadas.bind("<Double-1>", self.controlador.seleccionar_lista_personalizada)
