import tkinter as tk
from ui import AplicacionDescargador

def main():
    """Función principal de la aplicación."""
    root = tk.Tk()
    app = AplicacionDescargador(root)
    root.mainloop()

if __name__ == "__main__":
    main()