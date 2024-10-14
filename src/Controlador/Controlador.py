import threading
import pygame
import random
import time
import json
import os

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
        pygame.init()
        pygame.mixer.init()
        self.cargar_configuracion()
        self.ADELANTAR_EVENTO = pygame.USEREVENT + 1
        self.RETROCEDER_EVENTO = pygame.USEREVENT + 2

    def iniciar(self):
        self.vista.boton_seleccionar_carpeta.config(command=self.seleccionar_carpeta)
        self.vista.boton_reproducir_pausar.config(command=self.reproducir_pausar)
        self.vista.boton_anterior.config(command=self.anterior)
        self.vista.boton_siguiente.config(command=self.siguiente)
        self.vista.boton_aleatorio.config(command=self.alternar_aleatorio)
        self.vista.boton_repetir.config(command=self.alternar_repetir)
        self.vista.boton_favorito.config(command=self.alternar_favorito)
        self.vista.boton_me_gusta.config(command=self.alternar_me_gusta)
        self.vista.volumen_slider.config(command=self.cambiar_volumen)
        self.vista.boton_mute.config(command=self.alternar_mute)
        self.vista.lista_canciones.bind("<Double-1>", self.seleccionar_cancion)
        self.vista.boton_nueva_lista.config(command=self.crear_lista_personalizada)
        self.vista.boton_eliminar_lista.config(command=self.eliminar_lista_personalizada)
        self.vista.boton_modificar_lista.config(command=self.modificar_lista_personalizada)
        self.vista.boton_mostrar_cola.config(command=self.mostrar_cola)
        self.vista.boton_adelantar.config(command=self.adelantar_10_segundos)
        self.vista.boton_retroceder.config(command=self.retroceder_10_segundos)
        self.vista.boton_agregar_cola.config(command=self.agregar_cancion_actual_a_cola)
        self.cargar_canciones()
        self.actualizar_iconos_me_gusta_favoritos()
        threading.Thread(target=self.manejar_eventos, daemon=True).start()

    def cargar_configuracion(self):
        os.makedirs("datos/configuracion", exist_ok=True)
        os.makedirs("datos/listas", exist_ok=True)
        os.makedirs("datos/listas/personalizadas", exist_ok=True)
        if os.path.exists("datos/configuracion/ajustes.json"):
            with open("datos/configuracion/ajustes.json", "r") as f:
                config = json.load(f)
                self.modelo.directorio = config.get("directorio", "")
                self.volumen = config.get("volumen", 1.0)
        if os.path.exists("datos/listas/favoritos.json"):
            with open("datos/listas/favoritos.json", "r") as f:
                self.favoritos = set(json.load(f))
        if os.path.exists("datos/listas/me_gusta.json"):
            with open("datos/listas/me_gusta.json", "r") as f:
                self.me_gusta = set(json.load(f))
        if os.path.exists("datos/listas/personalizadas"):
            for archivo in os.listdir("datos/listas/personalizadas"):
                if archivo.endswith(".json"):
                    nombre_lista = os.path.splitext(archivo)[0]
                    with open(f"datos/listas/personalizadas/{archivo}", "r") as f:
                        self.listas_personalizadas[nombre_lista] = json.load(f)
        if os.path.exists("datos/listas/cola.json"):
            with open("datos/listas/cola.json", "r") as f:
                self.cola_reproduccion = json.load(f)

    def guardar_configuracion(self):
        config = {"directorio": self.modelo.directorio, "volumen": self.volumen}
        with open("datos/configuracion/ajustes.json", "w") as f:
            json.dump(config, f)
        with open("datos/listas/favoritos.json", "w") as f:
            json.dump(list(self.favoritos), f)
        with open("datos/listas/me_gusta.json", "w") as f:
            json.dump(list(self.me_gusta), f)
        for nombre, canciones in self.listas_personalizadas.items():
            with open(f"datos/listas/personalizadas/{nombre}.json", "w") as f:
                json.dump(canciones, f)
        with open("datos/listas/cola.json", "w") as f:
            json.dump(self.cola_reproduccion, f)

    def seleccionar_carpeta(self):
        ruta = self.vista.seleccionar_directorio()
        if ruta:
            self.modelo.directorio = ruta
            self.cargar_canciones()
            self.guardar_configuracion()

    def cargar_canciones(self):
        if self.modelo.directorio:
            self.modelo.cargar_canciones(self.modelo.directorio)
            self.vista.actualizar_lista_canciones(self.modelo.obtener_canciones())
            self.actualizar_listas_especiales()
            if self.modelo.canciones:
                self.vista.actualizar_cancion(self.modelo.canciones[0])

    def reproducir_pausar(self):
        if not self.modelo.canciones:
            return
        if not self.reproduciendo:
            cancion_actual = self.modelo.canciones[self.indice_actual]
            self.vista.actualizar_cancion(cancion_actual)
            pygame.mixer.music.load(cancion_actual.ruta)
            pygame.mixer.music.set_volume(self.volumen)
            pygame.mixer.music.play()
            self.reproduciendo = True
            self.pausado = False
            self.tiempo_inicio = time.time()
            self.posicion_actual = 0
            threading.Thread(target=self.actualizar_progreso, daemon=True).start()
        elif self.pausado:
            pygame.mixer.music.unpause()
            self.pausado = False
            self.tiempo_inicio = time.time()
        else:
            pygame.mixer.music.pause()
            self.pausado = True
            self.posicion_actual += time.time() - self.tiempo_inicio
        self.vista.actualizar_boton_reproducir_pausar(self.reproduciendo, self.pausado)

    def anterior(self):
        if self.modelo.canciones:
            if self.modo_aleatorio:
                self.indice_actual = random.randint(0, len(self.modelo.canciones) - 1)
            else:
                self.indice_actual = (self.indice_actual - 1) % len(self.modelo.canciones)
            self.detener()
            self.reproducir_pausar()

    def siguiente(self):
        if self.cola_reproduccion:
            siguiente_cancion = self.cola_reproduccion.pop(0)
            self.indice_actual = self.modelo.canciones.index(siguiente_cancion)
        elif self.modelo.canciones:
            if self.modo_aleatorio:
                self.indice_actual = random.randint(0, len(self.modelo.canciones) - 1)
            else:
                self.indice_actual = (self.indice_actual + 1) % len(self.modelo.canciones)
        self.detener()
        self.reproducir_pausar()
        self.guardar_configuracion()

    def seleccionar_cancion(self, event):
        indice = self.vista.lista_canciones.curselection()[0]
        self.indice_actual = indice
        self.detener()
        self.reproducir_pausar()

    def detener(self):
        if self.reproduciendo:
            pygame.mixer.music.stop()
            self.reproduciendo = False
            self.pausado = False

    def actualizar_progreso(self):
        while self.reproduciendo:
            if not self.pausado:
                tiempo_actual = time.time() - self.tiempo_inicio + self.posicion_actual
                duracion_total = self.modelo.canciones[self.indice_actual].duracion
                progreso = tiempo_actual / duracion_total
                self.vista.actualizar_progreso(progreso, tiempo_actual)
            time.sleep(0.1)
        self.vista.actualizar_progreso(0, 0)

    def manejar_eventos(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    if self.modo_repetir:
                        self.reproducir_pausar()
                    else:
                        self.siguiente()
                elif event.type == self.ADELANTAR_EVENTO:
                    self.adelantar_10_segundos_interno()
                elif event.type == self.RETROCEDER_EVENTO:
                    self.retroceder_10_segundos_interno()
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
        self.vista.actualizar_boton_favorito(cancion_actual.ruta in self.favoritos)
        self.actualizar_listas_especiales()
        self.guardar_configuracion()

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

    def agregar_a_lista_personalizada(self, nombre_lista, cancion):
        if nombre_lista in self.listas_personalizadas and cancion.ruta not in self.listas_personalizadas[nombre_lista]:
            self.listas_personalizadas[nombre_lista].append(cancion.ruta)
            self.guardar_configuracion()
            self.actualizar_listas_especiales()

    def eliminar_lista_personalizada(self):
        seleccion = self.vista.lista_personalizadas.curselection()
        if seleccion:
            indice = seleccion[0]
            nombre = self.vista.lista_personalizadas.get(indice)
            if nombre in self.listas_personalizadas:
                del self.listas_personalizadas[nombre]
                os.remove(f"datos/listas/personalizadas/{nombre}.json")
                self.guardar_configuracion()
                self.actualizar_listas_especiales()

    def eliminar_de_lista_personalizada(self, nombre_lista, cancion):
        if nombre_lista in self.listas_personalizadas:
            self.listas_personalizadas[nombre_lista] = [
                c for c in self.listas_personalizadas[nombre_lista] if c != cancion.ruta
            ]
            self.guardar_configuracion()
            self.actualizar_listas_especiales()

    def modificar_lista_personalizada(self):
        seleccion = self.vista.lista_personalizadas.curselection()
        if seleccion:
            indice = seleccion[0]
            nombre_antiguo = self.vista.lista_personalizadas.get(indice)
            nombre_nuevo = self.vista.mostrar_dialogo_modificar_lista(nombre_antiguo)
            if nombre_nuevo and nombre_nuevo != nombre_antiguo:
                self.listas_personalizadas[nombre_nuevo] = self.listas_personalizadas.pop(nombre_antiguo)
                os.rename(
                    f"datos/listas/personalizadas/{nombre_antiguo}.json",
                    f"datos/listas/personalizadas/{nombre_nuevo}.json",
                )
                self.guardar_configuracion()
                self.actualizar_listas_especiales()

    def actualizar_listas_especiales(self):
        canciones_me_gusta = [self.modelo.obtener_cancion_por_ruta(ruta) for ruta in self.me_gusta]
        canciones_favoritos = [self.modelo.obtener_cancion_por_ruta(ruta) for ruta in self.favoritos]
        self.vista.actualizar_lista_me_gusta(canciones_me_gusta)
        self.vista.actualizar_lista_favoritos(canciones_favoritos)
        self.vista.actualizar_listas_personalizadas(self.listas_personalizadas)

    def actualizar_cola(self):
        self.cola_reproduccion = self.modelo.canciones[self.indice_actual + 1 : self.indice_actual + 6]
        self.vista.mostrar_cola(self.cola_reproduccion)

    def actualizar_iconos_me_gusta_favoritos(self):
        for cancion in self.modelo.canciones:
            self.vista.actualizar_boton_me_gusta(cancion.ruta in self.me_gusta)
            self.vista.actualizar_boton_favorito(cancion.ruta in self.favoritos)

    def agregar_a_cola(self, cancion):
        self.cola_reproduccion.append(cancion)
        self.vista.mostrar_cola(self.cola_reproduccion)

    def cambiar_volumen(self, volumen):
        self.volumen = float(volumen) / 100
        if not self.mute:
            pygame.mixer.music.set_volume(self.volumen)
        self.guardar_configuracion()

    def alternar_mute(self):
        self.mute = not self.mute
        if self.mute:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.volumen)
        self.vista.actualizar_icono_volumen(0 if self.mute else self.volumen)

    def adelantar_10_segundos(self):
        pygame.event.post(pygame.event.Event(self.ADELANTAR_EVENTO))

    def retroceder_10_segundos(self):
        pygame.event.post(pygame.event.Event(self.RETROCEDER_EVENTO))

    def adelantar_10_segundos_interno(self):
        if self.reproduciendo:
            tiempo_actual = time.time() - self.tiempo_inicio + self.posicion_actual
            nueva_posicion = min(tiempo_actual + 10, self.modelo.canciones[self.indice_actual].duracion)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=nueva_posicion)
            self.tiempo_inicio = time.time()
            self.posicion_actual = nueva_posicion
            self.actualizar_progreso()

    def retroceder_10_segundos_interno(self):
        if self.reproduciendo:
            tiempo_actual = time.time() - self.tiempo_inicio + self.posicion_actual
            nueva_posicion = max(tiempo_actual - 10, 0)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=nueva_posicion)
            self.tiempo_inicio = time.time()
            self.posicion_actual = nueva_posicion
            self.actualizar_progreso()

    def agregar_cancion_actual_a_cola(self):
        cancion_actual = self.modelo.canciones[self.indice_actual]
        self.agregar_a_cola(cancion_actual)