import yt_dlp
from .urldetector import esUrlRadioOMix

def EsPlaylist(url):
    """Detecta si la URL es una playlist de YouTube"""
    try:
        # Si es una URL de radio/mix, verificar si realmente tiene contenido
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
            
            # Casos especiales de radio - verificar si tienen contenido extraíble
            radio_especiales = ['RDMM', 'RDCLAK', 'RDQM', 'RDEM', 'RDAMVM', 'RDTMAK']
            if playlist_id and any(playlist_id.startswith(radio) for radio in radio_especiales):
                print(f"Radio especial detectado: {playlist_id} - verificando contenido...")
                # Para radios especiales, intentar extraer contenido primero
                try:
                    opciones_verificacion = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': True,
                        'socket_timeout': 15,
                        'retries': 0,
                        'ignoreerrors': True,
                        'playlistend': 5,  # Solo verificar los primeros 5
                    }
                    
                    with yt_dlp.YoutubeDL(opciones_verificacion) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info and info.get('entries'):
                            entries = [e for e in info.get('entries', []) if e is not None]
                            if len(entries) > 1:
                                print(f"Radio {playlist_id} tiene {len(entries)} elementos - tratando como playlist")
                                return True
                            else:
                                print(f"Radio {playlist_id} tiene pocos elementos - tratando como video individual")
                                return True  # Aún considerarlo playlist para mostrar diálogo
                except:
                    print(f"No se pudo verificar contenido del radio {playlist_id} - tratando como playlist")
                    return True  # En caso de error, asumir que es playlist
            
            # Si tenemos ID de playlist normal, construir URL directa de playlist
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
        
        # Casos especiales de radio - intentar extraer primero, si falla entonces tratar especial
        radio_especiales = ['RDMM', 'RDCLAK', 'RDQM', 'RDEM', 'RDAMVM', 'RDTMAK']
        es_radio_especial = playlist_id and any(playlist_id.startswith(radio) for radio in radio_especiales)
        
        if es_radio_especial:
            print(f"Radio especial detectado: {playlist_id} - intentando extraer contenido...")
        
        # URL a usar para extracción
        url_a_usar = url
        if playlist_id:
            # Para radios especiales, usar la URL original que puede tener más información
            if es_radio_especial:
                url_a_usar = url  # Mantener URL original para radios
            else:
                url_a_usar = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        # Configuración base
        opciones = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'socket_timeout': 20,  # Aumentar timeout para radios
            'retries': 1,  # Permitir 1 reintento
            'ignoreerrors': True,
            'playlistend': 50,  # Más videos para radios
        }
        
        # Para URLs de radio/mix, configuración más específica
        if esUrlRadioOMix(url):
            opciones.update({
                'socket_timeout': 25,  # Más tiempo para radios
                'playlistend': 25,     # Limitar para evitar demasiados videos
            })
        
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url_a_usar, download=False)
            
            # Buscar playlist info - puede estar en diferentes lugares
            if info and (info.get('_type') == 'playlist' or info.get('entries')):
                entries = info.get('entries', [])
                
                # Filtrar entradas válidas
                valid_entries = [entry for entry in entries if entry is not None and entry.get('title')]
                
                if len(valid_entries) <= 1:
                    # Si solo tiene 1 video o menos, crear respuesta especial para radios
                    if es_radio_especial:
                        return {
                            'titulo': f"🔀 Radio YouTube Music - {playlist_id}",
                            'total_videos': 1,
                            'videos': [{
                                'indice': 1,
                                'titulo': f"📻 Radio basado en esta canción (descarga video actual)",
                                'url': url,
                                'duracion': 0
                            }]
                        }
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
                # Si no se pudo extraer como playlist, manejar como caso especial
                if es_radio_especial:
                    print(f"No se pudo extraer contenido del radio {playlist_id}, tratando como video individual")
                    return {
                        'titulo': f"🔀 Radio YouTube Music - {playlist_id}",
                        'total_videos': 1,
                        'videos': [{
                            'indice': 1,
                            'titulo': f"📻 Radio basado en esta canción (descarga video actual)",
                            'url': url,
                            'duracion': 0
                        }]
                    }
                return None
    except Exception as e:
        print(f"Error al obtener info de playlist: {e}")
        return None