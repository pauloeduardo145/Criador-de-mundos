import uuid

def nova_historia(nome):
    return {
        "nome": nome,
        "id":str(uuid.uuid4()),
        "imagem": "",
        "ultima_edicao": "",
        "capitulos": [],
        "arcos": [],
        "personagens": [],
        "sistemas_poder": [],
        "observacoes": [],
        "especies": []
    }

def nova_especie(nome, historia, descricao=""):
    return{
        "id": str(uuid.uuid4()),
        "nome": nome,
        "historia_id": historia["id"],
        "descricao": descricao
    }

def novo_personagem(nome, idade,especie,historia,caminho_imagem,personalidade,aparencia,his,relacoes,sistema,hab):
    return {
        "nome": nome,
        "idade": idade,
        "especie": especie["id"] if especie else "",
        "id": str(uuid.uuid4()),
        "imagens": caminho_imagem,
        "galeria": [],
        "historia_id": historia["id"],
        "personalidade": personalidade,
        "aparencia": aparencia,
        "historia": his,
        "relacoes": relacoes,
        "sistema_poder": sistema["id"] if sistema else "",
        "habilidades": hab
    }

def nova_imagem_galeria(caminho, descricao):
    return {
        "imagem": caminho,
        "descricao": descricao
    }

def nova_observacao(nome,titulo,conteudo,tipo="Personagem"):
    return{
        "tipo": tipo,
        "nome": nome,
        "titulo": titulo,
        "conteudo": conteudo
    }

def novo_capitulo(nome,arco_id,conteudo):
    return {
        "nome": nome,
        "arco_id": arco_id,
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

def novo_arco (nome, historia, descricao):
    return{
        "id": str(uuid.uuid4()),
        "nome": nome,
        "historia_id": historia["id"],
        "descricao": descricao
    }