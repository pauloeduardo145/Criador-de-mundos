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
        "especies": [],
        "calendarios": [],
        "dicionarios": [],
        "desenhos": [],
        "sistemas_solares": [],
        "planetas": []
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

# ---------------------------------------------------------------
# MURAL (calendários, dicionários, desenhos, sistemas solares)
# ---------------------------------------------------------------

def novo_calendario(nome, historia, ano_inicial=1):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "historia_id": historia["id"],
        "ano_inicial": ano_inicial,
        "horas_dia": 24,
        "dias_semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
        "meses": [{"nome": n, "dias": d} for n, d in [
            ("Janeiro", 31), ("Fevereiro", 28), ("Março", 31), ("Abril", 30),
            ("Maio", 31), ("Junho", 30), ("Julho", 31), ("Agosto", 31),
            ("Setembro", 30), ("Outubro", 31), ("Novembro", 30), ("Dezembro", 31)]],
        # a cada N anos o mês ganha dias extras (ex.: ano bissexto)
        "regras": [],              # [{"cada": 4, "mes": 1, "extra": 1}]
        # anos com duração própria (têm prioridade sobre as regras)
        "anos_especiais": []       # [{"ano": 1042, "dias": [31, 30, ...]}]
    }

def novo_dicionario(nome, historia, descricao=""):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "historia_id": historia["id"],
        "descricao": descricao,
        "letras": []
    }

def nova_letra(nome):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "equivale": nome.lower(),   # letra/som latino que ela representa
        "tipo": "Consoante",
        "pronuncia": "",
        "notas": "",
        "espessura": 8,
        "avanco": 1000,             # largura do glifo (1000 = quadrado inteiro)
        "tracos": []                # [[[x, y], ...], ...] em um quadrado 0..1000
    }

def novo_desenho(nome, largura=800, altura=600):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "largura": largura,
        "altura": altura,
        "camadas": []               # [{"id", "nome", "visivel"}]; PNGs em DESENHOS/<id>/
    }

def novo_sistema_solar(nome, x=0.0, y=0.0):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "x": x,                     # posição na galáxia, em anos-luz
        "y": y,
        "estrela": {"nome": nome, "cor": "#ffd54a", "tamanho": 1.0},
        "orbitas": []               # [{"id", "raio" (UA), "planeta_id", "angulo0"}]
    }

def novo_planeta(nome):
    return {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "cor": "#4aa3ff",
        "tamanho": "Médio",
        "peso": "",
        "diametro_km": 12742.0,
        "estacoes": False,
        "luas": 0,
        "especie_id": "",
        "dias_ano": 365.0,
        "horas_dia": 24.0,
        "sistema_id": "",
        "orbita_id": ""
    }
