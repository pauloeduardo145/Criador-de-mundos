import customtkinter as ctk
import historias
from modelos import nova_historia, novo_personagem, novo_capitulo,novo_sistemapoder,nova_imagem_galeria,nova_observacao
from PIL import Image

def mostrar_frame(frame):
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.lift()

def criar_historia(texto):

    if not texto.strip():
        print("Digite um nome.")
        return

    for h in historias.Historias:
        if h["nome"] == texto:
            print("Já existe uma história com esse nome.")
            return h

    historia = nova_historia(texto)

    historias.Historias.append(historia)

    print(historias.Historias)

    historias.atualizar()

    return historia

def ocultar_frame(frame):
    frame.place_forget()

def criar_label(nova_historia, frame_historia, callback=None, row=0):
    label = ctk.CTkButton(frame_historia, text=nova_historia["nome"], command=lambda:callback(nova_historia)
            if callback else None)
    label.grid(column=0,row=row,sticky="ew",pady=3)

    return label

def criar_personagem(historia,nome,imagem,personalidade,aparencia,his,relacoes,poderes,fraq,hab):

    if not nome.strip():
        print("Digite um nome.")
        return

    if historia is None:
        print("Selecione uma história primeiro")
        return

    for p in historia["personagens"]:
        if p["nome"] == nome:
            print("Já existe um personagem com esse nome.")
            return p

    personagem = novo_personagem(nome, historia,imagem,personalidade,aparencia,his,relacoes,poderes,fraq,hab)

    historia["personagens"].append(personagem)

    historias.atualizar()

    return personagem

def criar_label_personagem(personagem, frame, callback=None):

    botao = ctk.CTkButton(
        frame,
        text=personagem["nome"],
        command=lambda:
            callback(personagem)
            if callback else None
    )

    botao.pack(pady=3)

    return botao

def criar_label_capitulo(capitulo,frame,callback=None):
    botao = ctk.CTkButton(
        frame,
        text=capitulo["nome"],
        command=lambda:
            callback(capitulo)
            if callback else None
    )

    botao.pack(pady=3)

    return botao

def criar_capitulo(historia,nome,conteudo):

    if not nome.strip():
        print("Digite um nome.")
        return

    if historia is None:
        print("Selecione uma história primeiro")
        return

    capitulo = novo_capitulo(nome,conteudo)

    historia["capitulos"].append(capitulo)

    historias.atualizar()

    return capitulo

def criar_galeria(historia,personagem,caminho,descricao):
    
    if historia is None:
        return
    
    galeria = nova_imagem_galeria(caminho,descricao)

    personagem["galeria"].append(galeria)

    return galeria

def criar_label_sistema_poder(nome, frame, callback=None):

    botao = ctk.CTkButton(
        frame,
        text=nome["nome"],
        command=lambda:
            callback(nome)
            if callback else None
    )

    botao.pack(pady=3)

    return botao

def criar_sistemadepoder(historia,nome,descricao,regras,vantagens,fraquezas):

    if historia is None:
        print("Nenhuma história selecionada")
        return

    sistemapoder = novo_sistemapoder(nome,historia,descricao,regras,vantagens,fraquezas)

    historia["sistemas_poder"].append(sistemapoder)

    historias.atualizar()

    return sistemapoder

def criar_label_obs(nome, frame, callback=None):

    obs = ctk.CTkButton(
        frame,
        text=nome["nome"],
        command=lambda:
            callback(nome)
            if callback else None
    )

    obs.pack(pady=3)

    return obs

def criar_observacoes(historia,nome,titulo,conteudo):

    if historia is None:
        print("Nenhuma história selecionada")
        return

    observacao = nova_observacao(nome,titulo,conteudo)

    historia["observacoes"].append(observacao)

    historias.atualizar()

    return observacao

def mostrar_imagem(caminho,tamanho):
    imagem_pil = Image.open(caminho)
    imagem_pil.thumbnail((tamanho,tamanho))
    img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(imagem_pil.width, imagem_pil.height))

    return img_ctk
