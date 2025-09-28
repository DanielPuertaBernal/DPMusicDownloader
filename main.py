"""
DPMusicDownloader - Aplicación principal
Descargador de música y videos de YouTube con interfaz gráfica.
"""
import tkinter as tk
from ui import DownloaderApp

def main():
    """Función principal de la aplicación."""
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()