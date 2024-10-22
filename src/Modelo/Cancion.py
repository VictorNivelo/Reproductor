from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen import File
from PIL import Image
import os
import io


class Cancion:
    EXTENSIONES_SOPORTADAS = {".mp3": MP3, ".flac": FLAC, ".ogg": OggVorbis, ".wav": WAVE}

    def __init__(self, ruta):
        self.ruta = ruta
        self.extension = os.path.splitext(ruta)[1].lower()
        self.audio = self._cargar_audio()
        self.titulo = self._obtener_metadato("title")
        self.artista = self._obtener_metadato("artist")
        self.album = self._obtener_metadato("album")
        self.año = self._obtener_metadato("date")
        self.numero_pista = self._obtener_metadato("tracknumber")
        self.duracion = self._obtener_duracion()
        self.caratula = self._obtener_caratula()

    def _cargar_audio(self):
        if self.extension in self.EXTENSIONES_SOPORTADAS:
            return (
                self.EXTENSIONES_SOPORTADAS[self.extension](self.ruta, ID3=ID3)
                if self.extension == ".mp3"
                else self.EXTENSIONES_SOPORTADAS[self.extension](self.ruta)
            )
        return File(self.ruta)

    def _obtener_metadato(self, clave):
        try:
            if self.extension == ".mp3":
                return self._obtener_metadato_mp3(clave)
            return str(self.audio.get(clave, ["Desconocido"])[0])
        except:
            return "Desconocido"

    def _obtener_metadato_mp3(self, clave):
        metadatos_mp3 = {"title": "TIT2", "artist": "TPE1", "album": "TALB", "date": "TDRC", "tracknumber": "TRCK"}
        return str(self.audio.get(metadatos_mp3[clave], f"{clave.title()} Desconocido"))

    def _obtener_duracion(self):
        try:
            return self.audio.info.length
        except:
            return 0

    def _obtener_caratula(self):
        try:
            if self.extension == ".mp3":
                return Image.open(io.BytesIO(self.audio.get("APIC:").data))
            elif self.extension in [".flac", ".ogg"]:
                return Image.open(io.BytesIO(self.audio.pictures[0].data))
            return None
        except:
            return None

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "artista": self.artista,
            "album": self.album,
            "año": self.año,
            "numero_pista": self.numero_pista,
            "duracion": self.duracion,
            "ruta": self.ruta,
        }


class Biblioteca:
    EXTENSIONES_VALIDAS = (".mp3", ".flac", ".ogg", ".wav")

    def __init__(self):
        self.canciones = []
        self.directorio = ""

    def cargar_canciones(self, directorio):
        self.canciones.clear()
        for raiz, _, archivos in os.walk(directorio):
            for archivo in archivos:
                if archivo.endswith(self.EXTENSIONES_VALIDAS):
                    ruta_completa = os.path.join(raiz, archivo)
                    self.canciones.append(Cancion(ruta_completa))

    def obtener_canciones(self):
        return self.canciones

    def obtener_cancion_por_ruta(self, ruta):
        return next((cancion for cancion in self.canciones if cancion.ruta == ruta), None)
