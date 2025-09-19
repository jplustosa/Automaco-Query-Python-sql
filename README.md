# Monitor de Queries SQL - Auto Delete

Sistema automatizado para executar queries SQL a partir de arquivos de texto e exportar os resultados para CSV, com remoção automática dos scripts após execução bem-sucedida.

## 📋 Funcionalidades

- **Monitoramento Automático**: Observa a pasta `./scripts/` por novos arquivos
- **Execução de Queries**: Executa queries SQL diretamente no banco Oracle
- **Exportação para CSV**: Salva resultados em arquivos CSV com encoding UTF-8
- **Auto Delete**: Remove automaticamente os scripts após execução bem-sucedida
- **Interface Gráfica**: Interface intuitiva com log de atividades
- **Multi-encoding**: Suporte a diferentes codificações de arquivo

## 🚀 Como Usar

### 1. Pré-requisitos

```bash
# Instalar dependências
pip install oracledb pandas chardet
```

### 2. Preparação dos Scripts

Crie a pasta `scripts` (será criada automaticamente) e adicione arquivos `.txt` com suas queries SQL:

**Exemplo de arquivo `minha_query.txt`:**
```sql
SELECT 
    CLIENTE.ID AS CODIGO_CLIENTE,
    CLIENTE.NOME AS NOME_CLIENTE,
    CLIENTE.EMAIL,
    CLIENTE.TELEFONE,
    TO_CHAR(CLIENTE.DATA_CADASTRO, 'DD/MM/YYYY') AS DATA_CADASTRO,
    CIDADE.NOME AS CIDADE,
    ESTADO.UF,...
```

### 3. Execução do Sistema

```bash
python monitor_queries.py
```

### 4. Fluxo de Trabalho

1. **Cole arquivos** `.txt` na pasta `./scripts/`
2. **Inicie o monitoramento** ou processe manualmente
3. **Escolha onde salvar** o CSV quando solicitado
4. **O script será apagado** automaticamente após sucesso

## 🎯 Comandos da Interface

### Botões Principais

- **Testar Conexão**: Verifica conexão com o banco de dados
- **Iniciar Monitoramento**: Inicia monitoramento automático da pasta
- **Parar Monitoramento**: Interrompe o monitoramento
- **Processar Arquivos**: Executa todos os arquivos existentes
- **Abrir Pasta**: Abre a pasta de scripts no explorador
- **Limpar Pasta**: Remove todos os arquivos .txt manualmente

### Comportamento de Auto Delete

- ✅ **Sucesso**: CSV salvo → Script .txt apagado
- ✅ **Sem resultados**: Query executada → Script .txt apagado  
- ❌ **Erro**: Falha na execução → Script NÃO apagado (para correção)

## ⚙️ Configuração do Banco

Edite as variáveis no script para sua conexão Oracle:

```python
user = "seu_usuario"
password = "sua_senha"
dsn = "sua_string_de_conexao"
```

## 📁 Estrutura de Arquivos

```
projeto/
├── monitor_queries.py      # Script principal
├── scripts/               # Pasta monitorada (auto-criada)
│   ├── query1.txt         # Arquivos com queries SQL
│   └── query2.txt
└── resultados/            # CSVs salvos (local escolhido pelo usuário)
```

## 🔄 Fluxo de Processamento

1. **Detecção**: Sistema detecta novo arquivo `.txt` na pasta
2. **Leitura**: Lê o conteúdo do arquivo (suporte a múltiplos encodings)
3. **Execução**: Conecta ao Oracle e executa a query
4. **Exportação**: Gera arquivo CSV com os resultados
5. **Limpeza**: Apaga o arquivo `.txt` original
6. **Log**: Registra todas as atividades no painel

## 🛠️ Solução de Problemas

### Erros Comuns

1. **Erro de encoding**: 
   - O sistema tenta automaticamente UTF-8, Latin-1, ISO-8859-1, CP1252
   - Funciona com a maioria dos arquivos de texto

2. **Erro de conexão**:
   - Use "Testar Conexão" para verificar configurações
   - Verifique usuário, senha e DSN

3. **Query não executa**:
   - Teste a query diretamente no PL/SQL primeiro
   - Verifique sintaxe SQL

### Log de Atividades

O painel inferior mostra em tempo real:
- Arquivos detectados
- Queries executadas
- Erros encontrados
- Arquivos apagados

## 📝 Notas Importantes

- **Backup automático**: Os scripts são apagados após uso, mantenha cópias se necessário
- **Segurança**: As credenciais do banco estão embutidas no código
- **Performance**: Queries muito grandes podem demorar para processar
- **Network**: Requer conexão estável com o banco de dados

## 🎉 Pronto para Usar!

Agora basta colocar seus arquivos `.txt` na pasta `scripts` e o sistema fará todo o trabalho automaticamente!