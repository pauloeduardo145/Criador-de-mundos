import os
import sys
import requests

if getattr(sys, "frozen", False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_PATH, "version.txt"), encoding="utf-8") as f:
    VERSAO_ATUAL = f.read().strip()

URL = "https://create-of-world-s.pauloeduardodasilvaporto613.workers.dev/latest.json"


def verificar_atualizacao():
    try:
        dados = requests.get(URL, timeout=5).json()

        if dados["version"] != VERSAO_ATUAL:
            return True, dados

    except Exception:
        pass

    return False, None