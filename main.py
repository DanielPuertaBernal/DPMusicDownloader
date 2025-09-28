import tkinter as tk
from ui import DownloaderApp

def main():
    """Función principal de la aplicación."""
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()