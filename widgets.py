import customtkinter as ctk
import historias
from modelos import nova_historia, novo_personagem, novo_capitulo,novo_sistemapoder

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

def criar_personagem(historia,nome,imagem,personalidade,aparencia,his,relacoes,poderes,hab):

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

    personagem = novo_personagem(nome, historia,imagem,personalidade,aparencia,his,relacoes,poderes,hab)

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