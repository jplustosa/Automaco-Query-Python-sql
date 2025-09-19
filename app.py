#exclui arquivo ja executado
import oracledb
import csv
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import time
import threading
import glob

# Configuração do banco de dados
user = "usuario_db"
password = "senhadb"
dsn = "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=servidor-scan)(PORT=porta))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=bancodedados)))" #Configuração de DSN do seu Banco

# Variáveis globais
pasta_monitorada = "./scripts/"
monitorando = False
thread_monitoramento = None

def criar_pasta_scripts():
    """Cria a pasta scripts se não existir"""
    if not os.path.exists(pasta_monitorada):
        os.makedirs(pasta_monitorada)
        print(f"Pasta '{pasta_monitorada}' criada.")

def extrair_query_do_arquivo(caminho_arquivo):
    """Lê o conteúdo do arquivo de forma simples"""
    try:
        # Tenta diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(caminho_arquivo, 'r', encoding=encoding) as file:
                    conteudo = file.read().strip()
                return conteudo
            except UnicodeDecodeError:
                continue
        
        # Se todos falharem, tenta com errors ignore
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as file:
            conteudo = file.read().strip()
        return conteudo
        
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None

def executar_query_direct(cursor, query):
    """Executa a query diretamente no cursor"""
    try:
        cursor.execute(query)
        return True
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        print(f"Erro Oracle: {error_obj.code} - {error_obj.message}")
        return False
    except Exception as e:
        print(f"Erro geral: {e}")
        return False

def apagar_arquivo_script(caminho_arquivo):
    """Apaga o arquivo de script após execução bem-sucedida"""
    try:
        os.remove(caminho_arquivo)
        print(f"Arquivo apagado: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"Erro ao apagar arquivo {caminho_arquivo}: {e}")
        return False

def executar_query(query, nome_arquivo, caminho_script):
    """Executa a query e exporta para CSV"""
    try:
        if not query or query.strip() == '':
            messagebox.showerror("Erro", "Query vazia ou inválida.")
            return False
            
        print(f"Executando query: {query[:100]}...")  # Log parcial da query
        
        # Estabelecendo conexão com o banco
        dados_conexao = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = dados_conexao.cursor()

        # Define formato de data para a sessão
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY'")
        
        # Executa a query
        if not executar_query_direct(cursor, query):
            dados_conexao.close()
            return False

        # Obter os nomes das colunas
        columns = [col[0] for col in cursor.description]

        # Obter todos os dados
        data = cursor.fetchall()

        if not data:
            messagebox.showinfo("Info", "A query não retornou resultados.")
            cursor.close()
            dados_conexao.close()
            # Apaga o arquivo mesmo sem resultados
            apagar_arquivo_script(caminho_script)
            return True

        # Criar DataFrame com pandas
        df = pd.DataFrame(data, columns=columns)
        
        # Perguntar onde salvar o arquivo
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=nome_arquivo,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if caminho_arquivo:
            # Exportar para CSV usando pandas com encoding UTF-8-BOM
            df.to_csv(caminho_arquivo, sep=';', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
            
            # Apagar o arquivo de script após sucesso
            if apagar_arquivo_script(caminho_script):
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso!\nLinhas: {len(df)}\nScript original apagado.")
            else:
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso!\nLinhas: {len(df)}\n(Erro ao apagar script)")
            
            return True
        
        # Fechar recursos
        cursor.close()
        dados_conexao.close()
        return False

    except oracledb.DatabaseError as e:
        error_obj, = e.args
        messagebox.showerror("Erro de Banco de Dados", 
                           f"Erro Oracle {error_obj.code}:\n{error_obj.message}")
        return False
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{str(e)}")
        return False

def processar_arquivos_txt():
    """Processa todos os arquivos .txt na pasta scripts"""
    global pasta_monitorada
    
    criar_pasta_scripts()
    arquivos_txt = glob.glob(os.path.join(pasta_monitorada, "*.txt"))
    
    if not arquivos_txt:
        messagebox.showinfo("Info", "Nenhum arquivo .txt encontrado na pasta './scripts/'.")
        return
    
    for arquivo in arquivos_txt:
        nome_arquivo = os.path.basename(arquivo)
        query_content = extrair_query_do_arquivo(arquivo)
        
        if query_content:
            # Usar o nome do arquivo txt como base para o CSV
            nome_csv = nome_arquivo.replace('.txt', '.csv')
            log_mensagem(f"Processando: {nome_arquivo}")
            
            if executar_query(query_content, nome_csv, arquivo):
                log_mensagem(f"Concluído e script apagado: {nome_arquivo}")
            else:
                log_mensagem(f"Falha ao executar: {nome_arquivo}")
        else:
            log_mensagem(f"Erro ao ler: {nome_arquivo}")

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        dados_conexao = oracledb.connect(user=user, password=password, dsn=dsn)
        cursor = dados_conexao.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        resultado = cursor.fetchone()
        cursor.close()
        dados_conexao.close()
        
        messagebox.showinfo("Conexão Testada", "Conexão com o banco de dados bem-sucedida!")
        return True
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Falha na conexão:\n{str(e)}")
        return False

def monitorar_pasta():
    """Monitora a pasta por novos arquivos .txt"""
    global monitorando
    
    criar_pasta_scripts()
    arquivos_processados = set()
    
    while monitorando:
        try:
            # Verificar novos arquivos .txt
            arquivos_atual = set(glob.glob(os.path.join(pasta_monitorada, "*.txt")))
            novos_arquivos = arquivos_atual - arquivos_processados
            
            for arquivo in novos_arquivos:
                nome_arquivo = os.path.basename(arquivo)
                query_content = extrair_query_do_arquivo(arquivo)
                
                if query_content:
                    root.after(0, lambda: status_var.set(f"Processando: {nome_arquivo}"))
                    root.after(0, lambda: log_mensagem(f"Novo arquivo: {nome_arquivo}"))
                    
                    nome_csv = nome_arquivo.replace('.txt', '.csv')
                    success = executar_query(query_content, nome_csv, arquivo)
                    
                    if success:
                        arquivos_processados.add(arquivo)
                        root.after(0, lambda: status_var.set(f"Processado: {nome_arquivo}"))
                        root.after(0, lambda: log_mensagem(f"Concluído e script apagado: {nome_arquivo}"))
                    else:
                        root.after(0, lambda: log_mensagem(f"Falha: {nome_arquivo}"))
                
            time.sleep(5)  # Verificar a cada 5 segundos
            
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            time.sleep(10)

def iniciar_monitoramento():
    """Inicia o monitoramento da pasta"""
    global monitorando, thread_monitoramento
    
    if not testar_conexao():
        return
    
    monitorando = True
    thread_monitoramento = threading.Thread(target=monitorar_pasta, daemon=True)
    thread_monitoramento.start()
    btn_iniciar.config(state=tk.DISABLED)
    btn_parar.config(state=tk.NORMAL)
    status_var.set("Monitoramento INICIADO")
    log_mensagem("Monitoramento iniciado - Os scripts serão apagados após execução")

def parar_monitoramento():
    """Para o monitoramento da pasta"""
    global monitorando
    monitorando = False
    btn_iniciar.config(state=tk.NORMAL)
    btn_parar.config(state=tk.DISABLED)
    status_var.set("Monitoramento PARADO")
    log_mensagem("Monitoramento parado")

def abrir_pasta_scripts():
    """Abre a pasta scripts no explorador de arquivos"""
    criar_pasta_scripts()
    try:
        os.startfile(os.path.abspath(pasta_monitorada))
    except:
        try:
            os.system(f'explorer "{os.path.abspath(pasta_monitorada)}"')
        except:
            messagebox.showinfo("Abrir Pasta", f"Pasta: {os.path.abspath(pasta_monitorada)}")

def limpar_pasta_scripts():
    """Limpa todos os arquivos .txt da pasta scripts"""
    try:
        arquivos_txt = glob.glob(os.path.join(pasta_monitorada, "*.txt"))
        if not arquivos_txt:
            messagebox.showinfo("Info", "Não há arquivos para limpar.")
            return
        
        confirmacao = messagebox.askyesno("Confirmar", 
                                         f"Deseja apagar {len(arquivos_txt)} arquivo(s) da pasta scripts?")
        if confirmacao:
            for arquivo in arquivos_txt:
                try:
                    os.remove(arquivo)
                    log_mensagem(f"Arquivo apagado: {os.path.basename(arquivo)}")
                except Exception as e:
                    log_mensagem(f"Erro ao apagar {os.path.basename(arquivo)}: {e}")
            
            messagebox.showinfo("Concluído", "Limpeza da pasta scripts concluída.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao limpar pasta: {e}")

def log_mensagem(mensagem):
    """Adiciona mensagem ao log"""
    text_log.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {mensagem}\n")
    text_log.see(tk.END)
    text_log.update_idletasks()

# Criar a interface gráfica
root = tk.Tk()
root.title("Monitor de Queries SQL - Auto Delete")
root.geometry("800x600")

# Frame principal
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Título
tk.Label(frame, text="Monitor de Queries SQL - Auto Delete", font=("Arial", 16, "bold")).pack(pady=10)

# Botões de controle
frame_botoes = tk.Frame(frame)
frame_botoes.pack(pady=10)

btn_testar = tk.Button(frame_botoes, text="Testar Conexão", command=testar_conexao, bg="blue", fg="white")
btn_testar.pack(side=tk.LEFT, padx=5)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_monitoramento, bg="green", fg="white")
btn_iniciar.pack(side=tk.LEFT, padx=5)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento, bg="red", fg="white", state=tk.DISABLED)
btn_parar.pack(side=tk.LEFT, padx=5)

