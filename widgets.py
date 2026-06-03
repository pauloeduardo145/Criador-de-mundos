import customtkinter as ctk
import historias


def mostrar_frame(frame):
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.lift()

def criar_historia(texto):

    nova_historia =  {
        "nome": texto,
        "arcos": [],
        "capitulos": [],
        "personagens": [],
        "sistemas_poder": []
    } 

    historias.Historias.append(nova_historia)
    print(historias.Historias[0]["nome"])
    print(historias.Historias)

    return nova_historia

def ocultar_frame(frame):
    frame.place_forget()

def criar_label(texto,frame_historia):
    label = ctk.CTkButton(frame_historia, text=texto,command=lambda:criar_historia(texto))
    label.grid(column=0, row=len(historias.Historias),sticky="n",pady=3)
    return label

def selecionar_historia(historia):
    global historia_selecionada

    historias.historia_selecionada = historia

    print("Selecionada:")
    print(historia["nome"])

def selecionar_historia(historia,nome_historia,arcos,cap,pers,sp):
    nome_historia.configure(text=f"Nome: {historia['nome']}")
    arcos.configure(text=f"Arcos: {len(historia['arcos'])}")
    cap.configure(text=f"Capítulos: {len(historia['capitulos'])}")
    pers.configure(text=f"Personagens: {len(historia['personagens'])}")
    sp.configure(text=f"Sistemas: {len(historia['sistemas_poder'])}")