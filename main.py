from interface import *

from updater import verificar_atualizacao

tem_atualizacao, dados = verificar_atualizacao()

if tem_atualizacao:
    print("Nova versão disponível:", dados["version"])

# continua iniciando o programa normalmente