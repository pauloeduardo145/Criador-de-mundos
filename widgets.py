def mostrar_frame(frame):
    frame.place(relx=0.5, rely=0.5, anchor="center")
    frame.lift()

def criar_historia(nome):
    texto = nome.get()
    print(texto)

def ocultar_frame(frame):
    frame.place_forget()