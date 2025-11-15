import yt_dlp
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import os

class YouTubeToMP3App:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixador de YouTube para MP3")
        self.root.geometry("700x600")
        self.style = ttk.Style("darkly") 
        
        # Variáveis
        self.output_dir = ttk.StringVar(value="downloads")
        self.urls = []
        self.is_downloading = False
        self.current_download_index = 0
        self.total_downloads = 0
        self.progress_bars = {}  # Dicionário para barras de progresso individuais
        
        # Interface
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        ttk.Label(
            main_frame, 
            text="Baixador de YouTube para MP3", 
            font=("Helvetica", 18, "bold"), 
            bootstyle="light"
        ).pack(pady=10)
        
        # Campo de texto para URLs
        ttk.Label(
            main_frame, 
            text="Cole os URLs do YouTube (um por linha) ou carregue um arquivo txt:", 
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(10, 5))
        self.url_text = ttk.Text(main_frame, height=6, width=60, font=("Helvetica", 10))
        self.url_text.pack(fill=X, pady=5)
        
        # Botão para carregar arquivo
        ttk.Button(
            main_frame, 
            text="Carregar Arquivo de URLs", 
            command=self.load_url_file, 
            bootstyle="primary-outline", 
            width=20
        ).pack(anchor="w", pady=5)
        
        # Seleção do diretório de saída
        ttk.Label(main_frame, text="Diretório de Saída:", font=("Helvetica", 10)).pack(anchor="w", pady=(10, 5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=X)
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=50, font=("Helvetica", 10)).pack(side=LEFT, fill=X)
        ttk.Button(
            dir_frame, 
            text="Selecionar", 
            command=self.choose_output_dir, 
            bootstyle="secondary-outline", 
            width=12
        ).pack(side=LEFT, padx=5)
        
        # Barra de progresso geral
        ttk.Label(main_frame, text="Progresso Total:", font=("Helvetica", 10)).pack(anchor="w", pady=(10, 5))
        self.total_progress = ttk.Progressbar(main_frame, mode="determinate", bootstyle="success")
        self.total_progress.pack(fill=X, pady=5)
        
        # Frame para barras de progresso individuais
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Botão de download
        self.download_button = ttk.Button(
            main_frame, 
            text="Baixar MP3s", 
            command=self.start_download, 
            bootstyle="success", 
            width=20
        )
        self.download_button.pack(pady=10)
        
        # Área de log
        ttk.Label(main_frame, text="Log de Progresso:", font=("Helvetica", 10)).pack(anchor="w")
        self.log_text = ttk.Text(main_frame, height=8, width=60, font=("Helvetica", 10), state="disabled")
        self.log_text.pack(fill=BOTH, expand=True, pady=5)
        scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)
        self.log_text.config(state="disabled")
        self.root.update()
    
    def load_url_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    urls = [line.strip() for line in file if line.strip()]
                    self.url_text.delete("1.0", END)
                    self.url_text.insert(END, "\n".join(urls))
                    self.log(f"Carregados {len(urls)} URLs de {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")
    
    def choose_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
            self.log(f"Diretório de saída selecionado: {dir_path}")
    
    def validate_urls(self, urls):
        return [url for url in urls if url.startswith(('https://www.youtube.com', 'https://youtu.be'))]
    
    def create_progress_bar(self, url, index):
        # Cria um frame para cada barra de progresso
        frame = ttk.Frame(self.progress_frame)
        frame.pack(fill=X, pady=2)
        ttk.Label(frame, text=f"Música {index + 1}: {url[:30]}...", font=("Helvetica", 9)).pack(side=LEFT)
        progress = ttk.Progressbar(frame, mode="determinate", bootstyle="info")
        progress.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.progress_bars[url] = progress
    
    def update_progress(self, url, percent):
        if url in self.progress_bars:
            self.progress_bars[url]["value"] = percent
            self.root.update()
        # Atualiza progresso geral
        if self.total_downloads > 0:
            completed = self.current_download_index + (percent / 100)
            total_percent = (completed / self.total_downloads) * 100
            self.total_progress["value"] = total_percent
            self.root.update()
    
    def download_youtube_mp3(self, urls, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for index, url in enumerate(urls):
                    self.current_download_index = index
                    self.create_progress_bar(url, index)
                    self.log(f"Baixando: {url}")
                    ydl.download([url])
                    self.log(f"Concluído: {url}")
        except Exception as e:
            self.log(f"Erro: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                percent = float(percent_str)
            except ValueError:
                percent = 0
            self.update_progress(d.get('info_dict', {}).get('webpage_url', ''), percent)
            self.log(f"Progresso: {d.get('_percent_str', '0%')} - {d.get('filename', 'Desconhecido')}")
        elif d['status'] == 'finished':
            self.log("Conversão para MP3 concluída.")
    
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Aviso", "Download em andamento. Aguarde.")
            return
        
        # Limpar barras de progresso antigas
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        self.progress_bars.clear()
        self.total_progress["value"] = 0
        
        # Obter URLs
        urls = self.url_text.get("1.0", END).strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]
        valid_urls = self.validate_urls(urls)
        
        if not valid_urls:
            messagebox.showerror("Erro", "Nenhum URL válido do YouTube fornecido.")
            return
        
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showerror("Erro", "Selecione um diretório de saída.")
            return
        
        self.total_downloads = len(valid_urls)
        self.is_downloading = True
        self.download_button.config(state=DISABLED)
        self.log(f"Iniciando download de {len(valid_urls)} vídeos...")
        
        # Executar download em uma thread separada
        def download_thread():
            self.download_youtube_mp3(valid_urls, output_dir)
            self.is_downloading = False
            self.download_button.config(state=NORMAL)
            self.log("Todos os downloads concluídos!")
            self.root.after(0, lambda: messagebox.showinfo("Concluído", "Downloads finalizados com sucesso!"))
        
        threading.Thread(target=download_thread, daemon=True).start()

if __name__ == "__main__":
    root = ttk.Window()
    app = YouTubeToMP3App(root)
    root.mainloop()