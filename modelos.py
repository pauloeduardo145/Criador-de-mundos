import uuid

def nova_historia(nome):
    return {
        "nome": nome,
        "imagem": "",
        "arcos": [],
        "capitulos": [],
        "personagens": [],
        "sistemas_poder": []
    }

def novo_personagem(nome, historia):
    return {
        "nome": nome,
        "id": str(uuid.uuid4()),
        "imagens": "",
        "historia_id": historia["nome"],
        "personalidade": "",
        "aparencia": "",
        "relacoes": "",
        "poderes": ""
    }

def novo_capitulo(nome,conteudo):
    return {
        "nome": nome,
        "imagens": "",
        "relacoes": "",
        "conteudo": conteudo
    }