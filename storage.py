import json
import os


ARQUIVO = "historias.json"

def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return []

    with open(ARQUIVO, "r",encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
        with open(ARQUIVO, "w",encoding="utf-8") as f:
             json.dump(dados,f,ensure_ascii=False,indent=4)