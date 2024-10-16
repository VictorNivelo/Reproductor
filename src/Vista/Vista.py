from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from customtkinter import CTkImage


class VistaReproductor:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música")
        self.root.geometry("1200x720")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.frame_principal = ctk.CTkFrame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_izquierdo = ctk.CTkFrame(self.frame_principal, width=400)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)
        self.frame_derecho = ctk.CTkFrame(self.frame_principal)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.caratula = ctk.CTkLabel(self.frame_izquierdo, text="")
        self.caratula.pack(pady=10)
        self.titulo = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.titulo.pack()
        self.artista = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=14))
        self.artista.pack()
        self.album = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=12))
        self.album.pack()
        self.año = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=12))
        self.año.pack()
        self.numero_pista = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=12))
        self.numero_pista.pack()
        self.duracion = ctk.CTkLabel(self.frame_izquierdo, text="", font=ctk.CTkFont(size=12))
        self.duracion.pack()
        self.barra_progreso = ctk.CTkProgressBar(self.frame_izquierdo, width=300)
        self.barra_progreso.pack(pady=10)
        self.tiempo_actual = ctk.CTkLabel(self.frame_izquierdo, text="0:00")
        self.tiempo_actual.pack(side=tk.LEFT)
        self.tiempo_total = ctk.CTkLabel(self.frame_izquierdo, text="0:00")
        self.tiempo_total.pack(side=tk.RIGHT)
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
        self.boton_aleatorio = ctk.CTkButton(self.frame_controles, text="🔀", width=40)
        self.boton_aleatorio.pack(side=tk.LEFT, padx=5)
        self.boton_repetir = ctk.CTkButton(self.frame_controles, text="🔁", width=40)
        self.boton_repetir.pack(side=tk.LEFT, padx=5)
        self.boton_favorito = ctk.CTkButton(self.frame_controles, text="☆", width=40)
        self.boton_favorito.pack(side=tk.LEFT, padx=5)
        self.boton_me_gusta = ctk.CTkButton(self.frame_controles, text="👍", width=40)
        self.boton_me_gusta.pack(side=tk.LEFT, padx=5)
        self.boton_agregar_cola = ctk.CTkButton(self.frame_controles, text="➕", width=40)
        self.boton_agregar_cola.pack(side=tk.LEFT, padx=5)
        self.volumen_slider = ctk.CTkSlider(self.frame_izquierdo, from_=0, to=100)
        self.volumen_slider.set(100)
        self.volumen_slider.pack(pady=10)
        self.boton_mute = ctk.CTkButton(self.frame_izquierdo, text="🔊", width=40)
        self.boton_mute.pack()
        self.boton_mostrar_cola = ctk.CTkButton(self.frame_izquierdo, text="Mostrar Cola")
        self.boton_mostrar_cola.pack(pady=10)
        self.notebook = ctk.CTkTabview(self.frame_derecho)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tab_todas = self.notebook.add("Todas")
        self.tab_me_gusta = self.notebook.add("Me gusta")
        self.tab_favoritos = self.notebook.add("Favoritos")
        self.tab_personalizadas = self.notebook.add("Listas personalizadas")
        self.lista_canciones = tk.Listbox(self.tab_todas, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#1F538D")
        self.lista_canciones.pack(fill=tk.BOTH, expand=True)
        self.lista_me_gusta = tk.Listbox(self.tab_me_gusta, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#1F538D")
        self.lista_me_gusta.pack(fill=tk.BOTH, expand=True)
        self.lista_favoritos = tk.Listbox(self.tab_favoritos, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#1F538D")
        self.lista_favoritos.pack(fill=tk.BOTH, expand=True)
        self.frame_listas_personalizadas = ctk.CTkFrame(self.tab_personalizadas)
        self.frame_listas_personalizadas.pack(fill=tk.BOTH, expand=True)
        self.lista_personalizadas = tk.Listbox(
            self.frame_listas_personalizadas, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#1F538D"
        )
        self.lista_personalizadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_botones_listas = ctk.CTkFrame(self.frame_listas_personalizadas)
        self.frame_botones_listas.pack(side=tk.RIGHT, fill=tk.Y)
        self.boton_nueva_lista = ctk.CTkButton(self.frame_botones_listas, text="Nueva lista")
        self.boton_nueva_lista.pack(pady=5)
        self.boton_eliminar_lista = ctk.CTkButton(self.frame_botones_listas, text="Eliminar lista")
        self.boton_eliminar_lista.pack(pady=5)
        self.boton_modificar_lista = ctk.CTkButton(self.frame_botones_listas, text="Modificar lista")
        self.boton_modificar_lista.pack(pady=5)
        self.boton_seleccionar_carpeta = ctk.CTkButton(self.frame_derecho, text="Seleccionar carpeta")
        self.boton_seleccionar_carpeta.pack(pady=10)

    def actualizar_cancion(self, cancion):
        self.titulo.configure(text=cancion.titulo)
        self.artista.configure(text=cancion.artista)
        self.album.configure(text=f"Álbum: {cancion.album}")
        self.año.configure(text=f"Año: {cancion.año}")
        self.numero_pista.configure(text=f"Pista: {cancion.numero_pista}")
        self.duracion.configure(text=f"Duración: {int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}")
        self.tiempo_total.configure(text=f"{int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}")
        if cancion.caratula:
            image = cancion.caratula.resize((300, 300), Image.LANCZOS)
            photo = CTkImage(light_image=image, dark_image=image, size=(300, 300))
            self.caratula.configure(image=photo)
            self.caratula.image = photo
        else:
            self.caratula.configure(image=None)
            self.caratula.image = None

    def actualizar_lista_canciones(self, canciones):
        self.lista_canciones.delete(0, tk.END)
        for cancion in canciones:
            self.lista_canciones.insert(tk.END, f"{cancion.titulo} - {cancion.artista}")

    def actualizar_lista_me_gusta(self, canciones):
        self.lista_me_gusta.delete(0, tk.END)
        for cancion in canciones:
            self.lista_me_gusta.insert(tk.END, f"{cancion.titulo} - {cancion.artista}")

    def actualizar_lista_favoritos(self, canciones):
        self.lista_favoritos.delete(0, tk.END)
        for cancion in canciones:
            self.lista_favoritos.insert(tk.END, f"{cancion.titulo} - {cancion.artista}")

    def actualizar_listas_personalizadas(self, listas):
        self.lista_personalizadas.delete(0, tk.END)
        for nombre in listas.keys():
            self.lista_personalizadas.insert(tk.END, nombre)

    def actualizar_progreso(self, valor, tiempo_actual):
        self.barra_progreso.set(valor)
        minutos, segundos = divmod(int(tiempo_actual), 60)
        self.tiempo_actual.configure(text=f"{minutos}:{segundos:02d}")

    def actualizar_boton_reproducir_pausar(self, reproduciendo, pausado):
        if reproduciendo and not pausado:
            self.boton_reproducir_pausar.configure(text="⏸")
        else:
            self.boton_reproducir_pausar.configure(text="▶")

    def actualizar_boton_aleatorio(self, activo):
        self.boton_aleatorio.configure(text="🔀" if activo else "🔀")

    def actualizar_boton_repetir(self, activo):
        self.boton_repetir.configure(text="🔁" if activo else "🔁")

    def actualizar_boton_favorito(self, activo):
        self.boton_favorito.configure(text="★" if activo else "☆")

    def actualizar_boton_me_gusta(self, activo):
        self.boton_me_gusta.configure(text="👍" if activo else "👍")

    def seleccionar_directorio(self):
        return ctk.filedialog.askdirectory()

    def mostrar_dialogo_nueva_lista(self):
        return ctk.CTkInputDialog(text="Nombre de la lista:", title="Nueva lista").get_input()

    def mostrar_dialogo_modificar_lista(self, nombre_actual):
        return ctk.CTkInputDialog(text="Nuevo nombre de la lista:", title="Modificar lista").get_input()

    def actualizar_icono_volumen(self, volumen):
        if volumen == 0:
            self.boton_mute.configure(text="🔇")
        elif volumen < 0.5:
            self.boton_mute.configure(text="🔉")
        else:
            self.boton_mute.configure(text="🔊")

    def mostrar_cola(self, cola):
        ventana_cola = ctk.CTkToplevel(self.root)
        ventana_cola.title("Cola de reproducción")
        ventana_cola.geometry("400x300")
        lista_cola = tk.Listbox(ventana_cola, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#1F538D")
        lista_cola.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for cancion in cola:
            lista_cola.insert(tk.END, f"{cancion.titulo} - {cancion.artista}")
