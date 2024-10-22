from customtkinter import CTkScrollableFrame, CTkButton, CTkImage
from PIL import Image, ImageColor
from tkinter import messagebox
import customtkinter as ctk
import tkinter as tk
import colorsys


class VistaReproductor:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self._inicializar_ventana()
        self._crear_widgets()
        self._configurar_listas_personalizadas()

    def _inicializar_ventana(self):
        self.root.title("Reproductor de Música")
        self.root.geometry("1200x720")
        self.root.minsize(1200, 720)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.color_principal = "#2EBD59"
        self.color_secundario = "#222222"

    def _crear_widgets(self):
        self._crear_frame_principal()
        self._crear_widgets_izquierdos()
        self._crear_widgets_derechos()

    def _crear_frame_principal(self):
        self.frame_principal = ctk.CTkFrame(self.root, fg_color="#0A0A0A")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_principal.grid_columnconfigure(0, weight=2)
        self.frame_principal.grid_columnconfigure(1, weight=1)
        self.frame_izquierdo = ctk.CTkFrame(self.frame_principal, width=700, corner_radius=20, fg_color="#111111")
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        self.frame_izquierdo.pack_propagate(False)
        self.frame_derecho = ctk.CTkFrame(self.frame_principal, width=350, corner_radius=20, fg_color="#111111")
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        self.frame_derecho.pack_propagate(False)

    def _crear_widgets_izquierdos(self):
        self._crear_caratula()
        self._crear_info_cancion()
        self._crear_controles_reproduccion()
        self._crear_controles_volumen()
        self._crear_frame_listas()

    def _crear_caratula(self):
        self.caratula = ctk.CTkLabel(self.frame_izquierdo, text="", width=250, height=250)
        self.caratula.pack(pady=15)
        self.caratula.pack_propagate(False)

    def _crear_info_cancion(self):
        self.titulo = ctk.CTkLabel(
            self.frame_izquierdo, text="", font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        )
        self.titulo.pack()
        self.artista = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(family="Inter", size=16))
        self.artista.pack()
        self.album = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(family="Inter", size=14))
        self.album.pack()

    def _crear_controles_reproduccion(self):
        self.barra_progreso = ctk.CTkProgressBar(
            self.frame_izquierdo, width=575, height=4, corner_radius=2, fg_color="#222222", progress_color="#2EBD59"
        )
        self.barra_progreso.pack(pady=15)
        self._crear_frame_tiempo()
        self._crear_botones_control()

    def _crear_frame_tiempo(self):
        self.frame_tiempo = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_tiempo.pack(fill=tk.X, pady=2)
        self.tiempo_actual = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=("Inter", 10))
        self.tiempo_actual.pack(side=tk.LEFT, padx=15)
        self.tiempo_total = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=("Inter", 10))
        self.tiempo_total.pack(side=tk.RIGHT, padx=15)

    def _crear_botones_control(self):
        self.frame_controles = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent", width=800, height=50)
        self.frame_controles.pack(pady=12)
        self.frame_controles.pack_propagate(False)
        botones_control = [
            ("🔁", "repetir", 36),
            ("🔀", "aleatorio", 36),
            ("⏮", "anterior", 36),
            ("⏪", "retroceder", 36),
            ("▶", "reproducir_pausar", 40),
            ("⏩", "adelantar", 36),
            ("⏭", "siguiente", 36),
            ("⭐", "favorito", 36),
            ("❤", "me_gusta", 36),
            ("👁", "mostrar_cola", 36),
            ("➕", "agregar_cola", 36),
        ]
        for texto, nombre, tamaño in botones_control:
            btn = ctk.CTkButton(
                self.frame_controles,
                text=texto,
                width=tamaño,
                height=tamaño,
                font=("Inter", 18),
                fg_color="#333333",
                hover_color="#444444",
                corner_radius=tamaño // 1.5,
            )
            setattr(self, f"boton_{nombre}", btn)
            btn.pack(side=tk.LEFT, padx=3)
        self.boton_reproducir_pausar.configure(fg_color="#1DB954", hover_color="#1ED760", font=("Inter", 18))

    def _crear_controles_volumen(self):
        self.frame_volumen = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_volumen.pack(pady=12, fill=tk.X, padx=40)
        self.boton_mute = ctk.CTkButton(
            self.frame_volumen,
            text="🔊",
            width=36,
            height=36,
            font=("Inter", 12),
            fg_color="#222222",
            hover_color="#333333",
            corner_radius=14,
        )
        self.boton_mute.pack(side=tk.LEFT, padx=5)
        self.volumen_slider = ctk.CTkSlider(
            self.frame_volumen,
            from_=0,
            to=100,
            height=10,
            fg_color="#222222",
            progress_color="#2EBD59",
            button_color="#2EBD59",
            button_hover_color="#1ed760",
        )
        self.volumen_slider.set(100)
        self.volumen_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _crear_frame_listas(self):
        self.frame_listas = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_listas.pack(pady=12)

    def _crear_widgets_derechos(self):
        self._crear_busqueda_ordenar()
        self._crear_notebook()
        self._crear_botones_inferiores()
        self._configurar_grid_derecho()

    def _crear_busqueda_ordenar(self):
        self.frame_busqueda_ordenar = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_busqueda_ordenar.pack(fill=tk.X, pady=12, padx=15)
        self.entrada_busqueda = ctk.CTkEntry(
            self.frame_busqueda_ordenar,
            placeholder_text="Buscar...",
            height=36,
            font=("Inter", 12),
            fg_color="#333333",
            border_color="#1DB954",
            border_width=1,
        )
        self.entrada_busqueda.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.entrada_busqueda.bind("<KeyRelease>", self._buscar_cancion)
        self.combobox_ordenar = ctk.CTkComboBox(
            self.frame_busqueda_ordenar,
            values=["Título", "Artista", "Álbum", "Año"],
            command=self._ordenar_canciones,
            height=36,
            font=("Inter", 12),
            fg_color="#333333",
            button_color="#1DB954",
            border_color="#1DB954",
            button_hover_color="#1ED760",
            dropdown_fg_color="#333333",
        )
        self.combobox_ordenar.pack(side=tk.RIGHT)

    def _crear_notebook(self):
        self.notebook = ctk.CTkTabview(
            self.frame_derecho,
            height=400,
            fg_color="#222222",
            segmented_button_fg_color="#111111",
            segmented_button_selected_color="#2EBD59",
            segmented_button_unselected_color="#222222",
        )
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        for tab in ["Todas", "Me gusta", "Favoritos", "Listas personalizadas"]:
            self.notebook.add(tab)
        self._crear_lista_canciones(self.notebook.tab("Todas"), "lista_canciones")
        self._crear_lista_canciones(self.notebook.tab("Me gusta"), "lista_me_gusta")
        self._crear_lista_canciones(self.notebook.tab("Favoritos"), "lista_favoritos")
        self._crear_listas_personalizadas(self.notebook.tab("Listas personalizadas"))

    def _crear_botones_inferiores(self):
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
                height=36,
                font=("Inter", 12),
                fg_color="#333333",
                hover_color="#444444",
                corner_radius=8,
            )
            setattr(self, f"boton_{nombre}", btn)
        self.boton_seleccionar_carpeta.pack(side=tk.TOP, pady=(0, 5), fill=tk.X)
        self.boton_importar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        self.boton_exportar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))
        self.boton_importar.configure(command=self.controlador.importar_lista)
        self.boton_exportar.configure(command=self.controlador.exportar_lista)

    def _configurar_grid_derecho(self):
        self.frame_derecho.grid_rowconfigure(0, weight=0)
        self.frame_derecho.grid_rowconfigure(1, weight=1)
        self.frame_derecho.grid_rowconfigure(2, weight=0)

    def _crear_lista_canciones(self, parent, nombre):
        lista = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=8, width=300, height=400)
        lista.pack(fill=tk.BOTH, expand=True)
        lista.pack_propagate(False)
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
        lista.configure(width=300, height=400)
        lista.pack_propagate(False)
        for widget in lista.winfo_children():
            widget.destroy()
        canvas = tk.Canvas(lista, bg="#1E1E1E", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(lista, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#1E1E1E")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        for cancion in canciones:
            try:
                btn = ctk.CTkButton(
                    scrollable_frame,
                    text=f"{cancion.titulo} - {cancion.artista}",
                    anchor="w",
                    command=lambda c=cancion: self.controlador.reproducir_cancion(c),
                    fg_color="#333333",
                    hover_color="#444444",
                    height=40,
                    corner_radius=8,
                    font=("Roboto", 12),
                )
                btn.pack(fill=tk.X, pady=2, padx=4)
            except Exception as e:
                print(f"Error al crear botón para {cancion.titulo}: {str(e)}")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def actualizar_cancion(self, cancion):
        self.titulo.configure(text=cancion.titulo)
        self.artista.configure(text=cancion.artista)
        self.album.configure(text=cancion.album)
        duracion = f"{int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}"
        self.tiempo_total.configure(text=duracion)
        if cancion.caratula:
            img = CTkImage(light_image=cancion.caratula, size=(250, 250))
            self.caratula.configure(image=img)
            self.color_principal = self.obtener_color_dominante(cancion.caratula)
            self.color_secundario = self.ajustar_brillo(self.color_principal, 0.2)
            self.actualizar_colores()
        else:
            self.caratula.configure(image=None, text="Sin carátula")
            self.color_principal = "#2EBD59"
            self.color_secundario = "#222222"
            self.actualizar_colores()
        self.barra_progreso.set(0)
        self.tiempo_actual.configure(text="0:00")
        self.actualizar_boton_me_gusta(cancion.ruta in self.controlador.me_gusta)
        self.actualizar_boton_favorito(cancion.ruta in self.controlador.favoritos)

    def obtener_color_dominante(self, imagen):
        imagen = imagen.copy()
        imagen = imagen.resize((50, 50))
        resultado = imagen.convert("P", palette=Image.ADAPTIVE, colors=1)
        paleta = resultado.getpalette()
        color_dominante = tuple(paleta[:3])
        return f"#{color_dominante[0]:02x}{color_dominante[1]:02x}{color_dominante[2]:02x}"

    def ajustar_brillo(self, color, factor):
        rgb = ImageColor.getrgb(color)
        hsv = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], max(min(hsv[2] * factor, 1.0), 0.0))
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

    def actualizar_colores(self):
        self.barra_progreso.configure(progress_color=self.color_principal)
        self.volumen_slider.configure(progress_color=self.color_principal, button_color=self.color_principal)
        botones_principales = [
            self.boton_reproducir_pausar,
            self.boton_aleatorio,
            self.boton_siguiente,
            self.boton_anterior,
            self.boton_adelantar,
            self.boton_retroceder,
            self.boton_repetir,
            self.boton_mostrar_cola,
            self.boton_agregar_cola,
            self.boton_mute,
        ]
        for widget in botones_principales:
            widget.configure(fg_color=self.color_principal, hover_color=self.ajustar_brillo(self.color_principal, 1.2))
        for widget in [self.frame_izquierdo, self.frame_derecho]:
            widget.configure(fg_color=self.color_secundario)
        botones_especiales = [
            self.boton_reproducir_pausar,
            self.boton_aleatorio,
            self.boton_siguiente,
            self.boton_anterior,
            self.boton_adelantar,
            self.boton_retroceder,
            self.boton_repetir,
            self.boton_me_gusta,
            self.boton_favorito,
            self.boton_mostrar_cola,
            self.boton_agregar_cola,
        ]
        for widget in self.frame_controles.winfo_children():
            if widget not in botones_especiales:
                widget.configure(
                    fg_color=self.color_secundario, hover_color=self.ajustar_brillo(self.color_secundario, 1.2)
                )
        self.boton_me_gusta.configure(fg_color="#FF0000", hover_color="#FF3333")
        self.boton_favorito.configure(fg_color="#eed010", hover_color="#FFFF33")
        self.entrada_busqueda.configure(border_color=self.color_principal)
        self.combobox_ordenar.configure(
            button_color=self.color_principal,
            border_color=self.color_principal,
            button_hover_color=self.ajustar_brillo(self.color_principal, 1.2),
        )
        self.notebook.configure(segmented_button_selected_color=self.color_principal)
        for lista in [self.lista_canciones, self.lista_me_gusta, self.lista_favoritos, self.lista_personalizadas]:
            lista.configure(fg_color=self.ajustar_brillo(self.color_secundario, 0.8))
        self.actualizar_lista_canciones(self.controlador.modelo.canciones)

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
        self.boton_me_gusta.configure(fg_color="#ff0000" if activo else self.color_secundario)

    def actualizar_boton_favorito(self, activo):
        self.boton_favorito.configure(fg_color="#eed010" if activo else self.color_secundario)

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
