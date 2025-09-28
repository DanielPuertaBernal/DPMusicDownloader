"""
Módulo de lógica para DPMusicDownloader.
"""

from .config_manager import cargar_config, guardar_config, actualizar_config
from .url_detector import es_url_radio_o_mix, es_url_valida, obtener_tipo_contenido
from .playlist_manager import es_playlist, obtener_info_playlist
from .download_manager import DownloadManager, descargar

__all__ = [
    'cargar_config',
    'guardar_config', 
    'actualizar_config',
    'es_url_radio_o_mix',
    'es_url_valida',
    'obtener_tipo_contenido',
    'es_playlist',
    'obtener_info_playlist',
    'DownloadManager',
    'descargar'
]