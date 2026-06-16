import customtkinter as ctk
from widgets import mostrar_frame,criar_historia, ocultar_frame,criar_label,criar_personagem,criar_label_personagem, criar_capitulo,criar_label_capitulo
import historias

ctk.set_appearance_mode("dark")

historia_selecionada = None
capitulo_selecionado = None
personagem_selecionado = None


def histOria(frame):
    if historia_selecionada is None:
        print("Selecione a historia primeiro")
    else:
        mostrar_frame(frame)
        frame.focus()

#JANELAS

janela = ctk.CTk()
janela.title("Criador de Mundos")
janela.geometry("1200x1200")
janela.attributes('-fullscreen', True)
janela.bind('<Escape>', lambda e: janela.attributes('-fullscreen', False))
janela.grid_columnconfigure(1, weight=1)
janela.grid_rowconfigure(1,weight=1)

#CONTEUDO


def carregar_interface():

    for widget in frame_lista.winfo_children():
        widget.destroy()

    for indice, historia in enumerate(historias.Historias):

        criar_label(
            historia,
            frame_lista,
            selecionar_historia,
            row=indice
        )

frame_conteudo = ctk.CTkFrame(janela)
#frame_conteudo.grid_propagate(False)
frame_conteudo.grid_columnconfigure(0,weight=1)
frame_conteudo.grid_rowconfigure(0,weight=0)
frame_conteudo.grid_rowconfigure(1,weight=2)
frame_conteudo.grid_rowconfigure(2,weight=0)
frame_conteudo.grid(column=1, row=0, columnspan=5, rowspan=5, sticky="nsew",padx=5,pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0, sticky="n",padx=5,pady=5)

#LABEL DO CONTEUDO

frame_lista_conteudo = ctk.CTkScrollableFrame(frame_conteudo,width=600,height=550)
frame_lista_conteudo.grid(column=0,row=1,columnspan=5, sticky="nsew",padx=10,pady=5)
frame_lista_conteudo._scrollbar.configure(height=0)

#CONTEUDO DO HISTORIA

Addper = ctk.CTkButton(frame_conteudo,height=15,text="[Criar Personagem]",
                       command=lambda:histOria(janepers))
Addper.grid(column=0,row=2,sticky="w",padx=10,pady=10)

capitadic = ctk.CTkButton(frame_conteudo,height=15,text="[Criar Arco]",
                          command=lambda:histOria(janecapi))
capitadic.grid(column=1,row=2,sticky="w",padx=10,pady=10)

#HISTORIAS

frame_historia = ctk.CTkFrame(janela,width=200,height=400)
frame_historia.grid_propagate(False)
frame_historia.grid_columnconfigure(0,weight=1)
frame_historia.grid_rowconfigure(0,weight=1)
frame_historia.grid_rowconfigure(1,weight=2)
frame_historia.grid_rowconfigure(2,weight=2)
frame_historia.grid_rowconfigure(3,weight=1)
frame_historia.grid(column=0,row=1, padx=10,pady=5)

menu = ctk.CTkLabel(frame_historia,text='HISTÓRIAS')
menu.grid(column=0,row=0,sticky="n",padx=10,pady=5)

criah = ctk.CTkButton(frame_historia, text="[Criar historias]",
                      command=lambda:mostrar_frame(frame_nomeh))
criah.grid(column=0,row=2,sticky="s",padx=10,pady=6)

#LABEL DO HISTORIA

frame_lista = ctk.CTkScrollableFrame(frame_historia,height=220)
frame_lista.grid_columnconfigure(0,weight=1)
frame_lista.grid_rowconfigure(0,weight=0)
frame_lista.grid(column=0,row=1,sticky="n",padx=10,pady=5)
frame_lista._scrollbar.configure(height=0)

#INFORMAÇÕES

frame_inf = ctk.CTkFrame(janela,width=200,height=300)
frame_inf.grid_propagate(False)
frame_inf.grid_columnconfigure(0,weight=1)
frame_inf.grid_rowconfigure(0,weight=1)
frame_inf.grid(column=0,row=2,padx=10,pady=5)

inicio = ctk.CTkLabel(frame_inf,text='INFORMAÇÕES')
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=10)

lista = ctk.CTkFrame(frame_inf,width=200,height=250)
lista.grid_propagate(False)
lista.grid_columnconfigure(0,weight=1)
lista.grid_rowconfigure(0,weight=0)
lista.grid_rowconfigure(0,weight=0)
lista.grid_rowconfigure(2,weight=0)
lista.grid_rowconfigure(3,weight=0)
lista.grid_rowconfigure(4,weight=0)
lista.grid_rowconfigure(5,weight=0)
lista.grid_rowconfigure(6,weight=0)
lista.grid(column=0,row=2,sticky="n",padx=10,pady=5)

#LABELS DO INFORMAÇÕES
nome_historia = ctk.CTkLabel(lista,text='Nome:')
nome_historia.grid(column=0,row=0,sticky="w",padx=10,pady=5)

arcos = ctk.CTkLabel(lista,text='Arcos:')
arcos.grid(column=0,row=2,sticky="w",padx=10,pady=5)

cap = ctk.CTkLabel(lista,text='Capitulos:')
cap.grid(column=0,row=3,sticky="w",padx=10,pady=5)

pers = ctk.CTkLabel(lista,text='Personagens:')
pers.grid(column=0,row=4,sticky="w",padx=10,pady=5)

ue = ctk.CTkLabel(lista,text='Ultima Edição:')
ue.grid(column=0,row=5,sticky="w",padx=10,pady=5)

