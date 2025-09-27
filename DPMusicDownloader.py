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
    else:  # mp4 con audio garantizado
        opciones = {
            # baja mejor video y mejor audio
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
            'merge_output_format': 'mp4',
            'outtmpl': f'{carpeta_salida}/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [
                {   # convierte el audio si está en opus → AAC dentro del mp4
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }
            ],
        }

    if progress_hook:
        opciones['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])
