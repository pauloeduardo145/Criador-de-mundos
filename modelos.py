import uuid

def nova_historia(nome):
    return {
        "nome": nome,
        "id":str(uuid.uuid4()),
        "imagem": "",
        "ultima_edicao": "",
        "capitulos": [],
        "personagens": [],
        "sistemas_poder": [],
        "observacoes": []
    }

def novo_personagem(nome, historia,caminho_imagem,personalidade,aparencia,his,relacoes,poderes,fraq,hab):
    return {
        "nome": nome,
        "id": str(uuid.uuid4()),
        "imagens": caminho_imagem,
        "galeria": [],
        "historia_id": historia["id"],
        "personalidade": personalidade,
        "aparencia": aparencia,
        "historia": his,
        "relacoes": relacoes,
        "poderes": poderes,
        "fraquezas": fraq,
        "habilidades": hab
    }

def nova_imagem_galeria(caminho, descricao):
    return {
        "imagem": caminho,
        "descricao": descricao
    }

def nova_observacao(nome,relacao,conteudo):
    return{
        "nome": nome,
        "relacao": relacao,
        "conteudo": conteudo
    }

def novo_capitulo(nome,conteudo):
    return {
        "nome": nome,
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
