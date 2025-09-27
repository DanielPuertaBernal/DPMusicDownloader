import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from DPMusicDownloader import descargar 

CONFIG_FILE = "config.json"

# ------------------------------
# Configuración
# ------------------------------
def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "carpeta_descargas": os.path.join(os.getcwd(), "descargas"),
        "formato": "mp3",
        "ffmpeg_path": r"C:\Users\danie\OneDrive\Documentos\ffmpeg\ffmpeg-8.0-essentials_build\bin"
    }

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# ------------------------------
# Interfaz gráfica
# ------------------------------
class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 DPMusicDownloader")
        self.root.geometry("600x350")
        self.root.configure(bg="#2C3E50")

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11), padding=6)
        style.configure("TLabel", background="#2C3E50", foreground="white", font=("Arial", 12))

        # Configuración
        self.config = cargar_config()
        self.url_var = tk.StringVar()
        self.formato_var = tk.StringVar(value=self.config["formato"])

        # Frame principal
        frame = tk.Frame(root, bg="#2C3E50")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Entrada URL
        ttk.Label(frame, text="Pega el link de YouTube:").pack(anchor="w")
        self.url_entry = ttk.Entry(frame, textvariable=self.url_var, width=70)
        self.url_entry.pack(pady=5)

        # Selección de formato
        formato_frame = tk.Frame(frame, bg="#2C3E50")
        formato_frame.pack(pady=5, anchor="w")
        ttk.Label(formato_frame, text="Formato:").pack(side="left")
        ttk.Radiobutton(formato_frame, text="MP3", variable=self.formato_var, value="mp3").pack(side="left", padx=5)
        ttk.Radiobutton(formato_frame, text="MP4", variable=self.formato_var, value="mp4").pack(side="left", padx=5)

        # Botones
        btn_frame = tk.Frame(frame, bg="#2C3E50")
        btn_frame.pack(pady=10)

        self.download_btn = ttk.Button(btn_frame, text="⬇️ Descargar", command=self.iniciar_descarga)
        self.download_btn.grid(row=0, column=0, padx=10)

        self.config_btn = ttk.Button(btn_frame, text="⚙️ Configurar carpeta", command=self.configurar_carpeta)
        self.config_btn.grid(row=0, column=1, padx=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=400)
        self.progress.pack(pady=15)

        # Log
        self.log_text = tk.Text(frame, height=6, bg="#34495E", fg="white", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def bloquear_ui(self, estado=True):
        if estado:
            self.download_btn.config(state="disabled")
            self.config_btn.config(state="disabled")
            self.url_entry.config(state="disabled")
            self.progress.start()
        else:
            self.download_btn.config(state="normal")
            self.config_btn.config(state="normal")
            self.url_entry.config(state="normal")
            self.progress.stop()

    def iniciar_descarga(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("⚠️ Atención", "Por favor, ingresa una URL.")
            return

        self.config["formato"] = self.formato_var.get()
        guardar_config(self.config)

        self.log(f"🔗 Iniciando descarga de: {url}")
        self.bloquear_ui(True)

        def worker():
            try:
                descargar(url, self.config["carpeta_descargas"], self.config["formato"], self.config["ffmpeg_path"])
                self.finalizar_descarga(True, "✅ Descarga completada.")
            except Exception as e:
                self.finalizar_descarga(False, f"❌ Error: {str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def finalizar_descarga(self, success, msg):
        self.root.after(0, lambda: [
            self.log(msg),
            self.bloquear_ui(False),
            messagebox.showinfo("Resultado", msg) if success else messagebox.showerror("Error", msg)
        ])

    def configurar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de descargas")
        if carpeta:
            self.config["carpeta_descargas"] = carpeta
            guardar_config(self.config)
            self.log(f"📂 Carpeta de descarga configurada: {carpeta}")

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