sp = ctk.CTkLabel(lista,text='Sistema(as) de Poder(es):')
sp.grid(column=0,row=6,sticky="w",padx=10,pady=5)

#RECEBER INFORMAÇÕES DA HISTORIA SELECIONADA 

def selecionar_historia(historia):
    global historia_selecionada

    historia_selecionada = historia

    nome_historia.configure(text=f"Nome: {historia['nome']}")

    arcos.configure(text=f"Arcos: {len(historia['arcos'])}")

    cap.configure(text=f"Capítulos: {len(historia['capitulos'])}")

    pers.configure(text=f"Personagens: {len(historia['personagens'])}")
    
    sp.configure(text=f"Sistemas P: {historia['sistemas_poder']}")

    # Limpa os personagens exibidos
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # Recria os personagens da história
    for personagem in historia["personagens"]:
        criar_label_personagem(
            personagem,
            frame_lista_conteudo,
            selecionar_personagem
        )

def selecionar_personagem(personagem):
    global personagem_selecionado

    personagem_selecionado = personagem

    print(personagem["nome"])

def selecionar_capitulo(capitulo):
    global capitulo_selecionado

    capitulo_selecionado = capitulo

    print(capitulo["nome"])

#CAIXA

caixa_frame = ctk.CTkFrame(janela,width= 200,height=20)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,padx=10,pady=5)

botaofake = ctk.CTkButton(caixa_frame,height=10,text="butoon",fg_color="black",width=4,font=("Helvetica", 7))
botaofake.grid(column=0,row=0,sticky="n",padx=5,pady=5)

label_config = ctk.CTkButton(caixa_frame,height=10,text="config",fg_color="black",width=4,font=("Helvetica", 7))
label_config.grid(column=1,row=0,sticky="n",padx=5,pady=5)

#CRIAR INTERFACE

frame_nomeh = ctk.CTkFrame(janela,fg_color="black",width=200, height=150)
frame_nomeh.grid_propagate(False)
frame_nomeh.grid_columnconfigure(0, weight=1)

frame_nomeh.place(relx=0.5, rely=0.5, anchor="center")
frame_nomeh.place_forget()

botaofake = ctk.CTkLabel(frame_nomeh,text="Criar historia")
botaofake.grid(column=0,row=1,padx=10,pady=10)

def enter_historia(events):
    criar_historia(nome.get())
    print(historias.Historias)
    print(len(historias.Historias))
    carregar_interface()
    ocultar_frame(frame_nomeh)

nome = ctk.CTkEntry(frame_nomeh)
nome.bind("<Return>", enter_historia)
nome.grid(column=0,row=2)
nome.focus()

criar_h = ctk.CTkButton(frame_nomeh,text="Criar",command=lambda: (criar_historia(nome.get()),carregar_interface(),ocultar_frame(frame_nomeh),print(historias.Historias),print(len(historias.Historias))))
criar_h.grid(column=0,row=3,padx=10,pady=10,sticky="s")

#JANELA CRIAR PERSONAGEM

def salvar_personagem():
    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    novo = criar_personagem(historia_selecionada, personame.get())

    if novo:
        criar_label_personagem(
            novo,
            frame_lista_conteudo,
            selecionar_personagem
        )

        selecionar_historia(historia_selecionada)
        ocultar_frame(janepers)

def enter_personagem(event):
    salvar_personagem()


janepers = ctk.CTkFrame(janela,width=600,height=400)
janepers.grid_propagate(False)
janepers.grid_columnconfigure(0, weight=1)
janepers.grid_columnconfigure(1, weight=1)
janepers.grid_rowconfigure(0,weight=0)
janepers.grid_rowconfigure(1,weight=0)


janepers.place(relx=0.5, rely=0.5, anchor="center")
janepers.place_forget()

perso = ctk.CTkLabel(janepers,text="Insira abaixo o nome do personagem")
perso.grid(column=1,row=0)

personame = ctk.CTkEntry(janepers)
personame.bind("<Return>", enter_personagem)
personame.grid(column=1,row=1)
personame.focus()

salvarperso = ctk.CTkButton(janepers,text="[Salvar Personagem]",command=lambda: salvar_personagem())
salvarperso.grid(column=1,row=4)

#JANELA CRIAR CAPITULO

def salvar_capitulo():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    novo = criar_capitulo(
        historia_selecionada,
        capiname.get()
    )

    if novo:

        criar_label_capitulo(
            novo,
            frame_lista_conteudo,
            selecionar_capitulo
        )

        selecionar_capitulo(novo)

        ocultar_frame(janecapi)

janecapi = ctk.CTkFrame(janela,width=600,height=400)
janecapi.grid_propagate(False)
janecapi.grid_columnconfigure(0, weight=1)
janecapi.grid_columnconfigure(1, weight=1)
janecapi.grid_rowconfigure(0,weight=0)
janecapi.grid_rowconfigure(1,weight=0)

janecapi.place(relx=0.5, rely=0.5, anchor="center")
janecapi.place_forget()

capi = ctk.CTkLabel(janecapi,text="Insira abaixo o nome do personagem")
capi.grid(column=1,row=0)

capiname = ctk.CTkEntry(janecapi)
capiname.focus()
capiname.bind("<Return>", None)
capiname.grid(column=1,row=1)

salvarcapit = ctk.CTkButton(janecapi,text="[Criar Capitulo]",command=lambda: salvar_capitulo())
salvarcapit.grid(column=1,row=4)

carregar_interface()

janela.mainloop()