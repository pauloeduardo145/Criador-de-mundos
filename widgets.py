import customtkinter as ctk
import historias

def mostrar_frame(frame):
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.lift()

def criar_historia(texto):

    for h in historias.Historias:
        if h["nome"] == texto:
            print("Já existe uma história com esse nome.")
            return h 

    nova_historia =  {
        "nome": texto,
        "imagem": "",
        "arcos": [],
        "capitulos": [],
        "personagens": [],
        "sistemas_poder": []
    } 

    historias.Historias.append(nova_historia)
    print(historias.Historias)
    historias.atualizar()  
    return nova_historia

def ocultar_frame(frame):
    frame.place_forget()

def criar_label(nova_historia,frame_historia, callback=None):
    label = ctk.CTkButton(frame_historia, text=nova_historia["nome"],command=lambda: callback(nova_historia) if callback else print(historias.Historias)
    )
    label.grid(column=0, row=len(historias.Historias),sticky="n",pady=3)
    return label

def criar_personagem(historia,nome):

    for p in historia["personagens"]:
        if p["nome"] == nome:
            print("Já existe um personagem com esse nome.")
            return p 

    if historia is None:
        print("Selecione uma história primeiro")
        return

    import uuid


    novo_id = str(uuid.uuid4())

    novo_personagem = {
        "nome": nome,
        "id": novo_id,
        "imagens": "", 
        "historia_id": historia["nome"],
        "personalidade": "",
        "aparencia": "",
        "relacoes": "",
        "poderes": ""
    }

    historia["personagens"].append(novo_personagem)
    historias.atualizar()
    return novo_personagem



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