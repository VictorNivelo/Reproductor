from tkinter import ttk, filedialog, simpledialog
from PIL import Image, ImageTk
import tkinter as tk


class VistaReproductor:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1E1E1E")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1E1E1E")
        style.configure("TLabel", background="#1E1E1E", foreground="#FFFFFF")
        style.configure("TButton", background="#3700B3", foreground="#FFFFFF", padding=10)
        style.map("TButton", background=[("active", "#6200EE")])
        style.configure("Horizontal.TProgressbar", background="#6200EE", troughcolor="#121212")
        style.configure("TNotebook", background="#1E1E1E", foreground="#FFFFFF")
        style.configure("TNotebook.Tab", background="#3700B3", foreground="#FFFFFF", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#6200EE")])
        self.frame_izquierdo = ttk.Frame(self.root, padding=20)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_derecho = ttk.Frame(self.root, padding=20)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.caratula = ttk.Label(self.frame_izquierdo)
        self.caratula.pack(pady=10)
        self.titulo = ttk.Label(self.frame_izquierdo, font=("Helvetica", 18, "bold"))
        self.titulo.pack()
        self.artista = ttk.Label(self.frame_izquierdo, font=("Helvetica", 14))
        self.artista.pack()
        self.album = ttk.Label(self.frame_izquierdo, font=("Helvetica", 12))
        self.album.pack()
        self.año = ttk.Label(self.frame_izquierdo, font=("Helvetica", 12))
        self.año.pack()
        self.numero_pista = ttk.Label(self.frame_izquierdo, font=("Helvetica", 12))
        self.numero_pista.pack()
        self.duracion = ttk.Label(self.frame_izquierdo, font=("Helvetica", 12))
        self.duracion.pack()
        self.barra_progreso = ttk.Progressbar(self.frame_izquierdo, length=300, mode="determinate")
        self.barra_progreso.pack(pady=10)
        self.tiempo_actual = ttk.Label(self.frame_izquierdo, text="0:00")
        self.tiempo_actual.pack(side=tk.LEFT)
        self.tiempo_total = ttk.Label(self.frame_izquierdo, text="0:00")
        self.tiempo_total.pack(side=tk.RIGHT)
        self.frame_controles = ttk.Frame(self.frame_izquierdo)
        self.frame_controles.pack(pady=10)
        self.boton_anterior = ttk.Button(self.frame_controles, text="⏮")
        self.boton_anterior.pack(side=tk.LEFT, padx=5)
        self.boton_retroceder = ttk.Button(self.frame_controles, text="⏪")
        self.boton_retroceder.pack(side=tk.LEFT, padx=5)
        self.boton_reproducir_pausar = ttk.Button(self.frame_controles, text="▶")
        self.boton_reproducir_pausar.pack(side=tk.LEFT, padx=5)
        self.boton_adelantar = ttk.Button(self.frame_controles, text="⏩")
        self.boton_adelantar.pack(side=tk.LEFT, padx=5)
        self.boton_siguiente = ttk.Button(self.frame_controles, text="⏭")
        self.boton_siguiente.pack(side=tk.LEFT, padx=5)
        self.boton_aleatorio = ttk.Button(self.frame_controles, text="🔀")
        self.boton_aleatorio.pack(side=tk.LEFT, padx=5)
        self.boton_repetir = ttk.Button(self.frame_controles, text="🔁")
        self.boton_repetir.pack(side=tk.LEFT, padx=5)
        self.boton_favorito = ttk.Button(self.frame_controles, text="☆")
        self.boton_favorito.pack(side=tk.LEFT, padx=5)
        self.boton_me_gusta = ttk.Button(self.frame_controles, text="👍")
        self.boton_me_gusta.pack(side=tk.LEFT, padx=5)
        self.boton_agregar_cola = ttk.Button(self.frame_controles, text="➕")
        self.boton_agregar_cola.pack(side=tk.LEFT, padx=5)
        self.volumen_slider = ttk.Scale(self.frame_izquierdo, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volumen_slider.set(100)
        self.volumen_slider.pack(pady=10)
        self.boton_mute = ttk.Button(self.frame_izquierdo, text="🔊")
        self.boton_mute.pack()
        self.boton_mostrar_cola = ttk.Button(self.frame_izquierdo, text="Mostrar Cola")
        self.boton_mostrar_cola.pack(pady=10)
        self.notebook = ttk.Notebook(self.frame_derecho)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tab_todas = ttk.Frame(self.notebook)
        self.tab_me_gusta = ttk.Frame(self.notebook)
        self.tab_favoritos = ttk.Frame(self.notebook)
        self.tab_personalizadas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_todas, text="Todas")
        self.notebook.add(self.tab_me_gusta, text="Me gusta")
        self.notebook.add(self.tab_favoritos, text="Favoritos")
        self.notebook.add(self.tab_personalizadas, text="Listas personalizadas")
        self.lista_canciones = tk.Listbox(self.tab_todas, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#6200EE")
        self.lista_canciones.pack(fill=tk.BOTH, expand=True)
        self.lista_me_gusta = tk.Listbox(self.tab_me_gusta, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#6200EE")
        self.lista_me_gusta.pack(fill=tk.BOTH, expand=True)
        self.lista_favoritos = tk.Listbox(self.tab_favoritos, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#6200EE")
        self.lista_favoritos.pack(fill=tk.BOTH, expand=True)
        self.frame_listas_personalizadas = ttk.Frame(self.tab_personalizadas)
        self.frame_listas_personalizadas.pack(fill=tk.BOTH, expand=True)
        self.lista_personalizadas = tk.Listbox(
            self.frame_listas_personalizadas, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#6200EE"
        )
        self.lista_personalizadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_botones_listas = ttk.Frame(self.frame_listas_personalizadas)
        self.frame_botones_listas.pack(side=tk.RIGHT, fill=tk.Y)
        self.boton_nueva_lista = ttk.Button(self.frame_botones_listas, text="Nueva lista")
        self.boton_nueva_lista.pack(pady=5)
        self.boton_eliminar_lista = ttk.Button(self.frame_botones_listas, text="Eliminar lista")
        self.boton_eliminar_lista.pack(pady=5)
        self.boton_modificar_lista = ttk.Button(self.frame_botones_listas, text="Modificar lista")
        self.boton_modificar_lista.pack(pady=5)
        self.boton_seleccionar_carpeta = ttk.Button(self.frame_derecho, text="Seleccionar carpeta")
        self.boton_seleccionar_carpeta.pack(pady=10)

    def actualizar_cancion(self, cancion):
        self.titulo.config(text=cancion.titulo)
        self.artista.config(text=cancion.artista)
        self.album.config(text=f"Álbum: {cancion.album}")
        self.año.config(text=f"Año: {cancion.año}")
        self.numero_pista.config(text=f"Pista: {cancion.numero_pista}")
        self.duracion.config(text=f"Duración: {int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}")
        self.tiempo_total.config(text=f"{int(cancion.duracion // 60)}:{int(cancion.duracion % 60):02d}")
        if cancion.caratula:
            image = cancion.caratula.resize((300, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.caratula.config(image=photo)
            self.caratula.image = photo
        else:
            self.caratula.config(image="")
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
        self.barra_progreso["value"] = valor * 100
        minutos, segundos = divmod(int(tiempo_actual), 60)
        self.tiempo_actual.config(text=f"{minutos}:{segundos:02d}")

    def actualizar_boton_reproducir_pausar(self, reproduciendo, pausado):
        if reproduciendo and not pausado:
            self.boton_reproducir_pausar.config(text="⏸")
        else:
            self.boton_reproducir_pausar.config(text="▶")

    def actualizar_boton_aleatorio(self, activo):
        self.boton_aleatorio.config(text="🔀" if activo else "🔀")

    def actualizar_boton_repetir(self, activo):
        self.boton_repetir.config(text="🔁" if activo else "🔁")

    def actualizar_boton_favorito(self, activo):
        self.boton_favorito.config(text="★" if activo else "☆")

    def actualizar_boton_me_gusta(self, activo):
        self.boton_me_gusta.config(text="👍" if activo else "👍")

    def seleccionar_directorio(self):
        return filedialog.askdirectory()

    def mostrar_dialogo_nueva_lista(self):
        return simpledialog.askstring("Nueva lista", "Nombre de la lista:")

    def mostrar_dialogo_modificar_lista(self, nombre_actual):
        return simpledialog.askstring("Modificar lista", "Nuevo nombre de la lista:", initialvalue=nombre_actual)

    def actualizar_icono_volumen(self, volumen):
        if volumen == 0:
            self.boton_mute.config(text="🔇")
        elif volumen < 0.5:
            self.boton_mute.config(text="🔉")
        else:
            self.boton_mute.config(text="🔊")

    def mostrar_cola(self, cola):
        ventana_cola = tk.Toplevel(self.root)
        ventana_cola.title("Cola de reproducción")
        ventana_cola.geometry("400x300")
        ventana_cola.configure(bg="#1E1E1E")
        lista_cola = tk.Listbox(ventana_cola, bg="#2E2E2E", fg="#FFFFFF", selectbackground="#6200EE")
        lista_cola.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for cancion in cola:
            lista_cola.insert(tk.END, f"{cancion.titulo} - {cancion.artista}")
