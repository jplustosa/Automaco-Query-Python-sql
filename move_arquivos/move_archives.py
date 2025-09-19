#script para mover arquivos

import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os
from pathlib import Path

class FileCopier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Copiador de Arquivos")
        self.root.geometry("500x400")
        
        self.selected_files = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Copiador de Arquivos", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Botão para selecionar arquivos
        select_btn = tk.Button(main_frame, text="Selecionar Arquivos", 
                              command=self.select_files,
                              font=("Arial", 12),
                              bg="#4CAF50", fg="white",
                              padx=20, pady=10)
        select_btn.pack(pady=10)
        
        # Lista de arquivos selecionados
        self.file_listbox = tk.Listbox(main_frame, height=8, width=60)
        self.file_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Frame para botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Botão para selecionar destino
        dest_btn = tk.Button(button_frame, text="Selecionar Destino", 
                            command=self.select_destination,
                            font=("Arial", 12),
                            bg="#2196F3", fg="white",
                            padx=20, pady=10)
        dest_btn.pack(side=tk.LEFT, padx=10)
        
        # Botão para copiar arquivos
        copy_btn = tk.Button(button_frame, text="Copiar Arquivos", 
                            command=self.copy_files,
                            font=("Arial", 12),
                            bg="#FF9800", fg="white",
                            padx=20, pady=10)
        copy_btn.pack(side=tk.LEFT, padx=10)
        
        # Botão para limpar seleção
        clear_btn = tk.Button(button_frame, text="Limpar Seleção", 
                             command=self.clear_selection,
                             font=("Arial", 12),
                             bg="#f44336", fg="white",
                             padx=20, pady=10)
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Pronto para selecionar arquivos", 
                                    font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=5)
    
    def select_files(self):
        """Abre o explorador de arquivos para selecionar múltiplos arquivos"""
        files = filedialog.askopenfilenames(
            title="Selecione os arquivos para copiar",
            filetypes=[("Todos os arquivos", "*.*"),
                      ("Arquivos de texto", "*.txt"),
                      ("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp"),
                      ("Documentos", "*.doc *.docx *.pdf *.xlsx *.pptx")]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_file_list()
            self.status_label.config(text=f"{len(self.selected_files)} arquivo(s) selecionado(s)")
    
    def select_destination(self):
        """Abre o explorador para selecionar a pasta de destino"""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Por favor, selecione os arquivos primeiro!")
            return
        
        destination = filedialog.askdirectory(
            title="Selecione a pasta de destino"
        )
        
        if destination:
            self.destination_path = destination
            self.status_label.config(text=f"Destino: {destination}")
    
    def copy_files(self):
        """Copia os arquivos selecionados para o destino"""
        if not hasattr(self, 'destination_path') or not self.destination_path:
            messagebox.showwarning("Aviso", "Por favor, selecione a pasta de destino primeiro!")
            return
        
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return
        
        try:
            success_count = 0
            total_files = len(self.selected_files)
            
            for i, file_path in enumerate(self.selected_files, 1):
                try:
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(self.destination_path, file_name)
                    
                    # Verifica se arquivo já existe no destino
                    if os.path.exists(dest_path):
                        result = messagebox.askyesno(
                            "Arquivo existente", 
                            f"O arquivo '{file_name}' já existe no destino. Deseja substituir?"
                        )
                        if not result:
                            continue
                    
                    # Copia o arquivo
                    shutil.copy2(file_path, dest_path)
                    success_count += 1
                    
                    # Atualiza status
                    self.status_label.config(
                        text=f"Copiando... {i}/{total_files} - {file_name}"
                    )
                    self.root.update()
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao copiar {file_name}: {str(e)}")
            
            messagebox.showinfo("Sucesso", 
                               f"{success_count} de {total_files} arquivo(s) copiado(s) com sucesso!")
            self.status_label.config(text="Operação concluída!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a cópia: {str(e)}")
    
    def clear_selection(self):
        """Limpa a seleção de arquivos"""
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.status_label.config(text="Seleção limpa")
    
    def update_file_list(self):
        """Atualiza a lista de arquivos na interface"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, file_name)
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

# Versão simplificada alternativa
def copiar_arquivos_simples():
    """Versão mais simples sem interface gráfica completa"""
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    
    # Selecionar arquivos
    print("Selecione os arquivos para copiar...")
    arquivos = filedialog.askopenfilenames(title="Selecione os arquivos para copiar")
    
    if not arquivos:
        print("Nenhum arquivo selecionado.")
        return
    
    # Selecionar destino
    print("Selecione a pasta de destino...")
    destino = filedialog.askdirectory(title="Selecione a pasta de destino")
    
    if not destino:
        print("Nenhum destino selecionado.")
        return
    
    # Copiar arquivos
    import shutil
    for arquivo in arquivos:
        try:
            shutil.copy2(arquivo, destino)
            print(f"Copiado: {os.path.basename(arquivo)}")
        except Exception as e:
            print(f"Erro ao copiar {arquivo}: {e}")
    
    print("Operação concluída!")

if __name__ == "__main__":
    # Executar a versão com interface gráfica completa
    app = FileCopier()
    app.run()
    
    # Para usar a versão simplificada, descomente a linha abaixo:
    copiar_arquivos_simples()