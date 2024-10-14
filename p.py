import flet as ft
import os
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import pygame
import io
import time
import asyncio
import json

class Cancion:
    def __init__(self, ruta):
        self.ruta = ruta
        self.audio = MP3(ruta, ID3=ID3)
        self.titulo = str(self.audio.get("TIT2", "Título Desconocido"))
        self.artista = str(self.audio.get("TPE1", "Artista Desconocido"))
        self.album = str(self.audio.get("TALB", "Álbum Desconocido"))
        self.duracion = self.audio.info.length
        self.año = str(self.audio.get("TDRC", "Año Desconocido"))
        self.portada = self.obtener_portada()

    def obtener_portada(self):
        try:
            pict = self.audio.get("APIC:").data
            return io.BytesIO(pict)
        except:
            return None

class ReproductorMusica(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.canciones = []
        self.indice_cancion_actual = 0
        self.reproduciendo = False
        self.aleatorio = False
        self.repetir = False
        self.favoritos = set()
        self.me_gusta = set()
        self.posicion_actual = 0
        self.tiempo_inicio = 0
        pygame.mixer.init()
        self.cargar_canciones_guardadas()

    def build(self):
        self.imagen_portada = ft.Image(
            src="",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(15),
        )
        self.texto_titulo = ft.Text(
            "Ninguna canción seleccionada",
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        self.texto_artista = ft.Text("", size=16, text_align=ft.TextAlign.CENTER)
        self.texto_album = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)
        self.texto_año = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)
        self.texto_posicion = ft.Text(
            "0:00 / 0:00", size=14, text_align=ft.TextAlign.CENTER
        )

        self.barra_progreso = ft.ProgressBar(width=300, height=5, value=0)
        self.control_volumen = ft.Slider(
            min=0, max=1, value=1, width=150, on_change=self.cambiar_volumen
        )

        self.boton_reproducir = ft.IconButton(
            ft.icons.PLAY_ARROW, on_click=self.alternar_reproduccion, icon_size=32
        )
        self.boton_anterior = ft.IconButton(
            ft.icons.SKIP_PREVIOUS, on_click=self.cancion_anterior, icon_size=24
        )
        self.boton_siguiente = ft.IconButton(
            ft.icons.SKIP_NEXT, on_click=self.cancion_siguiente, icon_size=24
        )
        self.boton_aleatorio = ft.IconButton(
            ft.icons.SHUFFLE, on_click=self.alternar_aleatorio, icon_size=24
        )
        self.boton_repetir = ft.IconButton(
            ft.icons.REPEAT, on_click=self.alternar_repetir, icon_size=24
        )
        self.boton_favorito = ft.IconButton(
            ft.icons.FAVORITE_BORDER, on_click=self.alternar_favorito, icon_size=24
        )
        self.boton_me_gusta = ft.IconButton(
            ft.icons.THUMB_UP_OUTLINED, on_click=self.alternar_me_gusta, icon_size=24
        )
        self.boton_adelantar_10 = ft.IconButton(
            ft.icons.FORWARD_10, on_click=self.adelantar_10, icon_size=24
        )
        self.boton_retroceder_10 = ft.IconButton(
            ft.icons.REPLAY_10, on_click=self.retroceder_10, icon_size=24
        )

        self.lista_canciones = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self.boton_seleccionar_carpeta = ft.ElevatedButton(
            "Seleccionar Carpeta", on_click=self.seleccionar_carpeta, style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )

        self.interruptor_tema = ft.Switch(label="Modo oscuro", on_change=self.cambiar_tema)

        info_cancion = ft.Column(
            [
                self.imagen_portada,
                self.texto_titulo,
                self.texto_artista,
                self.texto_album,
                self.texto_año,
                self.texto_posicion,
                self.barra_progreso,
                ft.Row(
                    [
                        self.boton_anterior,
                        self.boton_retroceder_10,
                        self.boton_reproducir,
                        self.boton_adelantar_10,
                        self.boton_siguiente,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        self.boton_aleatorio,
                        self.boton_repetir,
                        self.boton_favorito,
                        self.boton_me_gusta,
                        ft.Icon(ft.icons.VOLUME_UP, size=20),
                        self.control_volumen,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.boton_seleccionar_carpeta, self.interruptor_tema],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Card(content=info_cancion, elevation=10, width=500),
                            ft.VerticalDivider(width=1),
                            ft.Card(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Lista de reproducción",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        self.lista_canciones,
                                    ]
                                ),
                                elevation=10,
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                ],
                spacing=20,
            ),
            padding=20,
        )

    def seleccionar_carpeta(self, e):
        def resultado_seleccion_carpeta(e: ft.FilePickerResultEvent):
            if e.path:
                self.cargar_canciones(e.path)

        selector = ft.FilePicker(on_result=resultado_seleccion_carpeta)
        self.page.overlay.append(selector)
        self.page.update()
        selector.get_directory_path()

    def cargar_canciones(self, ruta_carpeta):
        self.canciones = []
        for raiz, directorios, archivos in os.walk(ruta_carpeta):
            for archivo in archivos:
                if archivo.endswith(".mp3"):
                    self.canciones.append(Cancion(os.path.join(raiz, archivo)))
        self.actualizar_lista_canciones()
        self.guardar_canciones()
        if self.canciones:
            self.reproducir_cancion(0)

    def actualizar_lista_canciones(self):
        self.lista_canciones.controls.clear()
        for i, cancion in enumerate(self.canciones):
            self.lista_canciones.controls.append(
                ft.ListTile(
                    title=ft.Text(cancion.titulo, size=16),
                    subtitle=ft.Text(cancion.artista, size=14),
                    on_click=lambda _, x=i: self.reproducir_cancion(x),
                    dense=True,
                )
            )
        self.update()

    async def iniciar_temporizador(self):
        while self.reproduciendo:
            self.actualizar_posicion()
            await asyncio.sleep(1)

    def reproducir_cancion(self, indice):
        self.indice_cancion_actual = indice
        self.actualizar_info_cancion()
        pygame.mixer.music.load(self.canciones[self.indice_cancion_actual].ruta)
        pygame.mixer.music.play()
        self.reproduciendo = True
        self.boton_reproducir.icon = ft.icons.PAUSE
        self.tiempo_inicio = time.time()
        self.posicion_actual = 0
        self.update()
        asyncio.create_task(self.iniciar_temporizador())

    def actualizar_info_cancion(self):
        cancion_actual = self.canciones[self.indice_cancion_actual]
        self.texto_titulo.value = cancion_actual.titulo
        self.texto_artista.value = cancion_actual.artista
        self.texto_album.value = cancion_actual.album
        self.texto_año.value = str(cancion_actual.año)
        if cancion_actual.portada:
            self.imagen_portada.src = cancion_actual.portada
        else:
            self.imagen_portada.src = None
        self.update()

    def alternar_reproduccion(self, e):
        if self.canciones:
            if self.reproduciendo:
                pygame.mixer.music.pause()
                self.boton_reproducir.icon = ft.icons.PLAY_ARROW
                self.posicion_actual += time.time() - self.tiempo_inicio
            else:
                pygame.mixer.music.unpause()
                self.boton_reproducir.icon = ft.icons.PAUSE
                self.tiempo_inicio = time.time()
            self.reproduciendo = not self.reproduciendo
            self.update()

    def cancion_anterior(self, e):
        if self.canciones:
            self.indice_cancion_actual = (self.indice_cancion_actual - 1) % len(self.canciones)
            self.reproducir_cancion(self.indice_cancion_actual)

    def cancion_siguiente(self, e):
        if self.canciones:
            if self.aleatorio:
                self.indice_cancion_actual = random.randint(0, len(self.canciones) - 1)
            else:
                self.indice_cancion_actual = (self.indice_cancion_actual + 1) % len(
                    self.canciones
                )
            self.reproducir_cancion(self.indice_cancion_actual)

    def alternar_aleatorio(self, e):
        self.aleatorio = not self.aleatorio
        self.boton_aleatorio.icon = (
            ft.icons.SHUFFLE_ON if self.aleatorio else ft.icons.SHUFFLE
        )
        self.update()

    def alternar_repetir(self, e):
        self.repetir = not self.repetir
        self.boton_repetir.icon = (
            ft.icons.REPEAT_ONE if self.repetir else ft.icons.REPEAT
        )
        self.update()

    def alternar_favorito(self, e):
        if self.canciones:
            cancion_actual = self.canciones[self.indice_cancion_actual]
            if cancion_actual in self.favoritos:
                self.favoritos.remove(cancion_actual)
                self.boton_favorito.icon = ft.icons.FAVORITE_BORDER
            else:
                self.favoritos.add(cancion_actual)
                self.boton_favorito.icon = ft.icons.FAVORITE
            self.update()

    def alternar_me_gusta(self, e):
        if self.canciones:
            cancion_actual = self.canciones[self.indice_cancion_actual]
            if cancion_actual in self.me_gusta:
                self.me_gusta.remove(cancion_actual)
                self.boton_me_gusta.icon = ft.icons.THUMB_UP_OUTLINED
            else:
                self.me_gusta.add(cancion_actual)
                self.boton_me_gusta.icon = ft.icons.THUMB_UP
            self.update()

    def adelantar_10(self, e):
        if self.canciones:
            tiempo_actual = time.time()
            transcurrido = tiempo_actual - self.tiempo_inicio + self.posicion_actual
            nueva_posicion = min(
                transcurrido + 10, self.canciones[self.indice_cancion_actual].duracion
            )
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=nueva_posicion)
            self.tiempo_inicio = time.time()
            self.posicion_actual = nueva_posicion
            self.actualizar_posicion()

    def retroceder_10(self, e):
        if self.canciones:
            tiempo_actual = time.time()
            transcurrido = tiempo_actual - self.tiempo_inicio + self.posicion_actual
            nueva_posicion = max(transcurrido - 10, 0)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=nueva_posicion)
            self.tiempo_inicio = time.time()
            self.posicion_actual = nueva_posicion
            self.actualizar_posicion()

    def actualizar_posicion(self):
        if self.reproduciendo:
            tiempo_actual = time.time()
            transcurrido = tiempo_actual - self.tiempo_inicio + self.posicion_actual
            duracion_total = self.canciones[self.indice_cancion_actual].duracion
            self.texto_posicion.value = (
                f"{self.formatear_tiempo(transcurrido)} / {self.formatear_tiempo(duracion_total)}"
            )
            self.barra_progreso.value = transcurrido / duracion_total
            self.update()
        return self.reproduciendo

    def formatear_tiempo(self, segundos):
        minutos, segundos = divmod(int(segundos), 60)
        return f"{minutos}:{segundos:02d}"

    def cambiar_volumen(self, e):
        pygame.mixer.music.set_volume(e.control.value)

    def cambiar_tema(self, e):
        if e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()

    def guardar_canciones(self):
        canciones_guardadas = [cancion.ruta for cancion in self.canciones]
        with open("canciones.json", "w") as f:
            json.dump(canciones_guardadas, f)

    def cargar_canciones_guardadas(self):
        try:
            with open("canciones.json", "r") as f:
                rutas_guardadas = json.load(f)
            for ruta in rutas_guardadas:
                if os.path.exists(ruta):
                    self.canciones.append(Cancion(ruta))
            self.actualizar_lista_canciones()
        except FileNotFoundError:
            pass

def main(page: ft.Page):
    page.title = "Reproductor de Música"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    page.window.width = 1200
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    
    reproductor = ReproductorMusica()
    page.add(reproductor)

    def on_window_event(e):
        if e.data == "close":
            reproductor.guardar_canciones()

    page.window.on_event = on_window_event

ft.app(target=main)