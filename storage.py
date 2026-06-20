import json
import os
from modelos import nova_historia

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

    try:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    except Exception as erro:
        print(type(erro))
        print(erro)
        print(dados)