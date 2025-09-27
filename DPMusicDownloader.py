import yt_dlp

def descargar(url, carpeta_salida, formato, ffmpeg_path, progress_hook=None):
    if formato == "mp3":
        opciones = {
            'format': 'bestaudio/best',
            'outtmpl': f'{carpeta_salida}/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:  # mp4
        opciones = {
            # descarga mejor video y mejor audio y los combina
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{carpeta_salida}/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
            # asegura que ffmpeg una los streams
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

    if progress_hook:
        opciones['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])
