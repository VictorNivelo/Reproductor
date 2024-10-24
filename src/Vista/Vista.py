from customtkinter import CTkScrollableFrame, CTkButton, CTkImage
from Vista.Tooltip import ToolTip
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
import tkinter as tk
import colorsys
import random
import pygame


class VistaReproductor:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self._inicializar_ventana()
        self._crear_widgets()
        self._configurar_listas_personalizadas()
        self.iniciar_visualizador()

    def _inicializar_ventana(self):
        self.root.title("Reproductor de Música")
        self.root.geometry("1200x720")
        self.root.minsize(1200, 720)
        self.tema_actual = "oscuro"
        ctk.set_appearance_mode(self.tema_actual)
        ctk.set_default_color_theme("blue")
        self.color_principal = "#2EBD59"
        self.color_secundario = "#222222"
        self.fuente_principal = ("SF Pro Display", 14)
        self.fuente_titulos = ("SF Pro Display", 20, "bold")
        self.cargar_iconos()
        self.reproduciendo = False
        self.pausado = True

    def cargar_iconos(self):
        self.iconos = {
            "adelantar": "⏩",
            "retroceder": "⏪",
            "play": "▶️",
            "pausa": "⏸️",
            "siguiente": "⏭️",
            "anterior": "⏮️",
            "aleatorio": "🔀",
            "repetir": "🔁",
            "repetir_una": "🔂",
            "repetir_todo": "↻",
            "volumen_alto": "🔊",
            "volumen_medio": "🔉",
            "volumen_bajo": "🔈",
            "silencio": "🔇",
            "me_gusta": "❤️",
            "favorito": "⭐",
            "agregar": "➕",
            "cola": "📋",
            "claro": "☀️",
            "oscuro": "🌙",
        }

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
        self._crear_controles_superiores()
        self._crear_caratula()
        self._crear_info_cancion()
        self._crear_visualizador()
        self._crear_controles_reproduccion()
        self._crear_controles_volumen()
        self._crear_frame_listas()

    def _crear_controles_superiores(self):
        self.frame_superior = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_superior.pack(fill=tk.X, pady=(10, 0), padx=10)
        self.boton_tema = ctk.CTkButton(
            self.frame_superior,
            text=self.iconos["claro"] if self.tema_actual == "oscuro" else self.iconos["oscuro"],
            width=35,
            height=35,
            font=self.fuente_principal,
            fg_color="#333333",
            hover_color="#444444",
            corner_radius=12,
            command=self.cambiar_tema,
            text_color=self.obtener_color_texto("333333"),
        )
        self.boton_tema.pack(side=tk.RIGHT)
        ToolTip(self.boton_tema, "Cambiar tema")

    def cambiar_tema(self):
        self.tema_actual = "claro" if self.tema_actual == "oscuro" else "oscuro"
        self.actualizar_tema(self.tema_actual)
        self.boton_tema.configure(text=self.iconos["claro"] if self.tema_actual == "oscuro" else self.iconos["oscuro"])

    def _crear_visualizador(self):
        self.frame_visualizador = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_visualizador.pack(pady=10)
        self.canvas_visualizador = tk.Canvas(self.frame_visualizador, width=550, height=70, highlightthickness=0)
        self.canvas_visualizador.pack(pady=5)
        self.canvas_visualizador.configure(bg=self.color_secundario)
        self.barras_visualizador = []
        self.num_barras = 100
        self.ancho_barra = 4
        self.espacio_entre_barras = 3
        ancho_total = (self.ancho_barra + self.espacio_entre_barras) * self.num_barras
        inicio_x = (550 - ancho_total) / 2
        for i in range(self.num_barras):
            x = inicio_x + i * (self.ancho_barra + self.espacio_entre_barras)
            barra = self.canvas_visualizador.create_rectangle(
                x, 80, x + self.ancho_barra, 80, fill=self.color_principal, width=0
            )
            self.barras_visualizador.append(barra)
        self.suavizado_barras = [0] * self.num_barras
        self.reproduciendo = False
        self.pausado = True
        self.visualizador_activo = False

    def resetear_visualizador(self):
        for barra in self.barras_visualizador:
            x0, _, x1, _ = self.canvas_visualizador.coords(barra)
            self.canvas_visualizador.coords(barra, x0, 80, x1, 80)
        self.suavizado_barras = [0] * self.num_barras

    def iniciar_visualizador(self):
        if self.reproduciendo and not self.pausado:
            self.visualizador_activo = True
            self.actualizar_visualizador()

    def detener_visualizador(self):
        self.visualizador_activo = False
        self.resetear_visualizador()

    def actualizar_visualizador(self, datos_audio=None):
        if not self.reproduciendo or self.pausado:
            self.resetear_visualizador()
            return
        if datos_audio is None:
            datos_audio = [random.random() * 0.9 for _ in range(self.num_barras)]
        for i, valor in enumerate(datos_audio[: self.num_barras]):
            objetivo = valor * 80
            self.suavizado_barras[i] = self.suavizado_barras[i] * 0.7 + objetivo * 0.3
            altura = max(1, min(80, self.suavizado_barras[i]))
            x0, _, x1, _ = self.canvas_visualizador.coords(self.barras_visualizador[i])
            self.canvas_visualizador.coords(self.barras_visualizador[i], x0, 80 - altura, x1, 80)
            self.canvas_visualizador.itemconfig(self.barras_visualizador[i], fill=self.color_principal)
        if self.visualizador_activo:
            self.root.after(50, self.actualizar_visualizador)

    def generar_color_espectro(self, hue, valor):
        sat = 0.8
        val = 0.8 + valor * 0.2
        rgb = colorsys.hsv_to_rgb(hue, sat, val)
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

    def animar_visualizador(self, datos_audio=None):
        if not self.reproduciendo or self.pausado:
            self.detener_visualizador()
            return
        if datos_audio is None:
            datos_audio = [random.random() * 0.8 for _ in range(self.num_barras)]
        datos_normalizados = []
        max_valor = max(abs(valor) for valor in datos_audio) if datos_audio else 1
        if max_valor > 0:
            factor_escala = 1.0 / max_valor
            chunk_size = max(1, len(datos_audio) // self.num_barras)
            for i in range(self.num_barras):
                inicio = i * chunk_size
                fin = min(inicio + chunk_size, len(datos_audio))
                chunk = datos_audio[inicio:fin] if datos_audio else [random.random() * 0.8]
                if chunk:
                    valor_promedio = sum(abs(x) for x in chunk) / len(chunk)
                    valor_normalizado = min(1.0, valor_promedio * factor_escala)
                    datos_normalizados.append(valor_normalizado)
                else:
                    datos_normalizados.append(random.random() * 0.8)
        else:
            datos_normalizados = [random.random() * 0.8 for _ in range(self.num_barras)]
        self.actualizar_visualizador(datos_normalizados)

    def animar_boton(self, boton):
        color_original = boton.cget("fg_color")
        boton.configure(fg_color=self.color_principal)
        self.root.after(100, lambda: boton.configure(fg_color=color_original))

    def actualizar_tema(self, modo):
        ctk.set_appearance_mode(modo)
        colores = {
            "oscuro": {"principal": "#2EBD59", "secundario": "#222222", "fondo": "#111111", "texto": "#FFFFFF"},
            "claro": {"principal": "#1DB954", "secundario": "#EEEEEE", "fondo": "#FFFFFF", "texto": "#000000"},
        }
        self.color_principal = colores[modo]["principal"]
        self.color_secundario = colores[modo]["secundario"]
        self.actualizar_colores()
        self.canvas_visualizador.configure(bg=self.color_secundario)
        for barra in self.barras_visualizador:
            self.canvas_visualizador.itemconfig(barra, fill=self.color_principal)

    def actualizar_estado_reproduccion(self, reproduciendo, pausado):
        self.reproduciendo = reproduciendo
        self.pausado = pausado
        if reproduciendo and not pausado:
            self.iniciar_visualizador()
        else:
            self.detener_visualizador()
        self.actualizar_boton_reproducir_pausar(reproduciendo, pausado)

    def _crear_widgets(self):
        self._crear_frame_principal()
        self._crear_widgets_izquierdos()
        self._crear_widgets_derechos()

    def _crear_caratula(self):
        self.caratula = ctk.CTkLabel(self.frame_izquierdo, text="", width=250, height=250)
        self.caratula.pack(pady=15)
        self.caratula.pack_propagate(False)

    def _crear_info_cancion(self):
        self.frame_info = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_info.pack(fill=tk.X, padx=20)
        self.titulo = ctk.CTkLabel(self.frame_info, text="", font=self.fuente_titulos)
        self.titulo.pack()
        self.artista = ctk.CTkLabel(self.frame_info, text="", font=self.fuente_principal)
        self.artista.pack()
        self.album = ctk.CTkLabel(self.frame_info, text="", font=self.fuente_principal)
        self.album.pack()

    def _crear_controles_reproduccion(self):
        self.frame_progreso = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_progreso.pack(fill=tk.X, padx=15)
        self.barra_progreso = ctk.CTkProgressBar(
            self.frame_progreso, height=4, corner_radius=2, fg_color="#222222", progress_color="#2EBD59"
        )
        self.barra_progreso.pack(fill=tk.X, pady=8)
        self._crear_frame_tiempo()
        self._crear_botones_control()

    def _crear_frame_tiempo(self):
        self.frame_tiempo = ctk.CTkFrame(self.frame_progreso, fg_color="transparent")
        self.frame_tiempo.pack(fill=tk.X)
        self.tiempo_actual = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=self.fuente_principal)
        self.tiempo_actual.pack(side=tk.LEFT)
        self.tiempo_total = ctk.CTkLabel(self.frame_tiempo, text="0:00", font=self.fuente_principal)
        self.tiempo_total.pack(side=tk.RIGHT)

    def _crear_botones_control(self):
        self.frame_controles = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_controles.pack(pady=5)
        botones_control = [
            (self.iconos["repetir"], "repetir", 35, "Repetir"),
            (self.iconos["aleatorio"], "aleatorio", 35, "Aleatorio"),
            (self.iconos["anterior"], "anterior", 35, "Anterior"),
            (self.iconos["retroceder"], "retroceder", 35, "Retroceder"),
            (self.iconos["play"], "reproducir_pausar", 35, "Reproducir/Pausar"),
            (self.iconos["adelantar"], "adelantar", 35, "Adelantar"),
            (self.iconos["siguiente"], "siguiente", 35, "Siguiente"),
            (self.iconos["me_gusta"], "me_gusta", 35, "Me gusta"),
            (self.iconos["favorito"], "favorito", 35, "Favorito"),
            (self.iconos["cola"], "mostrar_cola", 35, "Ver cola"),
            (self.iconos["agregar"], "agregar_cola", 35, "Agregar a cola"),
        ]
        self.tooltips = {}
        for icono, nombre, tamaño, tooltip in botones_control:
            btn = ctk.CTkButton(
                self.frame_controles,
                text=icono,
                width=tamaño,
                height=tamaño,
                font=("Roboto", 12),
                fg_color="#333333",
                hover_color="#444444",
                corner_radius=12,
                command=lambda n=nombre: self.animar_boton(getattr(self, f"boton_{n}")),
            )
            setattr(self, f"boton_{nombre}", btn)
            btn.pack(side=tk.LEFT, padx=2)
            tooltip_obj = ToolTip(btn, tooltip, self.color_secundario, "#FFFFFF")
            self.tooltips[nombre] = tooltip_obj

    def actualizar_tooltips(self):
        for tooltip in self.tooltips.values():
            tooltip.actualizar_colores(self.ajustar_brillo(self.color_secundario, 1.2), "#FFFFFF")

    def _crear_controles_volumen(self):
        self.frame_volumen = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_volumen.pack(pady=12, fill=tk.X, padx=40)
        self.boton_mute = ctk.CTkButton(
            self.frame_volumen,
            text=self.iconos["volumen_alto"],
            width=35,
            height=35,
            font=("Roboto", 12),
            fg_color="#222222",
            hover_color="#333333",
            corner_radius=12,
            command=self.alternar_mute,
        )
        self.boton_mute.pack(side=tk.LEFT, padx=5)
        ToolTip(self.boton_mute, "Silenciar")
        self.volumen_slider = ctk.CTkSlider(
            self.frame_volumen,
            from_=0,
            to=100,
            height=10,
            fg_color="#222222",
            progress_color="#2EBD59",
            button_color="#2EBD59",
            button_hover_color="#1ed760",
            command=self.actualizar_volumen_desde_slider,
        )
        self.volumen_slider.set(100)
        self.volumen_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.label_volumen = ctk.CTkLabel(self.frame_volumen, text="100%", font=("Roboto", 12))
        self.label_volumen.pack(side=tk.RIGHT)

    def alternar_mute(self):
        self.mute = not self.mute
        if self.mute:
            pygame.mixer.music.set_volume(0)
            self.boton_mute.configure(text=self.iconos["silencio"])
            volumen_actual = self.volumen_slider.get()
            self.volumen = volumen_actual / 100
        else:
            pygame.mixer.music.set_volume(self.volumen)
            if self.volumen == 0:
                self.boton_mute.configure(text=self.iconos["silencio"])
            elif self.volumen < 0.33:
                self.boton_mute.configure(text=self.iconos["volumen_bajo"])
            elif self.volumen < 0.66:
                self.boton_mute.configure(text=self.iconos["volumen_medio"])
            else:
                self.boton_mute.configure(text=self.iconos["volumen_alto"])
        self.guardar_configuracion()

    def actualizar_label_volumen(self, valor):
        porcentaje = int(valor)
        self.label_volumen.configure(text=f"{porcentaje}%")
        self.actualizar_icono_volumen(porcentaje / 100)

    def actualizar_volumen_desde_slider(self, valor):
        porcentaje = int(valor)
        volumen = porcentaje / 100
        self.volumen = volumen
        if not self.mute:
            pygame.mixer.music.set_volume(volumen)
        self.actualizar_porcentaje_volumen(porcentaje)
        if porcentaje == 0:
            self.boton_mute.configure(text=self.iconos["silencio"])
        elif porcentaje < 33:
            self.boton_mute.configure(text=self.iconos["volumen_bajo"])
        elif porcentaje < 66:
            self.boton_mute.configure(text=self.iconos["volumen_medio"])
        else:
            self.boton_mute.configure(text=self.iconos["volumen_alto"])
        self.controlador.cambiar_volumen(valor)

    def cambiar_volumen(self, valor):
        volumen = float(valor) / 100
        self.volumen = volumen
        if not self.mute:
            pygame.mixer.music.set_volume(volumen)
        self.guardar_configuracion()

    def actualizar_porcentaje_volumen(self, valor):
        porcentaje = int(valor)
        self.label_volumen.configure(text=f"{porcentaje}%")

    def actualizar_volumen(self, valor):
        porcentaje = int(valor)
        self.volumen_slider.set(porcentaje)
        self.label_volumen.configure(text=f"{porcentaje}%")
        if porcentaje == 0:
            icono = self.iconos["silencio"]
        elif porcentaje < 33:
            icono = self.iconos["volumen_bajo"]
        elif porcentaje < 66:
            icono = self.iconos["volumen_medio"]
        else:
            icono = self.iconos["volumen_alto"]
        self.boton_mute.configure(text=icono)

    def actualizar_icono_volumen(self, volumen):
        if volumen == 0:
            self.boton_mute.configure(text=self.iconos["silencio"])
        elif volumen < 0.33:
            self.boton_mute.configure(text=self.iconos["volumen_bajo"])
        elif volumen < 0.66:
            self.boton_mute.configure(text=self.iconos["volumen_medio"])
        else:
            self.boton_mute.configure(text=self.iconos["volumen_alto"])

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
            segmented_button_selected_hover_color=self.ajustar_brillo(self.color_principal, 1.1),
            segmented_button_unselected_color="#222222",
            segmented_button_unselected_hover_color="#333333",
            text_color=self.obtener_color_texto("222222"),
        )
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        for tab in ["Canciones", "Me gusta", "Favoritos", "Listas de reproducción"]:
            self.notebook.add(tab)
        self._crear_lista_canciones(self.notebook.tab("Canciones"), "lista_canciones")
        self._crear_lista_canciones(self.notebook.tab("Me gusta"), "lista_me_gusta")
        self._crear_lista_canciones(self.notebook.tab("Favoritos"), "lista_favoritos")
        self._crear_listas_personalizadas(self.notebook.tab("Listas de reproducción"))

    def _crear_botones_inferiores(self):
        self.frame_botones_inferiores = ctk.CTkFrame(self.frame_derecho, fg_color="transparent")
        self.frame_botones_inferiores.pack(fill=tk.X, pady=8, padx=8)
        botones_config = [
            ("Seleccionar carpeta", "seleccionar_carpeta"),
            ("Importar lista", "importar"),
            ("Exportar lista", "exportar"),
        ]
        for texto, nombre in botones_config:
            btn = ctk.CTkButton(
                self.frame_botones_inferiores,
                text=texto,
                height=30,
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
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="#1E1E1E")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)

        def scroll_raton(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", scroll_raton)
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        color_hover = self.ajustar_brillo(self.color_principal, 1.1)
        for cancion in canciones:
            try:
                text_color = self.obtener_color_texto(color_botones)
                btn = ctk.CTkButton(
                    scrollable_frame,
                    text=f"{cancion.titulo} - {cancion.artista}",
                    anchor="w",
                    command=lambda c=cancion: self.controlador.reproducir_cancion(c),
                    fg_color=color_botones,
                    hover_color=color_hover,
                    height=30,
                    corner_radius=8,
                    font=("Roboto", 12),
                    text_color=text_color,
                )
                btn.pack(fill=tk.X, pady=2, padx=4)
            except Exception as e:
                print(f"Error al crear botón para {cancion.titulo}: {str(e)}")

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
        self.reproduciendo = True
        self.pausado = False

    def obtener_color_dominante(self, imagen):
        imagen = imagen.copy()
        imagen = imagen.resize((50, 50))
        resultado = imagen.convert("P", palette=Image.ADAPTIVE, colors=1)
        paleta = resultado.getpalette()
        color_dominante = tuple(paleta[:3])
        return f"#{color_dominante[0]:02x}{color_dominante[1]:02x}{color_dominante[2]:02x}"

    def obtener_color_texto(self, color_fondo):
        if color_fondo.startswith("#"):
            color_fondo = color_fondo[1:]
        rgb = tuple(int(color_fondo[i : i + 2], 16) for i in (0, 2, 4))
        brillo = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        return "#000000" if brillo > 128 else "#FFFFFF"

    def ajustar_brillo(self, color_hex, factor):
        rgb = tuple(int(color_hex[i : i + 2], 16) for i in (1, 3, 5))
        hsv = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        rgb_nuevo = colorsys.hsv_to_rgb(hsv[0], hsv[1], min(hsv[2] * factor, 1.0))
        return f"#{int(rgb_nuevo[0]*255):02x}{int(rgb_nuevo[1]*255):02x}{int(rgb_nuevo[2]*255):02x}"

    def actualizar_colores(self):
        controles_principales = [
            self.frame_principal,
            self.frame_izquierdo,
            self.frame_derecho,
            self.frame_busqueda_ordenar,
            self.lista_personalizadas,
        ]
        for control in controles_principales:
            control.configure(fg_color=self.color_secundario)
        color_frames = self.ajustar_brillo(self.color_secundario, 0.8)
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        color_hover = self.ajustar_brillo(self.color_principal, 1.1)
        self.frame_visualizador.configure(fg_color=self.ajustar_brillo(self.color_secundario, 1.2))
        self.canvas_visualizador.configure(bg=self.color_secundario)
        for barra in self.barras_visualizador:
            self.canvas_visualizador.itemconfig(barra, fill=self.color_principal)
        self.barra_progreso.configure(progress_color=self.color_principal)
        self.volumen_slider.configure(
            progress_color=self.color_principal,
            button_color=self.color_principal,
            button_hover_color=self.ajustar_brillo(self.color_principal, 1.2),
        )
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
            self.boton_tema,
            self.boton_mute,
        ]
        for boton in botones_principales:
            boton.configure(
                fg_color=self.color_principal,
                hover_color=self.ajustar_brillo(self.color_principal, 1.2),
                text_color=self.obtener_color_texto(self.color_principal[1:]),
            )
        self.boton_me_gusta.configure(
            fg_color="#FF0000", hover_color="#FF3333", text_color=self.obtener_color_texto("FF0000")
        )
        self.boton_favorito.configure(
            fg_color="#FFD700", hover_color="#FFED4A", text_color=self.obtener_color_texto("FFD700")
        )
        self.entrada_busqueda.configure(
            border_color=self.color_principal, fg_color=self.ajustar_brillo(self.color_secundario, 1.2)
        )
        self.combobox_ordenar.configure(
            button_color=self.color_principal,
            border_color=self.color_principal,
            button_hover_color=self.ajustar_brillo(self.color_principal, 1.2),
            fg_color=self.ajustar_brillo(self.color_secundario, 1.2),
            dropdown_fg_color=self.ajustar_brillo(self.color_secundario, 1.2),
            dropdown_hover_color=self.ajustar_brillo(self.color_principal, 0.9),
            text_color=self.obtener_color_texto(self.color_secundario[1:]),
        )
        self.notebook.configure(
            segmented_button_selected_color=self.color_principal,
            segmented_button_fg_color=self.ajustar_brillo(self.color_secundario, 1.1),
            fg_color=self.ajustar_brillo(self.color_secundario, 0.9),
            segmented_button_selected_hover_color=self.ajustar_brillo(self.color_principal, 1.1),
            segmented_button_unselected_color=self.ajustar_brillo(self.color_secundario, 1.1),
            segmented_button_unselected_hover_color=self.ajustar_brillo(self.color_secundario, 1.2),
            text_color=self.obtener_color_texto(self.color_secundario[1:]),
        )
        for lista in [self.lista_canciones, self.lista_me_gusta, self.lista_favoritos]:
            lista.configure(fg_color=color_frames)
            for widget in lista.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.configure(bg=color_frames)
                    for item in widget.winfo_children():
                        if isinstance(item, ctk.CTkFrame):
                            item.configure(fg_color=color_frames)
                            for boton in item.winfo_children():
                                if isinstance(boton, ctk.CTkButton):
                                    boton.configure(
                                        fg_color=color_botones,
                                        hover_color=color_hover,
                                        text_color=self.obtener_color_texto(color_botones[1:]),
                                    )
        self.lista_personalizadas.configure(fg_color=color_frames)
        for boton in self.botones_listas_personalizadas:
            boton.configure(
                fg_color=color_botones, hover_color=color_hover, text_color=self.obtener_color_texto(color_botones[1:])
            )
        botones_inferiores = [
            self.boton_seleccionar_carpeta,
            self.boton_importar,
            self.boton_exportar,
            self.boton_nueva_lista,
            self.boton_eliminar_lista,
            self.boton_modificar_lista,
        ]
        for boton in botones_inferiores:
            boton.configure(
                fg_color=color_botones, hover_color=color_hover, text_color=self.obtener_color_texto(color_botones[1:])
            )
        self.actualizar_lista_canciones(self.controlador.modelo.canciones)
        self.actualizar_tooltips()

    def actualizar_listas_personalizadas(self, listas):
        for widget in self.lista_personalizadas.winfo_children():
            widget.destroy()
        self.botones_listas_personalizadas = []
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        color_hover = self.ajustar_brillo(self.color_principal, 1.1)
        for nombre in listas.keys():
            boton = CTkButton(
                self.lista_personalizadas,
                text=nombre,
                command=lambda n=nombre: self.controlador.seleccionar_lista_personalizada(n),
                fg_color=color_botones,
                hover_color=color_hover,
                text_color=self.obtener_color_texto(color_botones[1:]),
            )
            boton.pack(fill=tk.X, pady=2)
            self.botones_listas_personalizadas.append(boton)

    def actualizar_progreso(self, valor, tiempo_actual):
        self.barra_progreso.set(valor)
        minutos, segundos = divmod(int(tiempo_actual), 60)
        self.tiempo_actual.configure(text=f"{minutos}:{segundos:02d}")
        if self.reproduciendo and not self.pausado:
            self.actualizar_visualizador()

    def actualizar_boton_reproducir_pausar(self, reproduciendo, pausado):
        self.boton_reproducir_pausar.configure(
            text=self.iconos["pausa"] if reproduciendo and not pausado else self.iconos["play"]
        )

    def actualizar_boton_aleatorio(self, activo):
        color = self.color_principal if activo else self.ajustar_brillo(self.color_secundario, 1.2)
        self.boton_aleatorio.configure(fg_color=color, text_color=self.obtener_color_texto(color[1:]))

    def actualizar_boton_repetir(self, estado):
        if isinstance(estado, bool):
            estado = "none" if not estado else "all"
        iconos_repetir = {"none": "🔁", "one": "🔂", "all": "↻"}
        color = self.color_principal if estado != "none" else self.ajustar_brillo(self.color_secundario, 1.2)
        self.boton_repetir.configure(
            text=iconos_repetir[estado], fg_color=color, text_color=self.obtener_color_texto(color[1:])
        )

    def actualizar_boton_me_gusta(self, activo):
        color = "#FF0000" if activo else self.ajustar_brillo(self.color_secundario, 1.2)
        self.boton_me_gusta.configure(fg_color=color, text_color=self.obtener_color_texto(color.replace("#", "")))

    def actualizar_boton_favorito(self, activo):
        color = "#FFD700" if activo else self.ajustar_brillo(self.color_secundario, 1.2)
        self.boton_favorito.configure(fg_color=color, text_color=self.obtener_color_texto(color.replace("#", "")))

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
        frame = ctk.CTkFrame(dialog, fg_color=self.ajustar_brillo(self.color_secundario, 0.8))
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        ctk.CTkLabel(
            frame, text=mensaje, font=("Roboto", 14), text_color=self.obtener_color_texto(self.color_secundario[1:])
        ).pack(pady=15)
        return dialog, frame

    def mostrar_dialogo_formato(self):
        dialog, frame = self._crear_dialogo_personalizado("Exportar Lista", "Seleccione formato de exportación:")
        formato = tk.StringVar(value="txt")
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        for valor in ["txt", "json"]:
            ctk.CTkRadioButton(
                frame,
                text=valor.upper(),
                variable=formato,
                value=valor,
                font=("Roboto", 13),
                fg_color=self.color_principal,
                border_color=self.color_principal,
                text_color=self.obtener_color_texto(self.color_principal[1:]),
            ).pack(pady=5)
        result = tk.StringVar()

        def aceptar():
            result.set(formato.get())
            dialog.destroy()

        def cancelar():
            result.set("")
            dialog.destroy()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        color_hover = self.ajustar_brillo(self.color_principal, 1.1)
        for texto, comando in [("Aceptar", aceptar), ("Cancelar", cancelar)]:
            ctk.CTkButton(
                btn_frame,
                text=texto,
                command=comando,
                width=100,
                height=35,
                font=("Roboto", 13),
                fg_color=color_botones,
                hover_color=color_hover,
                text_color=self.obtener_color_texto(color_botones[1:]),
            ).pack(side=tk.LEFT, padx=5)
        dialog.wait_window()
        return result.get() if result.get() else None

    def _buscar_cancion(self, event):
        self.controlador.buscar_cancion(self.entrada_busqueda.get())

    def _ordenar_canciones(self, criterio):
        self.controlador.ordenar_canciones(criterio.lower())

    def mostrar_cola(self, cola):
        dialog, frame = self._crear_dialogo_personalizado("Cola de Reproducción", "Canciones en cola:")
        color_frame = self.ajustar_brillo(self.color_secundario, 0.8)
        color_botones = self.ajustar_brillo(self.color_principal, 0.9)
        color_hover = self.ajustar_brillo(self.color_principal, 1.1)
        lista_frame = ctk.CTkScrollableFrame(frame, height=200, fg_color=color_frame, corner_radius=8)
        lista_frame.pack(fill="both", expand=True, pady=10)
        if not cola:
            ctk.CTkLabel(
                lista_frame,
                text="La cola está vacía",
                font=("Roboto", 13),
                text_color=self.obtener_color_texto(color_frame[1:]),
            ).pack(pady=10)
        else:
            for cancion in cola:
                ctk.CTkLabel(
                    lista_frame,
                    text=f"{cancion.titulo} - {cancion.artista}",
                    font=("Roboto", 13),
                    anchor="w",
                    text_color=self.obtener_color_texto(color_frame[1:]),
                ).pack(pady=2, padx=10, anchor="w")
        ctk.CTkButton(
            dialog,
            text="Cerrar",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Roboto", 13),
            fg_color=color_botones,
            hover_color=color_hover,
            text_color=self.obtener_color_texto(color_botones[1:]),
        ).pack(pady=10)

    def _configurar_listas_personalizadas(self):
        self.lista_personalizadas.bind("<Double-1>", self.controlador.seleccionar_lista_personalizada)
