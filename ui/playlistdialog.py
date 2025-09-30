import tkinter as tk
from tkinter import messagebox, ttk

class DialogoSeleccionPlaylist:
    """Diálogo para seleccionar videos de una playlist."""
    
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
        
        self.configurarUi(playlist_info)
        
    def configurarUi(self, playlist_info):
        """Configura la interfaz del diálogo."""
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
                  command=self.seleccionarTodo).pack(side="left", padx=5)
        ttk.Button(quick_frame, text="❌ Deseleccionar Todo", 
                  command=self.deseleccionarTodo).pack(side="left", padx=5)
        
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
                'duracion': duracion_str,
                'seleccionado': False
            })
        
        # Bind para manejar clicks
        self.video_listbox.bind('<Button-1>', self.alHacerClick)
        
        # Frame para botones de confirmación
        button_frame = tk.Frame(main_frame, bg="#2C3E50")
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="⬇️ Descargar Seleccionados", 
                  command=self.descargarSeleccionados).pack(side="left", padx=10)
        ttk.Button(button_frame, text="⬇️ Descargar Toda la Playlist", 
                  command=self.descargarTodo).pack(side="left", padx=10)
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.cancelar).pack(side="right", padx=10)
        
    def alHacerClick(self, event):
        """Maneja el click en un elemento de la lista"""
        index = self.video_listbox.nearest(event.y)
        if index < len(self.video_data):
            # Toggle selección
            self.video_data[index]['seleccionado'] = not self.video_data[index]['seleccionado']
            
            # Actualizar visualización
            video = self.video_data[index]
            checkbox = "☑" if video['seleccionado'] else "☐"
            duracion_str = video.get('duracion', '')
            texto = f"{checkbox} {video['indice']}. {video['titulo']}{duracion_str}"
            
            self.video_listbox.delete(index)
            self.video_listbox.insert(index, texto)
    
    def seleccionarTodo(self):
        """Selecciona todos los videos"""
        for i, video in enumerate(self.video_data):
            video['seleccionado'] = True
            duracion_str = video.get('duracion', '')
            texto = f"☑ {video['indice']}. {video['titulo']}{duracion_str}"
            self.video_listbox.delete(i)
            self.video_listbox.insert(i, texto)
    
    def deseleccionarTodo(self):
        """Deselecciona todos los videos"""
        for i, video in enumerate(self.video_data):
            video['seleccionado'] = False
            duracion_str = video.get('duracion', '')
            texto = f"☐ {video['indice']}. {video['titulo']}{duracion_str}"
            self.video_listbox.delete(i)
            self.video_listbox.insert(i, texto)
    
    def descargarSeleccionados(self):
        """Descarga solo los videos seleccionados"""
        seleccionados = [v['indice'] for v in self.video_data if v['seleccionado']]
        if not seleccionados:
            messagebox.showwarning("⚠️ Atención", "No has seleccionado ningún video.")
            return
        
        self.indices_seleccionados = seleccionados
        self.result = "selected"
        self.dialog.destroy()
    
    def descargarTodo(self):
        """Descarga toda la playlist"""
        self.result = "all"
        self.dialog.destroy()
    
    def cancelar(self):
        """Cancela la operación"""
        self.result = "cancel"
        self.dialog.destroy()