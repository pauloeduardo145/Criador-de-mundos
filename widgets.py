import customtkinter as ctk
from historias import Historias

def mostrar_frame(frame):
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.lift()

def criar_historia(texto):
    Historias.append(texto)

def ocultar_frame(frame):
    frame.place_forget()


def criar_label(texto,frame_historia):
    label = ctk.CTkButton(frame_historia, text=texto)
    label.grid(column=0, row=len(Historias),sticky="n",pady=3)
    return label
