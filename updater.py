import requests

with open("version.txt", encoding="utf-8") as f:
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