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
        if self.extension == ".mp3":
            return MP3(self.ruta, ID3=ID3)
        elif self.extension == ".flac":
            return FLAC(self.ruta)
        elif self.extension == ".ogg":
            return OggVorbis(self.ruta)
        elif self.extension == ".wav":
            return WAVE(self.ruta)
        else:
            return File(self.ruta)

    def _obtener_metadato(self, clave):
        try:
            if self.extension == ".mp3":
                if clave == "title":
                    return str(self.audio.get("TIT2", "Título Desconocido"))
                elif clave == "artist":
                    return str(self.audio.get("TPE1", "Artista Desconocido"))
                elif clave == "album":
                    return str(self.audio.get("TALB", "Álbum Desconocido"))
                elif clave == "date":
                    return str(self.audio.get("TDRC", "Año Desconocido"))
                elif clave == "tracknumber":
                    return str(self.audio.get("TRCK", "Número de Pista Desconocido"))
            else:
                return str(self.audio.get(clave, ["Desconocido"])[0])
        except:
            return "Desconocido"

    def _obtener_duracion(self):
        try:
            return self.audio.info.length
        except:
            return 0

    def _obtener_caratula(self):
        try:
            if self.extension == ".mp3":
                pict = self.audio.get("APIC:").data
                return Image.open(io.BytesIO(pict))
            elif self.extension in [".flac", ".ogg"]:
                for picture in self.audio.pictures:
                    return Image.open(io.BytesIO(picture.data))
            else:
                return None
        except:
            return None


class Biblioteca:
    def __init__(self):
        self.canciones = []
        self.directorio = ""

    def cargar_canciones(self, directorio):
        self.canciones.clear()
        for raiz, dirs, archivos in os.walk(directorio):
            for archivo in archivos:
                if archivo.endswith((".mp3", ".flac", ".ogg", ".wav")):
                    ruta_completa = os.path.join(raiz, archivo)
                    self.canciones.append(Cancion(ruta_completa))

    def obtener_canciones(self):
        return self.canciones

    def obtener_cancion_por_ruta(self, ruta):
        for cancion in self.canciones:
            if cancion.ruta == ruta:
                return cancion
        return None
