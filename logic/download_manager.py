"""
Módulo principal para gestionar las descargas de YouTube.
"""
import yt_dlp
import os

class DownloadManager:
    """Gestor principal de descargas."""
    
    def __init__(self, ffmpeg_path):
        self.ffmpeg_path = ffmpeg_path
    
    def _get_base_options(self):
        """Obtiene las opciones base para yt-dlp."""
        return {
            'ffmpeg_location': self.ffmpeg_path,
        }
    
    def _get_mp3_options(self, output_path):
        """Obtiene opciones específicas para descargas MP3."""
        return {
            **self._get_base_options(),
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
    def _get_mp4_options(self, output_path):
        """Obtiene opciones específicas para descargas MP4."""
        return {
            **self._get_base_options(),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }
    
    def descargar(self, url, carpeta_salida, formato, progress_hook=None, indices_seleccionados=None):
        """
        Descarga contenido de YouTube.
        
        Args:
            url: URL del video o playlist
            carpeta_salida: Carpeta donde guardar las descargas
            formato: 'mp3' o 'mp4'
            progress_hook: Función callback para progreso
            indices_seleccionados: Lista de índices para playlists parciales
        """
        # Crear carpeta si no existe
        os.makedirs(carpeta_salida, exist_ok=True)
        
        # Configurar opciones según el formato
        if formato == "mp3":
            opciones = self._get_mp3_options(carpeta_salida)
        else:
            opciones = self._get_mp4_options(carpeta_salida)
        
        # Si hay índices seleccionados (playlist), configurar para descargar solo esos
        if indices_seleccionados:
            playlist_items = ','.join(map(str, indices_seleccionados))
            opciones['playlist_items'] = playlist_items
        
        # Agregar hook de progreso si se proporciona
        if progress_hook:
            opciones['progress_hooks'] = [progress_hook]
        
        # Realizar descarga
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
    
    def obtener_info_video(self, url):
        """Obtiene información básica de un video."""
        try:
            opciones = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'titulo': info.get('title', 'Sin título'),
                    'duracion': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Desconocido'),
                    'view_count': info.get('view_count', 0)
                }
        except Exception as e:
            print(f"Error obteniendo info del video: {e}")
            return None

# Función de compatibilidad con el código anterior
def descargar(url, carpeta_salida, formato, ffmpeg_path, progress_hook=None, indices_seleccionados=None):
    """Función de compatibilidad con la versión anterior."""
    manager = DownloadManager(ffmpeg_path)
    return manager.descargar(url, carpeta_salida, formato, progress_hook, indices_seleccionados)