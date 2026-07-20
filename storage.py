import json
import os
import shutil
from datetime import datetime

# Configuração de Caminhos
BASE_DOCUMENTOS = os.path.join(os.path.expanduser("~"), "Documentos")
PASTA_PROJETO = os.path.join(BASE_DOCUMENTOS, "Criador de Mundos")
PASTA_BACKUP = os.path.join(PASTA_PROJETO, "Backups Criador de Mundos")
PASTA_IMAGENS = os.path.join(PASTA_PROJETO, "IMAGENS")
ARQUIVO_DADOS = os.path.join(PASTA_PROJETO, "historias.json")
PASTA_GALERIA = os.path.join(PASTA_PROJETO,"GALERIA")
ARQUIVO_PERFIL = os.path.join(PASTA_PROJETO,"perfil.json")

# Garante que as pastas existam
os.makedirs(PASTA_IMAGENS, exist_ok=True)
os.makedirs(PASTA_BACKUP, exist_ok=True)
os.makedirs(PASTA_GALERIA, exist_ok=True)

def limpar_backups_antigos(max_quantidade=30):
    arquivos = sorted(
        [f for f in os.listdir(PASTA_BACKUP) if f.endswith(".zip")]
    )
    
    # Remove os mais antigos se exceder o limite
    while len(arquivos) > max_quantidade:
        arquivo_remover = os.path.join(PASTA_BACKUP, arquivos[0])
        try:
            os.remove(arquivo_remover)
            print(f"Backup antigo removido: {arquivos[0]}")
        except Exception as e:
            print(f"Erro ao remover {arquivos[0]}: {e}")
        arquivos.pop(0)

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return []
    
def salvar_dados(dados):
    # 1. Salva o JSON
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    # 2. Cria o Backup
    # CORREÇÃO: O backup deve ser da PASTA_PROJETO (ou IMAGENS), não da pasta de BACKUP.
    # Usamos ignore para não incluir a própria pasta de backups no zip.
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_{data_atual}"
    caminho_saida = os.path.join(PASTA_BACKUP, nome_backup)

    try:
        # Copia a estrutura ignorando a pasta de backups e arquivos temporários
        # Nota: make_archive não tem 'ignore' direto, então fazemos um zip manual ou usamos copytree+make_archive
        # Abaixo, método robusto usando shutil.copytree com ignore para criar um temp e depois zipar
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            nome_pasta_temp = "Criador_de_Mundos_Backup"
            caminho_temp = os.path.join(tmp_dir, nome_pasta_temp)
            
            # Função para ignorar a pasta de backups e arquivos ocultos
            def ignore_func(dir, files):
                return [f for f in files if f == os.path.basename(PASTA_BACKUP) or f.startswith('.')]
            
            # Copia apenas o necessário (excluindo a pasta de backups)
            # Precisamos listar o que ignorar pelo NOME da pasta, não caminho completo
            shutil.copytree(
                PASTA_PROJETO, 
                caminho_temp, 
                ignore=shutil.ignore_patterns(os.path.basename(PASTA_BACKUP), "*.tmp", ".DS_Store")
            )
            
            # Cria o zip a partir da cópia limpa
            shutil.make_archive(caminho_saida, "zip", tmp_dir, nome_pasta_temp)
            
        print(f"Backup criado com sucesso: {nome_backup}.zip")
        
        # 3. Limpa backups antigos
        limpar_backups_antigos(10)

    except Exception as erro:
        print(f"Erro ao criar backup: {erro}")

def carregar_perfil():
    if not os.path.exists(ARQUIVO_PERFIL):
        return {
            "autor": "",
            "descricao": ""
        }

    try:
        with open(ARQUIVO_PERFIL, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar perfil: {e}")
        return {
            "autor": "",
            "descricao": ""
        }

def salvar_perfil(perfil):
    with open(ARQUIVO_PERFIL, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=4)

# Exemplo de uso:
# dados = carregar_dados()
# dados.append({"historia": "Nova aventura"})
# salvar_dados(dados)   