btn_processar = tk.Button(frame_botoes, text="Processar Arquivos", command=processar_arquivos_txt, bg="orange", fg="white")
btn_processar.pack(side=tk.LEFT, padx=5)

btn_abrir_pasta = tk.Button(frame_botoes, text="Abrir Pasta", command=abrir_pasta_scripts, bg="purple", fg="white")
btn_abrir_pasta.pack(side=tk.LEFT, padx=5)

btn_limpar = tk.Button(frame_botoes, text="Limpar Pasta", command=limpar_pasta_scripts, bg="darkred", fg="white")
btn_limpar.pack(side=tk.LEFT, padx=5)

# Status
status_var = tk.StringVar()
status_var.set("Pronto - Aguardando")
tk.Label(frame, textvariable=status_var, font=("Arial", 11), fg="darkgreen", bg="lightyellow").pack(pady=5)

# Log de atividades
tk.Label(frame, text="Log de Execução:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
text_log = tk.Text(frame, height=15, width=90, font=("Consolas", 9))
text_log.pack(fill=tk.BOTH, expand=True, pady=5)

# Barra de rolagem
scrollbar = tk.Scrollbar(text_log)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_log.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_log.yview)

# Criar pasta scripts ao iniciar
criar_pasta_scripts()
log_mensagem(f"Sistema iniciado - Pasta: {os.path.abspath(pasta_monitorada)}")
log_mensagem("Cole arquivos .txt com queries SQL na pasta scripts")
log_mensagem("Os scripts serão APAGADOS após execução bem-sucedida!")

# Executar a interface
root.mainloop()