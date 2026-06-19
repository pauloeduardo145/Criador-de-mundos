from storage import carregar_dados, salvar_dados

Historias = carregar_dados()

def atualizar():
    print(Historias)
    salvar_dados(Historias)