import yt_dlp
from .urldetector import esUrlRadioOMix

def EsPlaylist(url):
    """Detecta si la URL es una playlist de YouTube"""
    try:
        # Si es una URL de radio/mix, preguntar al usuario pero con timeout más corto
        if esUrlRadioOMix(url):
            print("Detectada URL de radio/mix de YouTube Music")
        
        # Primero verificar si la URL contiene parámetros de playlist
        if 'list=' in url or 'playlist' in url.lower():
            # Extraer el ID de la playlist de la URL
            playlist_id = None
            if 'list=' in url:
                import re
                match = re.search(r'list=([^&]+)', url)
                if match:
                    playlist_id = match.group(1)
            
            # Si tenemos ID de playlist, construir URL directa de playlist
            if playlist_id:
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                
                # Configuración para extraer playlist directamente
                opciones = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'socket_timeout': 15,
                    'retries': 0,
                    'ignoreerrors': True,
                }
                
                # Para URLs de radio, usar timeout aún más agresivo
                if esUrlRadioOMix(url):
                    opciones['socket_timeout'] = 10
                    opciones['playlistend'] = 20
                
                with yt_dlp.YoutubeDL(opciones) as ydl:
                    info = ydl.extract_info(playlist_url, download=False)
                    
                    # Si es tipo playlist O tiene entries
                    if info and (info.get('_type') == 'playlist' or info.get('entries')):
                        entries = info.get('entries', [])
                        # Filtrar entradas válidas
                        valid_entries = [e for e in entries if e is not None]
                        # Solo considerar playlist si tiene más de 1 video
                        return len(valid_entries) > 1
                    return False
            
            # Si no pudimos extraer ID, usar método original
            opciones = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 15,
                'retries': 0,
                'ignoreerrors': True,
                'yes_playlist': True,
            }
            
            if esUrlRadioOMix(url):
                opciones['socket_timeout'] = 10
                opciones['playlistend'] = 20
            
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info and (info.get('_type') == 'playlist' or info.get('entries')):
                    entries = info.get('entries', [])
                    valid_entries = [e for e in entries if e is not None]
                    return len(valid_entries) > 1
                return False
        else:
            # Si no tiene parámetros de playlist, es un video individual
            return False
    except Exception as e:
        print(f"Error verificando playlist (tratando como video individual): {e}")
        return False

def ObtenerInfoPlaylist(url):
    """Obtiene información de la playlist (títulos y URLs de videos)"""
    try:
        # Extraer el ID de la playlist de la URL
        playlist_id = None
        if 'list=' in url:
            import re
            match = re.search(r'list=([^&]+)', url)
            if match:
                playlist_id = match.group(1)
        
        # URL a usar para extracción
        url_a_usar = url
        if playlist_id:
            url_a_usar = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        # Configuración base
        opciones = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'socket_timeout': 15,
            'retries': 0,
            'ignoreerrors': True,
            'playlistend': 30,
        }
        
        # Para URLs de radio/mix, configuración más restrictiva
        if esUrlRadioOMix(url):
            opciones.update({
                'socket_timeout': 10,
                'playlistend': 15,  # Solo primeros 15 para radios
            })
        
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url_a_usar, download=False)
            
            # Buscar playlist info - puede estar en diferentes lugares
            if info and (info.get('_type') == 'playlist' or info.get('entries')):
                entries = info.get('entries', [])
                
                # Filtrar entradas válidas
                valid_entries = [entry for entry in entries if entry is not None and entry.get('title')]
                
                if len(valid_entries) <= 1:
                    return None  # No es realmente una playlist
                
                # Para radios, usar título más descriptivo
                titulo_playlist = info.get('title', 'Playlist sin título')
                if esUrlRadioOMix(url):
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