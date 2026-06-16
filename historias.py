from storage import carregar_dados, salvar_dados

Historias = carregar_dados()

def atualizar():
    salvar_dados(Historias)