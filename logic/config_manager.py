import os
import json

CONFIG_FILE = "config.json"

def cargar_config():
    """Carga la configuración desde el archivo JSON."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "carpeta_descargas": os.path.join(os.getcwd(), "descargas"),
        "formato": "mp3",
        "ffmpeg_path": r"C:\Users\danie\OneDrive\Documentos\ffmpeg\ffmpeg-8.0-essentials_build\bin"
    }

def guardar_config(config):
    """Guarda la configuración en el archivo JSON."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def actualizar_config(config, **kwargs):
    """Actualiza la configuración con nuevos valores."""
    for key, value in kwargs.items():
        if key in config:
            config[key] = value
    guardar_config(config)
    return config