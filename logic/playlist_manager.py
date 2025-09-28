"""
Módulo para gestionar la información y procesamiento de playlists.
"""
import yt_dlp
from .url_detector import es_url_radio_o_mix

def es_playlist(url):
    """Detecta si la URL es una playlist de YouTube"""
    try:
        # Si es una URL de radio/mix, preguntar al usuario pero con timeout más corto
        if es_url_radio_o_mix(url):
            print("Detectada URL de radio/mix de YouTube Music")
        
        # Primero verificar si la URL contiene parámetros de playlist
        if 'list=' in url or 'playlist' in url.lower():
            # Configuración más específica para evitar que se cuelgue
            opciones = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # No extraer info completa, solo básica
                'socket_timeout': 15,  # Timeout más corto para radios
                'retries': 0,  # No reintentar si falla
                'ignoreerrors': True,  # Ignorar errores y continuar
            }
            
            # Para URLs de radio, usar timeout aún más agresivo
            if es_url_radio_o_mix(url):
                opciones['socket_timeout'] = 10
                opciones['playlistend'] = 20  # Limitar a primeros 20 para radios
            
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=False)
                # Verificar si es playlist y tiene múltiples entradas
                if info and info.get('_type') == 'playlist':
                    entries = info.get('entries', [])
                    # Filtrar entradas válidas
                    valid_entries = [e for e in entries if e is not None]
                    # Solo considerar playlist si tiene más de 1 video
                    return len(valid_entries) > 1
                return False
        else:
            # Si no tiene parámetros de playlist, es un video individual
            return False
    except Exception as e:
        print(f"Error verificando playlist (tratando como video individual): {e}")
        return False

def obtener_info_playlist(url):
    """Obtiene información de la playlist (títulos y URLs de videos)"""
    try:
        # Configuración base
        opciones = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Solo extrae metadatos básicos
            'socket_timeout': 15,  # Timeout base
            'retries': 0,  # No reintentar
            'ignoreerrors': True,  # Ignorar errores
            'playlistend': 30,  # Limitar videos por defecto
        }
        
        # Para URLs de radio/mix, configuración más restrictiva
        if es_url_radio_o_mix(url):
            opciones.update({
                'socket_timeout': 10,
                'playlistend': 15,  # Solo primeros 15 para radios
            })
        
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and info.get('_type') == 'playlist':
                entries = info.get('entries', [])
                
                # Filtrar entradas válidas
                valid_entries = [entry for entry in entries if entry is not None and entry.get('title')]
                
                if len(valid_entries) <= 1:
                    return None  # No es realmente una playlist
                
                # Para radios, usar título más descriptivo
                titulo_playlist = info.get('title', 'Playlist sin título')
                if es_url_radio_o_mix(url):
                    if 'radio' in titulo_playlist.lower() or 'mix' in titulo_playlist.lower():
                        titulo_playlist = f"🔀 {titulo_playlist}"
                    else:
                        titulo_playlist = f"🔀 Radio/Mix - {titulo_playlist}"
                
                playlist_info = {
                    'titulo': titulo_playlist,
                    'total_videos': len(valid_entries),
                    'videos': []
                }
                
                for i, entry in enumerate(valid_entries, 1):
                    video_info = {
                        'indice': i,
                        'titulo': entry.get('title', f'Video {i}'),
                        'url': entry.get('url', ''),
                        'duracion': entry.get('duration', 0)
                    }
                    playlist_info['videos'].append(video_info)
                
                return playlist_info
            else:
                return None
    except Exception as e:
        print(f"Error al obtener info de playlist: {e}")
        return None