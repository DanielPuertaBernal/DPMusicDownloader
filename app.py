import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from DPMusicDownloader import descargar, es_playlist, obtener_info_playlist, es_url_radio_o_mix 

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
# Diálogo de selección de playlist
# ------------------------------
class PlaylistSelectionDialog:
    def __init__(self, parent, playlist_info):
        self.result = None
        self.indices_seleccionados = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🎵 Playlist Detectada")
        self.dialog.geometry("650x500")
        self.dialog.configure(bg="#2C3E50")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()  # Hace el diálogo modal
        
        # Centrar el diálogo
        self.dialog.transient(parent)
        
        self.setup_ui(playlist_info)
        
    def setup_ui(self, playlist_info):
        main_frame = tk.Frame(self.dialog, bg="#2C3E50")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Título de la playlist
        title_label = tk.Label(main_frame, 
                              text=f"📋 {playlist_info['titulo']}", 
                              bg="#2C3E50", fg="white", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Info de la playlist
        info_label = tk.Label(main_frame, 
                             text=f"Total de videos: {playlist_info['total_videos']}", 
                             bg="#2C3E50", fg="#BDC3C7", 
                             font=("Arial", 10))
        info_label.pack(pady=(0, 15))
        
        # Frame para botones de acción rápida
        quick_frame = tk.Frame(main_frame, bg="#2C3E50")
        quick_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(quick_frame, text="✅ Seleccionar Todo", 
                  command=self.select_all).pack(side="left", padx=5)
        ttk.Button(quick_frame, text="❌ Deseleccionar Todo", 
                  command=self.deselect_all).pack(side="left", padx=5)
        
        # Frame con scroll para la lista de videos
        list_frame = tk.Frame(main_frame, bg="#2C3E50")
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox con checkboxes simulados
        self.video_listbox = tk.Listbox(list_frame, 
                                       bg="#34495E", fg="white",
                                       font=("Arial", 10),
                                       selectmode=tk.MULTIPLE,
                                       yscrollcommand=scrollbar.set)
        self.video_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Llenar la lista con los videos
        self.video_data = []
        for video in playlist_info['videos']:
            # Manejar duración como float o int
            duracion = video.get('duracion', 0)
            if duracion and isinstance(duracion, (int, float)) and duracion > 0:
                duracion_int = int(duracion)  # Convertir a entero
                minutos = duracion_int // 60
                segundos = duracion_int % 60
                duracion_str = f" ({minutos}:{segundos:02d})"
            else:
                duracion_str = ""
            
            texto = f"☐ {video['indice']}. {video['titulo']}{duracion_str}"
            self.video_listbox.insert(tk.END, texto)
            self.video_data.append({
                'indice': video['indice'],
                'titulo': video['titulo'],
                'duracion': duracion_str,  # Guardar la string formateada
                'seleccionado': False
            })
        
        # Bind para manejar clicks
        self.video_listbox.bind('<Button-1>', self.on_click)
        
        # Frame para botones de confirmación
        button_frame = tk.Frame(main_frame, bg="#2C3E50")
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="⬇️ Descargar Seleccionados", 
                  command=self.download_selected).pack(side="left", padx=10)
        ttk.Button(button_frame, text="⬇️ Descargar Toda la Playlist", 
                  command=self.download_all).pack(side="left", padx=10)
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.cancel).pack(side="right", padx=10)
        
    def on_click(self, event):
        """Maneja el click en un elemento de la lista"""
        index = self.video_listbox.nearest(event.y)
        if index < len(self.video_data):
            # Toggle selección
            self.video_data[index]['seleccionado'] = not self.video_data[index]['seleccionado']
            
            # Actualizar visualización
            video = self.video_data[index]
            checkbox = "☑" if video['seleccionado'] else "☐"
            duracion_str = video.get('duracion', '')  # Usar la duración ya formateada
            texto = f"{checkbox} {video['indice']}. {video['titulo']}{duracion_str}"
            
            self.video_listbox.delete(index)
            self.video_listbox.insert(index, texto)
    
    def select_all(self):
        """Selecciona todos los videos"""
        for i, video in enumerate(self.video_data):
            video['seleccionado'] = True
            duracion_str = video.get('duracion', '')
            texto = f"☑ {video['indice']}. {video['titulo']}{duracion_str}"
            self.video_listbox.delete(i)
            self.video_listbox.insert(i, texto)
    
    def deselect_all(self):
        """Deselecciona todos los videos"""
        for i, video in enumerate(self.video_data):
            video['seleccionado'] = False
            duracion_str = video.get('duracion', '')
            texto = f"☐ {video['indice']}. {video['titulo']}{duracion_str}"
            self.video_listbox.delete(i)
            self.video_listbox.insert(i, texto)
    
    def download_selected(self):
        """Descarga solo los videos seleccionados"""
        seleccionados = [v['indice'] for v in self.video_data if v['seleccionado']]
        if not seleccionados:
            messagebox.showwarning("⚠️ Atención", "No has seleccionado ningún video.")
            return
        
        self.indices_seleccionados = seleccionados
        self.result = "selected"
        self.dialog.destroy()
    
    def download_all(self):
        """Descarga toda la playlist"""
        self.result = "all"
        self.dialog.destroy()
    
    def cancel(self):
        """Cancela la operación"""
        self.result = "cancel"
        self.dialog.destroy()

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

        # Verificar si es una playlist
        self.log("🔍 Verificando tipo de contenido...")
        self.bloquear_ui(True)
        
        def verificar_playlist():
            try:
                # Verificación con timeout más agresivo
                import time
                
                timeout_seconds = 30  # Reducido para URLs de radio
                
                start_time = time.time()
                
                # Verificar si es URL de radio y avisar
                if es_url_radio_o_mix(url):
                    self.root.after(0, lambda: self.log("🔀 URL de radio/mix detectada, verificando..."))
                
                if es_playlist(url):
                    # Es una playlist, obtener información
                    if es_url_radio_o_mix(url):
                        self.root.after(0, lambda: self.log("📻 Radio/Mix confirmado, obteniendo canciones..."))
                    else:
                        self.root.after(0, lambda: self.log("📋 Playlist detectada, obteniendo información..."))
                    
                    # Verificar si no ha pasado demasiado tiempo
                    if time.time() - start_time > timeout_seconds:
                        raise TimeoutError("Timeout obteniendo información de playlist")
                    
                    playlist_info = obtener_info_playlist(url)
                    
                    if playlist_info and playlist_info['total_videos'] > 1:
                        self.root.after(0, lambda: self.mostrar_dialogo_playlist(url, playlist_info))
                    else:
                        # Si no es una playlist válida o tiene solo 1 video, tratar como individual
                        self.root.after(0, lambda: self.log("🎵 Tratando como video individual..."))
                        self.root.after(0, lambda: self.descargar_individual(url))
                else:
                    # Es un video individual, proceder normalmente
                    self.root.after(0, lambda: self.log("🎵 Video individual detectado"))
                    self.root.after(0, lambda: self.descargar_individual(url))
                    
            except TimeoutError as e:
                if es_url_radio_o_mix(url):
                    self.root.after(0, lambda: self.log("⏱️ Timeout verificando radio/mix, descargando solo el primer video..."))
                else:
                    self.root.after(0, lambda: self.log("⏱️ Timeout verificando playlist, tratando como video individual..."))
                self.root.after(0, lambda: self.descargar_individual(url))
            except Exception as e:
                error_msg = str(e)
                if "playlist" in error_msg.lower() or "timeout" in error_msg.lower():
                    if es_url_radio_o_mix(url):
                        self.root.after(0, lambda: self.log("⚠️ Error verificando radio/mix, descargando como video individual..."))
                    else:
                        self.root.after(0, lambda: self.log("⚠️ Error verificando playlist, tratando como video individual..."))
                    self.root.after(0, lambda: self.descargar_individual(url))
                else:
                    self.finalizar_descarga(False, f"❌ Error al verificar contenido: {error_msg}")
        
        threading.Thread(target=verificar_playlist, daemon=True).start()
    
    def mostrar_dialogo_playlist(self, url, playlist_info):
        """Muestra el diálogo de selección de playlist"""
        self.bloquear_ui(False)  # Desbloquear para permitir interacción con el diálogo
        
        dialog = PlaylistSelectionDialog(self.root, playlist_info)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result == "all":
            self.log(f"📋 Descargando playlist completa ({playlist_info['total_videos']} videos)")
            self.descargar_playlist(url, None)
        elif dialog.result == "selected":
            cantidad = len(dialog.indices_seleccionados)
            self.log(f"📋 Descargando {cantidad} videos seleccionados de la playlist")
            self.descargar_playlist(url, dialog.indices_seleccionados)
        else:  # cancel
            self.log("❌ Descarga cancelada por el usuario")
    
    def descargar_individual(self, url):
        """Descarga un video individual"""
        self.log(f"🔗 Iniciando descarga de video individual: {url}")
        
        def worker():
            try:
                descargar(url, self.config["carpeta_descargas"], self.config["formato"], self.config["ffmpeg_path"])
                self.finalizar_descarga(True, "✅ Descarga completada.")
            except Exception as e:
                self.finalizar_descarga(False, f"❌ Error: {str(e)}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def descargar_playlist(self, url, indices_seleccionados):
        """Descarga una playlist (completa o videos seleccionados)"""
        self.bloquear_ui(True)
        
        def worker():
            try:
                descargar(url, self.config["carpeta_descargas"], self.config["formato"], 
                         self.config["ffmpeg_path"], indices_seleccionados=indices_seleccionados)
                
                if indices_seleccionados:
                    self.finalizar_descarga(True, f"✅ Descarga completada: {len(indices_seleccionados)} videos.")
                else:
                    self.finalizar_descarga(True, "✅ Descarga de playlist completada.")
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
