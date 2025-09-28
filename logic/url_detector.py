def es_url_radio_o_mix(url):
    """Detecta si es una URL de radio o mix de YouTube Music"""
    radio_indicators = [
        'start_radio=1',
        'radio',
        'RD',  # Radio prefix en las playlist IDs
        'mix',
        'shuffle=1'
    ]
    return any(indicator in url.lower() for indicator in radio_indicators)

def es_url_valida(url):
    """Verifica si la URL es válida de YouTube."""
    youtube_domains = [
        'youtube.com',
        'youtu.be',
        'music.youtube.com',
        'm.youtube.com'
    ]
    return any(domain in url.lower() for domain in youtube_domains)

def obtener_tipo_contenido(url):
    """Determina el tipo de contenido de la URL."""
    if not es_url_valida(url):
        return "invalid"
    
    if es_url_radio_o_mix(url):
        return "radio_mix"
    
    if 'list=' in url or 'playlist' in url.lower():
        return "playlist"
    
    return "video"