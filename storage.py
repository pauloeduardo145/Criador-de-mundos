import json
import os
import shutil
from datetime import datetime

PASTA = os.path.join(
     os.path.expanduser("~"),
     "Documentos",
     "Criador de Mundos"
)

BACKUP = os.path.join(os.path.expanduser("~"),"Documentos","Criador de Mundos", "Backups Criador de Mundos")

IMAGENS = os.path.join(
    PASTA,
    "IMAGENS"
)

os.makedirs(IMAGENS, exist_ok=True)

os.makedirs(PASTA, exist_ok=True)

os.makedirs(BACKUP, exist_ok=True)

arquivos = sorted(
    [f for f in os.listdir(BACKUP) if f.endswith(".zip")]
)

while len(arquivos) > 30:
    os.remove(os.path.join(BACKUP, arquivos[0]))
    arquivos.pop(0)


ARQUIVO = os.path.join(
     PASTA,
     "historias.json"
)

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return []
    try:
        with open(ARQUIVO, "r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return[]
    
def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_{data_atual}"

    try:
        shutil.make_archive(
            os.path.join(BACKUP, nome_backup),
            "zip",
            PASTA
        )
    except Exception as erro:
        print(f"Erro ao criar backup: {erro}")

    arquivos = sorted(
        [f for f in os.listdir(BACKUP) if f.endswith(".zip")]
    )

    while len(arquivos) > 30:
        os.remove(os.path.join(BACKUP, arquivos[0]))
        arquivos.pop(0)