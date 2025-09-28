"""
Ventana principal de la aplicación DPMusicDownloader.
"""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from logic import (cargar_config, guardar_config, es_playlist, obtener_info_playlist, 
                   es_url_radio_o_mix, descargar)
from .playlist_dialog import PlaylistSelectionDialog

class DownloaderApp:
    """Aplicación principal del descargador."""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._setup_styles()
        
        # Configuración
        self.config = cargar_config()
        self.url_var = tk.StringVar()
        self.formato_var = tk.StringVar(value=self.config["formato"])
        
        self._create_widgets()
        
    def _setup_window(self):
        """Configura la ventana principal."""
        self.root.title("🎵 DPMusicDownloader")
        self.root.geometry("600x250")  # Reducido sin los logs
        self.root.configure(bg="#2C3E50")
        
    def _setup_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11), padding=6)
        style.configure("TLabel", background="#2C3E50", foreground="white", font=("Arial", 12))
        
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal
        frame = tk.Frame(self.root, bg="#2C3E50")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        self._create_url_section(frame)
        self._create_format_section(frame)
        self._create_buttons_section(frame)
        self._create_progress_section(frame)
        
    def _create_url_section(self, parent):
        """Crea la sección de entrada de URL."""
        ttk.Label(parent, text="Pega el link de YouTube:").pack(anchor="w")
        self.url_entry = ttk.Entry(parent, textvariable=self.url_var, width=70)
        self.url_entry.pack(pady=5)
        
    def _create_format_section(self, parent):
        """Crea la sección de selección de formato."""
        formato_frame = tk.Frame(parent, bg="#2C3E50")
        formato_frame.pack(pady=5, anchor="w")
        
        ttk.Label(formato_frame, text="Formato:").pack(side="left")
        ttk.Radiobutton(formato_frame, text="MP3", 
                       variable=self.formato_var, value="mp3").pack(side="left", padx=5)
        ttk.Radiobutton(formato_frame, text="MP4", 
                       variable=self.formato_var, value="mp4").pack(side="left", padx=5)
        
    def _create_buttons_section(self, parent):
        """Crea la sección de botones."""
        btn_frame = tk.Frame(parent, bg="#2C3E50")
        btn_frame.pack(pady=10)
        
        self.download_btn = ttk.Button(btn_frame, text="⬇️ Descargar", 
                                      command=self.iniciar_descarga)
        self.download_btn.grid(row=0, column=0, padx=10)
        
        self.config_btn = ttk.Button(btn_frame, text="⚙️ Configurar carpeta", 
                                    command=self.configurar_carpeta)
        self.config_btn.grid(row=0, column=1, padx=10)
        
    def _create_progress_section(self, parent):
        """Crea la sección de progreso."""
        # Barra de progreso
        self.progress = ttk.Progressbar(parent, mode="indeterminate", length=400)
        self.progress.pack(pady=15)
        
        # Etiqueta de estado
        self.status_label = tk.Label(parent, text="Listo para descargar", 
                                    bg="#2C3E50", fg="#BDC3C7", 
                                    font=("Arial", 10))
        self.status_label.pack(pady=5)
        
    def update_status(self, msg):
        """Actualiza el mensaje de estado."""
        self.status_label.config(text=msg)
        
    def bloquear_ui(self, estado=True):
        """Bloquea/desbloquea la interfaz durante operaciones."""
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
        """Inicia el proceso de descarga."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("⚠️ Atención", "Por favor, ingresa una URL.")
            return
            
        self.config["formato"] = self.formato_var.get()
        guardar_config(self.config)
        
        # Verificar si es una playlist
        self.update_status("🔍 Verificando tipo de contenido...")
        self.bloquear_ui(True)
        
        def verificar_playlist():
            try:
                import time
                
                timeout_seconds = 30
                start_time = time.time()
                
                # Verificar si es URL de radio y avisar
                if es_url_radio_o_mix(url):
                    self.root.after(0, lambda: self.update_status("🔀 URL de radio/mix detectada, verificando..."))
                
                if es_playlist(url):
                    # Es una playlist, obtener información
                    if es_url_radio_o_mix(url):
                        self.root.after(0, lambda: self.update_status("📻 Radio/Mix confirmado, obteniendo canciones..."))
                    else:
                        self.root.after(0, lambda: self.update_status("📋 Playlist detectada, obteniendo información..."))
                    
                    # Verificar si no ha pasado demasiado tiempo
                    if time.time() - start_time > timeout_seconds:
                        raise TimeoutError("Timeout obteniendo información de playlist")
                    
                    playlist_info = obtener_info_playlist(url)
                    
                    if playlist_info and playlist_info['total_videos'] > 1:
                        self.root.after(0, lambda: self.mostrar_dialogo_playlist(url, playlist_info))
                    else:
                        # Si no es una playlist válida o tiene solo 1 video, tratar como individual
                        self.root.after(0, lambda: self.update_status("🎵 Tratando como video individual..."))
                        self.root.after(0, lambda: self.descargar_individual(url))
                else:
                    # Es un video individual, proceder normalmente
                    self.root.after(0, lambda: self.update_status("🎵 Video individual detectado"))
                    self.root.after(0, lambda: self.descargar_individual(url))
                    
            except TimeoutError as e:
                if es_url_radio_o_mix(url):
                    self.root.after(0, lambda: self.update_status("⏱️ Timeout verificando radio/mix, descargando solo el primer video..."))
                else:
                    self.root.after(0, lambda: self.update_status("⏱️ Timeout verificando playlist, tratando como video individual..."))
                self.root.after(0, lambda: self.descargar_individual(url))
            except Exception as e:
                error_msg = str(e)
                if "playlist" in error_msg.lower() or "timeout" in error_msg.lower():
                    if es_url_radio_o_mix(url):
                        self.root.after(0, lambda: self.update_status("⚠️ Error verificando radio/mix, descargando como video individual..."))
                    else:
                        self.root.after(0, lambda: self.update_status("⚠️ Error verificando playlist, tratando como video individual..."))
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
            self.update_status(f"📋 Descargando playlist completa ({playlist_info['total_videos']} videos)")
            self.descargar_playlist(url, None)
        elif dialog.result == "selected":
            cantidad = len(dialog.indices_seleccionados)
            self.update_status(f"📋 Descargando {cantidad} videos seleccionados de la playlist")
            self.descargar_playlist(url, dialog.indices_seleccionados)
        else:  # cancel
            self.update_status("❌ Descarga cancelada por el usuario")
    
    def descargar_individual(self, url):
        """Descarga un video individual"""
        self.update_status(f"🔗 Iniciando descarga de video individual...")
        
        def worker():
            try:
                descargar(url, self.config["carpeta_descargas"], 
                         self.config["formato"], self.config["ffmpeg_path"])
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
        """Finaliza el proceso de descarga."""
        self.root.after(0, lambda: [
            self.update_status(msg),
            self.bloquear_ui(False),
            messagebox.showinfo("Resultado", msg) if success else messagebox.showerror("Error", msg)
        ])

    def configurar_carpeta(self):
        """Configura la carpeta de descarga."""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de descargas")
        if carpeta:
            self.config["carpeta_descargas"] = carpeta
            guardar_config(self.config)
            self.update_status(f"📂 Carpeta de descarga configurada: {carpeta}")