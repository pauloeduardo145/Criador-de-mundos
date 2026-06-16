import json
import os

PASTA = os.path.join(
     os.path.expanduser("~"),
     "Documentos",
     "Criador de Mundos"
)

os.makedirs(PASTA, exist_ok=True)

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
        with open(ARQUIVO, "w",encoding="utf-8") as f:
             json.dump(dados,f,ensure_ascii=False,indent=4)