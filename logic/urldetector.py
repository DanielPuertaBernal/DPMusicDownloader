def esUrlRadioOMix(url):
    """Detecta si es una URL de radio o mix de YouTube Music"""
    radio_indicators = [
        'start_radio=1',
        'radio',
        'RD',  # Radio prefix en las playlist IDs
        'mix',
        'shuffle=1'
    ]
    return any(indicator in url.lower() for indicator in radio_indicators)

def esUrlValida(url):
    """Verifica si la URL es válida de YouTube."""
    youtube_domains = [
        'youtube.com',
        'youtu.be',
        'music.youtube.com',
        'm.youtube.com'
    ]
    return any(domain in url.lower() for domain in youtube_domains)

def obtenerTipoContenido(url):
    """Determina el tipo de contenido de la URL."""
    if not esUrlValida(url):
        return "invalid"
    
    if esUrlRadioOMix(url):
        return "radio_mix"
    
    if 'list=' in url or 'playlist' in url.lower():
        return "playlist"
    
    return "video"