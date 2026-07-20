from storage import carregar_dados, salvar_dados

Historias = carregar_dados()

def atualizar():
    print(Historias)
    salvar_dados(Historias)

def estatisticas():

    return {
        "historias": len(Historias),
        "personagens": sum(len(h["personagens"]) for h in Historias),
        "sistemas": sum(len(h["sistemas_poder"]) for h in Historias),
        "capitulos": sum(len(h["capitulos"]) for h in Historias),
        "observacoes": sum(len(h["observacoes"]) for h in Historias),
    }