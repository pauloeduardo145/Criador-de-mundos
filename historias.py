from storage import carregar_dados, salvar_dados

Historias = carregar_dados()

def atualizar(backup=True):
    salvar_dados(Historias, backup=backup)

def estatisticas():

    return {
        "historias": len(Historias),
        "personagens": sum(len(h["personagens"]) for h in Historias),
        "sistemas": sum(len(h["sistemas_poder"]) for h in Historias),
        "arcos": sum(len(h["arcos"]) for h in Historias),
        "capitulos": sum(len(h["capitulos"]) for h in Historias),
        "observacoes": sum(len(h["observacoes"]) for h in Historias),
        "planetas": sum(len(h.get("planetas", [])) for h in Historias),
        "calendarios": sum(len(h.get("calendarios", [])) for h in Historias),
    }