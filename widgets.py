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
    print(historias.Historias)
    return nova_historia

def ocultar_frame(frame):
    frame.place_forget()

def criar_label(nova_historia,frame_historia, callback=None):
    label = ctk.CTkButton(frame_historia, text=nova_historia["nome"],command=lambda: callback(nova_historia) if callback else print(historias.Historias)
    )
    label.grid(column=0, row=len(historias.Historias),sticky="n",pady=3)
    return label