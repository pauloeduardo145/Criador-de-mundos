import uuid

def nova_historia(nome):
    return {
        "nome": nome,
        "id":str(uuid.uuid4()),
        "imagem": "",
        "ultima_edicao": "",
        "arcos": [],
        "capitulos": [],
        "personagens": [],
        "sistemas_poder": []
    }

def novo_personagem(nome, historia,caminho_imagem,personalidade,aparencia,his,relacoes,poderes,hab):
    return {
        "nome": nome,
        "id": str(uuid.uuid4()),
        "imagens": caminho_imagem,
        "historia_id": historia["id"],
        "personalidade": personalidade,
        "aparencia": aparencia,
        "historia": his,
        "relacoes": relacoes,
        "poderes": poderes,
        "habilidades": hab
    }

def novo_capitulo(nome,conteudo):
    return {
        "nome": nome,
        "imagens": "",
        "relacoes": "",
        "conteudo": conteudo
    }

def novo_sistemapoder(nome,historia,descricao,regras,vantagens,fraquezas):
    return {
    "id": str(uuid.uuid4()),
    "historia_id":historia["id"],
    "nome": nome,
    "descricao": descricao,
    "regras": regras,
    "vantagens": vantagens,
    "fraquezas": fraquezas,
    "exemplos": []
}

#sistema = novo_sistemapoder("Abelha")
#print(sistema["id"])