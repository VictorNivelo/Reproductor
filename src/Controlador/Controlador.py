from dataclasses import dataclass
from typing import Set
import threading
import pygame
import random
import time
import json
import os


@dataclass
class Cancion:
    titulo: str
    artista: str
    album: str
    duracion: float
    ruta: str


class CancionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Cancion):
            return obj.to_dict()
        return super().default(obj)


class ControladorReproductor:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.indice_actual = 0
        self.reproduciendo = False
        self.pausado = False
        self.modo_aleatorio = False
        self.modo_repetir = False
        self.favoritos = set()
        self.me_gusta = set()
        self.listas_personalizadas = {}
        self.cola_reproduccion = []
        self.volumen = 1.0
        self.mute = False
        self.tiempo_inicio = 0
        self.posicion_actual = 0
        self.historial_reproduccion = []
        pygame.init()
        pygame.mixer.init()
        self.cargar_configuracion()
        self.CAMBIAR_POSICION_EVENTO = pygame.USEREVENT + 1

    def iniciar(self):
        self._configurar_botones()
        self._configurar_listas()
        self.cargar_canciones()
        self._actualizar_interfaz()
        threading.Thread(target=self.manejar_eventos, daemon=True).start()

    def _configurar_botones(self):
        self.vista.boton_seleccionar_carpeta.configure(command=self.seleccionar_carpeta)
        self.vista.boton_reproducir_pausar.configure(command=self.reproducir_pausar)
        self.vista.boton_anterior.configure(command=self.anterior)
        self.vista.boton_siguiente.configure(command=self.siguiente)
        self.vista.boton_aleatorio.configure(command=self.alternar_aleatorio)
        self.vista.boton_repetir.configure(command=self.alternar_repetir)
        self.vista.boton_favorito.configure(command=self.alternar_favorito)
        self.vista.boton_me_gusta.configure(command=self.alternar_me_gusta)
        self.vista.volumen_slider.configure(command=self.cambiar_volumen)
        self.vista.boton_mute.configure(command=self.alternar_mute)
        self.vista.boton_nueva_lista.configure(command=self.crear_lista_personalizada)
        self.vista.boton_eliminar_lista.configure(command=self.eliminar_lista_personalizada)
        self.vista.boton_modificar_lista.configure(command=self.modificar_lista_personalizada)
        self.vista.boton_mostrar_cola.configure(command=self.mostrar_cola)
        self.vista.boton_adelantar.configure(command=lambda: self.cambiar_posicion(10))
        self.vista.boton_retroceder.configure(command=lambda: self.cambiar_posicion(-10))
        self.vista.boton_agregar_cola.configure(command=self.agregar_cancion_actual_a_cola)

    def _configurar_listas(self):
        self.vista.lista_canciones.bind("<<TreeviewSelect>>", self.seleccionar_cancion)
        self.vista.lista_me_gusta.bind("<<TreeviewSelect>>", self.seleccionar_cancion)
        self.vista.lista_favoritos.bind("<<TreeviewSelect>>", self.seleccionar_cancion)
        if hasattr(self.vista, "lista_personalizadas"):
            self.vista.lista_personalizadas.bind("<<TreeviewSelect>>", self.seleccionar_lista_personalizada)

    def _actualizar_interfaz(self):
        self.vista.volumen_slider.set(self.volumen * 100)
        self.vista.actualizar_icono_volumen(self.volumen)
        self.vista.actualizar_boton_aleatorio(self.modo_aleatorio)
        self.vista.actualizar_boton_repetir(self.modo_repetir)

    def cargar_configuracion(self):
        self._crear_directorios()
        self._cargar_ajustes()
        self._cargar_listas()

    def _crear_directorios(self):
        os.makedirs("datos/configuracion", exist_ok=True)
        os.makedirs("datos/listas", exist_ok=True)
        os.makedirs("datos/listas/personalizadas", exist_ok=True)

    def _cargar_ajustes(self):
        try:
            with open("datos/configuracion/ajustes.json", "r") as f:
                config = json.load(f)
                self.modelo.directorio = config.get("directorio", "")
                self.volumen = config.get("volumen", 1.0)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error al cargar ajustes.json. Usando valores predeterminados.")

    def _cargar_listas(self):
        self._cargar_lista("favoritos.json", self.favoritos)
        self._cargar_lista("me_gusta.json", self.me_gusta)
        self._cargar_listas_personalizadas()
        self._cargar_cola()

    def _cargar_lista(self, nombre_archivo: str, lista: Set[str]):
        try:
            with open(f"datos/listas/{nombre_archivo}", "r") as f:
                lista.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error al cargar {nombre_archivo}. Inicializando vacío.")

    def _cargar_listas_personalizadas(self):
        for archivo in os.listdir("datos/listas/personalizadas"):
            if archivo.endswith(".json"):
                nombre_lista = os.path.splitext(archivo)[0]
                try:
                    with open(f"datos/listas/personalizadas/{archivo}", "r") as f:
                        self.listas_personalizadas[nombre_lista] = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error al cargar {archivo}. Inicializando vacío.")
                    self.listas_personalizadas[nombre_lista] = []

    def _cargar_cola(self):
        try:
            with open("datos/listas/cola.json", "r") as f:
                rutas_cola = json.load(f)
                self.cola_reproduccion = [
                    self.modelo.obtener_cancion_por_ruta(ruta)
                    for ruta in rutas_cola
                    if self.modelo.obtener_cancion_por_ruta(ruta) is not None
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error al cargar cola.json. Inicializando vacío.")
            self.cola_reproduccion = []

    def guardar_configuracion(self):
        config = {"directorio": self.modelo.directorio, "volumen": self.volumen}
        self._guardar_json("datos/configuracion/ajustes.json", config)
        self._guardar_json("datos/listas/favoritos.json", list(self.favoritos))
        self._guardar_json("datos/listas/me_gusta.json", list(self.me_gusta))
        self._guardar_listas_personalizadas()
        self._guardar_json("datos/listas/cola.json", [cancion.ruta for cancion in self.cola_reproduccion])

    def _guardar_json(self, ruta: str, datos):
        with open(ruta, "w") as f:
            json.dump(datos, f)

    def _guardar_listas_personalizadas(self):
        for nombre, canciones in self.listas_personalizadas.items():
            self._guardar_json(f"datos/listas/personalizadas/{nombre}.json", canciones)

    def seleccionar_carpeta(self):
        ruta = self.vista.seleccionar_directorio()
        if ruta:
            self.modelo.directorio = ruta
            self.cargar_canciones()
            self.guardar_configuracion()

    def cargar_canciones(self):
        if self.modelo.directorio:
            self.modelo.cargar_canciones(self.modelo.directorio)
            self.vista.actualizar_lista_canciones(self.modelo.obtener_canciones(), "lista_canciones")
            self.actualizar_listas_especiales()
            if self.modelo.canciones:
                self.vista.actualizar_cancion(self.modelo.canciones[0])

    def reproducir_pausar(self):
        if not self.modelo.canciones:
            return
        if not self.reproduciendo:
            self._iniciar_reproduccion()
        else:
            self._pausar_reproduccion()
        self.vista.actualizar_boton_reproducir_pausar(self.reproduciendo, self.pausado)

    def _iniciar_reproduccion(self):
        cancion_actual = self.modelo.canciones[self.indice_actual]
        if self.pausado:
            pygame.mixer.music.unpause()
            self.tiempo_inicio = time.time() - self.posicion_actual
        else:
            pygame.mixer.music.load(cancion_actual.ruta)
            pygame.mixer.music.play(start=self.posicion_actual)
            self.tiempo_inicio = time.time() - self.posicion_actual
            self.historial_reproduccion.append(cancion_actual)
        self.reproduciendo = True
        self.pausado = False
        threading.Thread(target=self.actualizar_progreso, daemon=True).start()

    def _pausar_reproduccion(self):
        pygame.mixer.music.pause()
        tiempo_actual = time.time()
        self.posicion_actual += tiempo_actual - self.tiempo_inicio
        self.reproduciendo = False
        self.pausado = True

    def anterior(self):
        if not self.modelo.canciones:
            return
        if self.modo_aleatorio:
            self.indice_actual = random.randint(0, len(self.modelo.canciones) - 1)
        else:
            self.indice_actual = (self.indice_actual - 1) % len(self.modelo.canciones)
        self._cambiar_cancion()

    def siguiente(self):
        if self.cola_reproduccion:
            siguiente_cancion = self.cola_reproduccion.pop(0)
            self.indice_actual = self.modelo.canciones.index(siguiente_cancion)
        elif self.modelo.canciones:
            if self.modo_aleatorio:
                self.indice_actual = random.randint(0, len(self.modelo.canciones) - 1)
            else:
                self.indice_actual = (self.indice_actual + 1) % len(self.modelo.canciones)
        self._cambiar_cancion()

    def _cambiar_cancion(self):
        self.detener()
        self.posicion_actual = 0
        cancion_actual = self.modelo.canciones[self.indice_actual]
        self.vista.actualizar_cancion(cancion_actual)
        self.reproducir_pausar()
        self.guardar_configuracion()

    def seleccionar_cancion(self, event):
        lista_actual = event.get("widget")
        valores = event.get("values")
        if valores:
            titulo, artista = valores[0], valores[1]
            cancion = next((c for c in self.modelo.canciones if c.titulo == titulo and c.artista == artista), None)
            if cancion:
                self.indice_actual = self.modelo.canciones.index(cancion)
                self.vista.actualizar_cancion(cancion)
                self._cambiar_cancion()

    def seleccionar_lista_personalizada(self, nombre_lista):
        self.lista_personalizada_seleccionada = nombre_lista
        if nombre_lista in self.listas_personalizadas:
            canciones = [
                self.modelo.obtener_cancion_por_ruta(ruta) for ruta in self.listas_personalizadas[nombre_lista]
            ]
            canciones = [c for c in canciones if c is not None]
            self.vista.actualizar_lista_canciones(canciones)

    def detener(self):
        if self.reproduciendo:
            pygame.mixer.music.stop()
            self.reproduciendo = False
            self.pausado = False

    def actualizar_progreso(self):
        while self.reproduciendo:
            tiempo_actual = time.time()
            transcurrido = tiempo_actual - self.tiempo_inicio + self.posicion_actual
            duracion_total = self.modelo.canciones[self.indice_actual].duracion
            progreso = min(transcurrido / duracion_total, 1.0)
            self.vista.actualizar_progreso(progreso, transcurrido)
            if transcurrido >= duracion_total:
                self.siguiente()
            time.sleep(0.1)

    def manejar_eventos(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    if self.modo_repetir:
                        self.reproducir_pausar()
                    else:
                        self.siguiente()
                elif event.type == self.CAMBIAR_POSICION_EVENTO:
                    self._cambiar_posicion_interno(event.tiempo)
            clock.tick(10)

    def alternar_aleatorio(self):
        self.modo_aleatorio = not self.modo_aleatorio
        self.vista.actualizar_boton_aleatorio(self.modo_aleatorio)

    def alternar_repetir(self):
        self.modo_repetir = not self.modo_repetir
        self.vista.actualizar_boton_repetir(self.modo_repetir)

    def alternar_favorito(self):
        cancion_actual = self.modelo.canciones[self.indice_actual]
        if cancion_actual.ruta in self.favoritos:
            self.favoritos.remove(cancion_actual.ruta)
        else:
            self.favoritos.add(cancion_actual.ruta)
        self.guardar_configuracion()
        self.actualizar_listas_especiales()
        self.vista.actualizar_boton_favorito(cancion_actual.ruta in self.favoritos)

    def alternar_me_gusta(self):
        cancion_actual = self.modelo.canciones[self.indice_actual]
        if cancion_actual.ruta in self.me_gusta:
            self.me_gusta.remove(cancion_actual.ruta)
        else:
            self.me_gusta.add(cancion_actual.ruta)
        self.vista.actualizar_boton_me_gusta(cancion_actual.ruta in self.me_gusta)
        self.actualizar_listas_especiales()
        self.guardar_configuracion()

    def mostrar_cola(self):
        self.vista.mostrar_cola(self.cola_reproduccion)

    def crear_lista_personalizada(self):
        nombre = self.vista.mostrar_dialogo_nueva_lista()
        if nombre and nombre not in self.listas_personalizadas:
            self.listas_personalizadas[nombre] = []
            self.guardar_configuracion()
            self.actualizar_listas_especiales()

    def agregar_a_lista_personalizada(self, nombre_lista: str, cancion: Cancion):
        if nombre_lista in self.listas_personalizadas and cancion.ruta not in self.listas_personalizadas[nombre_lista]:
            self.listas_personalizadas[nombre_lista].append(cancion.ruta)
            self.guardar_configuracion()
            self.actualizar_listas_especiales()

    def eliminar_lista_personalizada(self):
        if hasattr(self, "lista_personalizada_seleccionada"):
            nombre = self.lista_personalizada_seleccionada
            if nombre in self.listas_personalizadas:
                del self.listas_personalizadas[nombre]
                os.remove(f"datos/listas/personalizadas/{nombre}.json")
                self.guardar_configuracion()
                self.actualizar_listas_especiales()
                delattr(self, "lista_personalizada_seleccionada")
            else:
                self.vista.mostrar_error("No se ha seleccionado ninguna lista para eliminar")
        else:
            self.vista.mostrar_error("No se ha seleccionado ninguna lista para eliminar")

    def eliminar_de_lista_personalizada(self, nombre_lista: str, cancion: Cancion):
        if nombre_lista in self.listas_personalizadas:
            self.listas_personalizadas[nombre_lista] = [
                c for c in self.listas_personalizadas[nombre_lista] if c != cancion.ruta
            ]
            self.guardar_configuracion()
            self.actualizar_listas_especiales()

    def modificar_lista_personalizada(self):
        if hasattr(self, "lista_personalizada_seleccionada"):
            nombre_antiguo = self.lista_personalizada_seleccionada
            nombre_nuevo = self.vista.mostrar_dialogo_modificar_lista(nombre_antiguo)
            if nombre_nuevo and nombre_nuevo != nombre_antiguo:
                self.listas_personalizadas[nombre_nuevo] = self.listas_personalizadas.pop(nombre_antiguo)
                os.rename(
                    f"datos/listas/personalizadas/{nombre_antiguo}.json",
                    f"datos/listas/personalizadas/{nombre_nuevo}.json",
                )
                self.guardar_configuracion()
                self.actualizar_listas_especiales()
                self.lista_personalizada_seleccionada = nombre_nuevo
        else:
            self.vista.mostrar_error("No se ha seleccionado ninguna lista para modificar")

    def actualizar_listas_especiales(self):
        canciones_me_gusta = [self.modelo.obtener_cancion_por_ruta(ruta) for ruta in self.me_gusta]
        canciones_favoritos = [self.modelo.obtener_cancion_por_ruta(ruta) for ruta in self.favoritos]
        self.vista.actualizar_lista_canciones([c for c in canciones_me_gusta if c is not None], "lista_me_gusta")
        self.vista.actualizar_lista_canciones([c for c in canciones_favoritos if c is not None], "lista_favoritos")
        self.vista.actualizar_listas_personalizadas(self.listas_personalizadas)

    def actualizar_cola(self):
        self.cola_reproduccion = self.modelo.canciones[self.indice_actual + 1 : self.indice_actual + 6]
        self.vista.mostrar_cola(self.cola_reproduccion)

    def actualizar_iconos_me_gusta_favoritos(self):
        for cancion in self.modelo.canciones:
            self.vista.actualizar_boton_me_gusta(cancion.ruta in self.me_gusta)
            self.vista.actualizar_boton_favorito(cancion.ruta in self.favoritos)

    def agregar_a_cola(self, cancion: Cancion):
        self.cola_reproduccion.append(cancion)
        self.vista.mostrar_cola(self.cola_reproduccion)

    def cambiar_volumen(self, volumen: float):
        self.volumen = float(volumen) / 100
        if not self.mute:
            pygame.mixer.music.set_volume(self.volumen)
        self.guardar_configuracion()

    def alternar_mute(self):
        self.mute = not self.mute
        pygame.mixer.music.set_volume(0 if self.mute else self.volumen)
        self.vista.actualizar_icono_volumen(0 if self.mute else self.volumen)

    def cambiar_posicion(self, segundos: int):
        pygame.event.post(pygame.event.Event(self.CAMBIAR_POSICION_EVENTO, {"tiempo": segundos}))

    def _cambiar_posicion_interno(self, segundos: int):
        if self.modelo.canciones:
            tiempo_actual = time.time()
            if self.reproduciendo:
                transcurrido = tiempo_actual - self.tiempo_inicio + self.posicion_actual
            else:
                transcurrido = self.posicion_actual
            nueva_posicion = max(0, min(transcurrido + segundos, self.modelo.canciones[self.indice_actual].duracion))
            if self.reproduciendo:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.modelo.canciones[self.indice_actual].ruta)
                pygame.mixer.music.play(start=nueva_posicion)
                self.tiempo_inicio = time.time()
            self.posicion_actual = nueva_posicion
            self.vista.actualizar_progreso(
                nueva_posicion / self.modelo.canciones[self.indice_actual].duracion, nueva_posicion
            )

    def agregar_cancion_actual_a_cola(self):
        cancion_actual = self.modelo.canciones[self.indice_actual]
        self.cola_reproduccion.append(cancion_actual)
        self.vista.mostrar_cola(self.cola_reproduccion)

    def mostrar_historial(self):
        self.vista.mostrar_historial(self.historial_reproduccion)

    def limpiar_historial(self):
        self.historial_reproduccion.clear()
        self.vista.mostrar_historial(self.historial_reproduccion)

    def ordenar_lista(self, criterio: str):
        if criterio == "titulo":
            self.modelo.canciones.sort(key=lambda x: x.titulo)
        elif criterio == "artista":
            self.modelo.canciones.sort(key=lambda x: x.artista)
        elif criterio == "album":
            self.modelo.canciones.sort(key=lambda x: x.album)
        elif criterio == "duracion":
            self.modelo.canciones.sort(key=lambda x: x.duracion)
        self.vista.actualizar_lista_canciones(self.modelo.canciones)

    def buscar_cancion(self, termino):
        lista_actual = self.vista.notebook.get()
        if not termino:
            if lista_actual == "Todas":
                self.vista.actualizar_lista_canciones(self.modelo.canciones)
            elif lista_actual == "Me gusta":
                self.vista.actualizar_lista_canciones(
                    [c for c in self.modelo.canciones if c.ruta in self.me_gusta], "lista_me_gusta"
                )
            elif lista_actual == "Favoritos":
                self.vista.actualizar_lista_canciones(
                    [c for c in self.modelo.canciones if c.ruta in self.favoritos], "lista_favoritos"
                )
            elif lista_actual == "Listas personalizadas":
                self._actualizar_lista_personalizada_actual()
            return
        resultados = [
            c
            for c in self.modelo.canciones
            if termino.lower() in c.titulo.lower()
            or termino.lower() in c.artista.lower()
            or termino.lower() in c.album.lower()
        ]
        if lista_actual == "Todas":
            self.vista.actualizar_lista_canciones(resultados)
        elif lista_actual == "Me gusta":
            self.vista.actualizar_lista_canciones([c for c in resultados if c.ruta in self.me_gusta], "lista_me_gusta")
        elif lista_actual == "Favoritos":
            self.vista.actualizar_lista_canciones(
                [c for c in resultados if c.ruta in self.favoritos], "lista_favoritos"
            )
        elif lista_actual == "Listas personalizadas":
            self._actualizar_lista_personalizada_actual(resultados)

    def _actualizar_lista_personalizada_actual(self, canciones=None):
        seleccion = self.vista.lista_personalizadas.selection()
        if seleccion:
            nombre = self.vista.lista_personalizadas.item(seleccion[0])["values"][0]
            if nombre in self.listas_personalizadas:
                if canciones is None:
                    canciones = self.modelo.canciones
                lista_filtrada = [c for c in canciones if c.ruta in self.listas_personalizadas[nombre]]
                self.vista.actualizar_lista_canciones(lista_filtrada)

    def ordenar_canciones(self, criterio):
        lista_actual = self.vista.notebook.get()
        if criterio == "título":
            key = lambda x: x.titulo
        elif criterio == "artista":
            key = lambda x: x.artista
        elif criterio == "álbum":
            key = lambda x: x.album
        elif criterio == "año":
            key = lambda x: x.año
        if lista_actual == "Todas":
            canciones = sorted(self.modelo.canciones, key=key)
            self.vista.actualizar_lista_canciones(canciones)
        elif lista_actual == "Me gusta":
            canciones = sorted([c for c in self.modelo.canciones if c.ruta in self.me_gusta], key=key)
            self.vista.actualizar_lista_canciones(canciones, "lista_me_gusta")
        elif lista_actual == "Favoritos":
            canciones = sorted([c for c in self.modelo.canciones if c.ruta in self.favoritos], key=key)
            self.vista.actualizar_lista_canciones(canciones, "lista_favoritos")
        elif lista_actual == "Listas personalizadas":
            nombre_lista = self.vista.lista_personalizadas.selection()
            if nombre_lista:
                nombre = self.vista.lista_personalizadas.item(nombre_lista[0])["values"][0]
                if nombre in self.listas_personalizadas:
                    canciones = sorted(
                        [c for c in self.modelo.canciones if c.ruta in self.listas_personalizadas[nombre]], key=key
                    )
                    self.vista.actualizar_lista_canciones(canciones)

    def exportar_lista(self):
        lista_actual = self.vista.notebook.get()
        canciones = []
        if lista_actual == "Todas":
            canciones = self.modelo.canciones
        elif lista_actual == "Me gusta":
            canciones = [c for c in self.modelo.canciones if c.ruta in self.me_gusta]
        elif lista_actual == "Favoritos":
            canciones = [c for c in self.modelo.canciones if c.ruta in self.favoritos]
        elif lista_actual == "Listas personalizadas":
            if hasattr(self, "lista_personalizada_seleccionada"):
                nombre = self.lista_personalizada_seleccionada
                if nombre in self.listas_personalizadas:
                    canciones = [c for c in self.modelo.canciones if c.ruta in self.listas_personalizadas[nombre]]
        if not canciones:
            self.vista.mostrar_error("No hay canciones para exportar")
            return
        formato = self.vista.mostrar_dialogo_formato()
        if not formato:
            return
        ruta_archivo = self.vista.seleccionar_ruta_guardar(formato)
        if not ruta_archivo:
            return
        try:
            if formato == "txt":
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    for cancion in canciones:
                        f.write(f"{cancion.titulo} - {cancion.artista} - {cancion.album}\n")
            elif formato == "json":
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump([cancion.to_dict() for cancion in canciones], f, indent=4, ensure_ascii=False)
            self.vista.mostrar_info("Lista exportada con éxito")
        except Exception as e:
            self.vista.mostrar_error(f"Error al exportar la lista: {str(e)}")

    def importar_lista(self):
        ruta_archivo = self.vista.seleccionar_ruta_abrir()
        if not ruta_archivo:
            return
        nombre_lista = os.path.splitext(os.path.basename(ruta_archivo))[0]
        extension = os.path.splitext(ruta_archivo)[1].lower()
        try:
            if extension == ".txt":
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    canciones = [linea.strip().split(" - ") for linea in f]
                    self.listas_personalizadas[nombre_lista] = [
                        cancion.ruta
                        for cancion in self.modelo.canciones
                        if any(cancion.titulo == c[0] and cancion.artista == c[1] for c in canciones)
                    ]
            elif extension == ".json":
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.listas_personalizadas[nombre_lista] = [
                        cancion.ruta
                        for cancion in self.modelo.canciones
                        if any(cancion.titulo == d["titulo"] and cancion.artista == d["artista"] for d in datos)
                    ]
            else:
                self.vista.mostrar_error("Formato de archivo no soportado")
                return
            self.guardar_configuracion()
            self.actualizar_listas_especiales()
            self.vista.mostrar_info(f"Lista '{nombre_lista}' importada con éxito")
        except Exception as e:
            self.vista.mostrar_error(f"Error al importar la lista: {str(e)}")

    def obtener_estadisticas(self):
        total_canciones = len(self.modelo.canciones)
        total_artistas = len(set(cancion.artista for cancion in self.modelo.canciones))
        total_albumes = len(set(cancion.album for cancion in self.modelo.canciones))
        duracion_total = sum(cancion.duracion for cancion in self.modelo.canciones)
        artista_mas_canciones = max(
            set(cancion.artista for cancion in self.modelo.canciones),
            key=lambda x: sum(1 for c in self.modelo.canciones if c.artista == x),
        )
        estadisticas = {
            "total_canciones": total_canciones,
            "total_artistas": total_artistas,
            "total_albumes": total_albumes,
            "duracion_total": duracion_total,
            "artista_mas_canciones": artista_mas_canciones,
        }
        self.vista.mostrar_estadisticas(estadisticas)

    def reproducir_cancion(self, cancion):
        if cancion in self.modelo.canciones:
            self.indice_actual = self.modelo.canciones.index(cancion)
            self.detener()
            self.posicion_actual = 0
            self.vista.actualizar_cancion(cancion)
            pygame.mixer.music.load(cancion.ruta)
            pygame.mixer.music.play()
            self.reproduciendo = True
            self.pausado = False
            self.vista.actualizar_boton_reproducir_pausar(self.reproduciendo, self.pausado)
            threading.Thread(target=self.actualizar_progreso, daemon=True).start()
