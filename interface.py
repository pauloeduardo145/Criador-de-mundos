import customtkinter as ctk
from widgets import *
import historias
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import shutil
import os
import storage
import uuid

ctk.set_appearance_mode("dark")

historico = []

data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")

historia_selecionada = None
capitulo_selecionado = None
personagem_selecionado = None
sistema_de_poder_selecionado = None
tela_anterior = None
caminho_imagem = None

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
frame_conteudo.grid_columnconfigure(1,weight=1)
frame_conteudo.grid_columnconfigure(2,weight=0)
frame_conteudo.grid_rowconfigure(0,weight=0)
frame_conteudo.grid_rowconfigure(1,weight=0)
frame_conteudo.grid_rowconfigure(2,weight=1)
frame_conteudo.grid_rowconfigure(3,weight=1)
frame_conteudo.grid(column=1, row=0, columnspan=5, rowspan=5, sticky="nsew",padx=5,pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0,columnspan=5, sticky="n",padx=5,pady=5)

#LABEL DO CONTEUDO

frame_lista_conteudo = ctk.CTkScrollableFrame(frame_conteudo,width=600,height=520)
frame_lista_conteudo.grid(column=0,row=2,columnspan=5, sticky="nsew",padx=10)
frame_lista_conteudo._scrollbar.configure(height=0)

#CONTEUDO DO HISTORIA

frame_botoes = ctk.CTkFrame(frame_conteudo,height=35)
frame_botoes.grid(column=0,row=3,sticky="w",padx=10,pady=5)

Addper = ctk.CTkButton(frame_botoes,height=25,text="[Criar Personagem]",command=lambda:histOria(janepers))
Addper.grid(column=0,row=3,sticky="w",padx=10,pady=10)

capitadic = ctk.CTkButton(frame_botoes,height=25,text="[Criar Capitulo]",command=lambda:histOria(janecapi))
capitadic.grid(column=1,row=3,sticky="w",padx=10,pady=10)

Addposis = ctk.CTkButton(frame_botoes,text="[Criar Sistema de Poder]",command=lambda: histOria(janesispoder))
Addposis.grid(column=2,row=3,)

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

criah = ctk.CTkButton(frame_historia, text="[Criar historias]",command=lambda:mostrar_frame(frame_nomeh))
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

id_historia = ctk.CTkLabel(lista,text='Id:')
id_historia.grid(column=0,row=1,sticky="w",padx=10,pady=1)

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

def navegar(funcao, *args):
    historico.append((funcao, args))
    funcao(*args)

def voltar():

    if len(historico) > 1:
        historico.pop()

        funcao, args = historico[-1]

        funcao(*args)



def selecionar_historia(historia):
    global historia_selecionada

    historia_selecionada = historia

    historia["ultima_edicao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    nome_historia.configure(text=f"Nome: {historia['nome']}")

    id_historia.configure(text=f"Id: {historia['id']}")

    arcos.configure(text=f"Arcos: {len(historia['arcos'])}")

    cap.configure(text=f"Capítulos: {len(historia['capitulos'])}")

    ue.configure(text=f"Ultima Edição: {historia.get('ultima_edicao', 'Nunca')}")

    pers.configure(text=f"Personagens: {len(historia['personagens'])}")
    
    if historia_selecionada["sistemas_poder"]:
        sp.configure(text=f"Sistema P: {historia_selecionada['sistemas_poder'][0]['nome']}")
    else:
        sp.configure(text="Sistema P: Nenhum")

    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    for historia in historias.Historias:
        if "id" not in historia:
            historia["id"] = str(uuid.uuid4())

    for personagem in historia["personagens"]:
        criar_label_personagem(
            personagem,
            frame_lista_conteudo,
            selecionar_personagem
        )

    for capitulo in historia["capitulos"]:
        criar_label_capitulo(
            capitulo,
            frame_lista_conteudo,
            selecionar_capitulo
        )
    
    for sistema in historia["sistemas_poder"]:
        criar_label_capitulo(
            sistema,
            frame_lista_conteudo,
            selecionar_sistemapoder
        )

def mostrar_todos_personagens():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    personagens = historia_selecionada.get("personagens", [])

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"📂 Todos os Personagens ({len(personagens)})",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    # 3. Cria um frame interno para organizar os personagens em grade (grid)
    # Isso evita que vire uma linha vertical gigante de 500 itens
    grid_personagens = ctk.CTkFrame(frame_lista_conteudo, fg_color="transparent")
    grid_personagens.pack(fill="both", expand=True, padx=20)

    # Configura o grid para ter, por exemplo, 4 colunas adaptáveis
    for i in range(4):
        grid_personagens.grid_rowconfigure(i, weight=1)

    # 4. Varre os 500 personagens usando o loop 'for'
    for indice, personagem in enumerate(historia_selecionada["personagens"]):
        # Calcula a linha e a coluna no grid com base no índice (ex: 4 por linha)
        linha = indice // 4
        coluna = indice % 4

        # Cria um pequeno card/botão para cada personagem
        botao_card = ctk.CTkButton(grid_personagens,text=personagem["nome"],height=40,
        # Usamos uma função lambda para que, ao clicar, abra a ficha dele
        command=lambda p=personagem: navegar(selecionar_personagem, p))
        botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

def edicao_capitulo():
    global capitulo_selecionado

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"Modo Edição",
        font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0,capitulo_selecionado["nome"])
    nome.pack(fill="x",padx=10,pady=5)

    conteudos = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    conteudos.insert("1.0", capitulo_selecionado["conteudo"])
    conteudos.pack(fill="x",padx=10,pady=5)

    def salvar_edicao():
        capitulo_selecionado["nome"] = nome.get()
        capitulo_selecionado["conteudo"] = conteudos.get("1.0","end-1c")

        historias.salvar_dados(historias.Historias)
        selecionar_capitulo(capitulo_selecionado)

    botao_salvar = ctk.CTkButton(frame_lista_conteudo,text="Salvar",command=lambda: salvar_edicao())
    botao_salvar.pack(pady=10)

def edicao_personagem():
    global personagem_selecionado

    global caminho_imagem

    caminho_imagem = None

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"Modo Edição",
        font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0,personagem_selecionado["nome"])
    nome.pack(fill="x",padx=10,pady=5)

    p = ctk.CTkLabel(frame_lista_conteudo,text="Personalidade:")
    p.pack(padx=10,pady=5)

    personalidade = ctk.CTkTextbox(frame_lista_conteudo,height=50,fg_color="#1E1E1E",text_color="white", border_color="gray")
    personalidade.pack(fill="x",pady=10,padx=5)
    personalidade.insert("1.0", personagem_selecionado["personalidade"])

    pe = ctk.CTkLabel(frame_lista_conteudo,text="Aparencia:")
    pe.pack(padx=10,pady=5) 

    aparencia = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    aparencia.pack(fill="x",pady=10,padx=5)
    aparencia.insert("1.0", personagem_selecionado["aparencia"])

    his = ctk.CTkLabel(frame_lista_conteudo,text="Historia:")
    his.pack(padx=10,pady=5)

    hispers = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    hispers.pack(fill="x",pady=10,padx=5)
    hispers.insert("1.0", personagem_selecionado["historia"])

    r = ctk.CTkLabel(frame_lista_conteudo,text="Relações:")
    r.pack(padx=10,pady=5)

    relacoes = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    relacoes.pack(fill="x",pady=10,padx=5)
    relacoes.insert("1.0", personagem_selecionado["relacoes"])

    po = ctk.CTkLabel(frame_lista_conteudo,text="Poderes:")
    po.pack(padx=10,pady=5)

    poderes = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    poderes.pack(fill="x",pady=10,padx=5)
    poderes.insert("1.0", personagem_selecionado["poderes"])

    ha = ctk.CTkLabel(frame_lista_conteudo,text="Habilidades:")
    ha.pack(padx=10,pady=5)

    hapers = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    hapers.pack(fill="x",pady=10,padx=5)
    hapers.insert("1.0", personagem_selecionado["habilidades"])

    # IMAGEM

    preview = ctk.CTkLabel(frame_lista_conteudo,text="[Clique para alterar imagem]")
    preview.pack(pady=10)

    def trocar_imagem():
        global caminho_imagem

        novo_caminho = filedialog.askopenfilename(title="Selecione uma imagem",filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),("Todos os arquivos", "*.*")])

        if not novo_caminho:
            return

        caminho_imagem = novo_caminho

        imagem_pil = Image.open(novo_caminho)
        imagem_pil.thumbnail((250,250))
        img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(imagem_pil.width, imagem_pil.height))

        preview.configure(image=img_ctk, text="")
        preview.image = img_ctk

    if personagem_selecionado.get("imagens"):
        try:
            imagem_pil = Image.open(personagem_selecionado["imagens"])

            imagem_pil.thumbnail((250, 250))

            img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(imagem_pil.width, imagem_pil.height))

            preview.configure(image=img_ctk, text="")
            preview.image = img_ctk

        except Exception as erro:
            print(f"Erro ao carregar imagem: {erro}")

    preview.bind("<Button-1>", lambda e: trocar_imagem())

    def salvar_edicao():
        global caminho_imagem

        personagem_selecionado["nome"] = nome.get()
        personagem_selecionado["personalidade"] = personalidade.get("1.0", "end-1c")
        personagem_selecionado["aparencia"] = aparencia.get("1.0", "end-1c")
        personagem_selecionado["historia"] = hispers.get("1.0","end-1c")
        personagem_selecionado["relacoes"] = relacoes.get("1.0", "end-1c")
        personagem_selecionado["poderes"] = poderes.get("1.0", "end-1c")
        personagem_selecionado["habilidades"] = hapers.get("1.0","end-1c")

        if caminho_imagem:

            imagem_antiga = personagem_selecionado.get("imagens")

            extensao = os.path.splitext(caminho_imagem)[1]

            novo_caminho = os.path.join(storage.IMAGENS,f"{personagem_selecionado['id']}{extensao}")

            # Copia primeiro
            shutil.copy2(caminho_imagem, novo_caminho)

            # Apaga a antiga apenas se for diferente da nova
            if imagem_antiga:

                nome_arquivo = os.path.basename(imagem_antiga)

                if nome_arquivo.startswith(personagem_selecionado["id"]):

                    if os.path.exists(imagem_antiga):
                        try:
                            os.remove(imagem_antiga)
                        except Exception as erro:
                            print(erro)

            personagem_selecionado["imagens"] = novo_caminho
            
        historias.salvar_dados(historias.Historias)

        caminho_imagem = None

        selecionar_personagem(personagem_selecionado)

    botao_salvar = ctk.CTkButton(frame_lista_conteudo,text="Salvar",command=lambda: salvar_edicao())
    botao_salvar.pack(pady=10)

def selecionar_personagem(personagem):
    global personagem_selecionado

    personagem_selecionado = personagem

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um label para o personagem
    for chave, valor in personagem.items():
        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda: edicao_personagem())
    edit.pack(pady=10)

    print(personagem["nome"])

def mostrar_todos_capitulos():
    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    capitulo = historia_selecionada.get("capitulos", [])

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"📂 Todos os Capitulos ({len(capitulo)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    # 3. Cria um frame interno para organizar os personagens em grade (grid)
    # Isso evita que vire uma linha vertical gigante de 500 itens
    grid_capitulos = ctk.CTkFrame(frame_lista_conteudo, fg_color="transparent")
    grid_capitulos.pack(fill="both", expand=True, padx=20)

    # Configura o grid para ter, por exemplo, 4 colunas adaptáveis
    for i in range(4):
        grid_capitulos.grid_rowconfigure(i, weight=1)

    # 4. Varre os 500 personagens usando o loop 'for'
    for indice, capitulo in enumerate(historia_selecionada["capitulos"]):
        # Calcula a linha e a coluna no grid com base no índice (ex: 4 por linha)
        linha = indice // 4
        coluna = indice % 4

        # Cria um pequeno card/botão para cada personagem
        botao_card = ctk.CTkButton(
            grid_capitulos,
            text=capitulo["nome"],
            height=40,
            # Usamos uma função lambda para que, ao clicar, abra a ficha dele
            command=lambda c=capitulo: navegar(selecionar_capitulo, c) 
        )
        botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

def selecionar_capitulo(capitulo):
    global capitulo_selecionado

    capitulo_selecionado = capitulo

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um label para o personagem
    for chave, valor in capitulo.items():
        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    print(capitulo["nome"])

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda: edicao_capitulo())
    edit.pack(pady=10)

#CAIXA

caixa_frame = ctk.CTkFrame(janela,width= 200,height=20)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,padx=10,pady=5)

botaofake = ctk.CTkButton(caixa_frame,height=10,text="butoon",fg_color="black",width=4,font=("Helvetica", 7))
botaofake.grid(column=0,row=0,sticky="n",padx=5,pady=5)

exit_button = ctk.CTkButton(caixa_frame,height=10,text='Exit',fg_color="black",width=4,font=("Helvetica", 7),command=lambda: janela.quit())
exit_button.grid(column=1,row=0,sticky="n",padx=5,pady=5)

label_config = ctk.CTkButton(caixa_frame,height=10,text="config",fg_color="black",width=4,font=("Helvetica", 7))
label_config.grid(column=2,row=0,sticky="n",padx=5,pady=5)

#CRIAR INTERFACE

frame_nomeh = ctk.CTkFrame(janela,fg_color="black",width=200, height=120)
frame_nomeh.grid_propagate(False)
frame_nomeh.grid_columnconfigure(0, weight=1)
frame_nomeh.grid_columnconfigure(1, weight=1)

frame_nomeh.place(relx=0.5, rely=0.5, anchor="center")
frame_nomeh.place_forget()

botaofake = ctk.CTkLabel(frame_nomeh,text="Criar Historia")
botaofake.grid(column=0,row=0,padx=10,pady=10,columnspan=2)

def enter_historia(events):
    criar_historia(nome.get())
    print(historias.Historias)
    print(len(historias.Historias))
    carregar_interface()
    ocultar_frame(frame_nomeh)

nome = ctk.CTkEntry(frame_nomeh,placeholder_text="Nome da Historia")
nome.bind("<Return>", enter_historia)
nome.grid(column=0,row=1,sticky="nsew",columnspan=2)
nome.focus()

criar_h = ctk.CTkButton(frame_nomeh,text="Criar Historia",command=lambda: (criar_historia(nome.get()),carregar_interface(),ocultar_frame(frame_nomeh),print(historias.Historias),print(len(historias.Historias))))
criar_h.grid(column=1,row=3,padx=5,pady=10,sticky="s")

f = ctk.CTkButton(frame_nomeh,text="Fechar",command=lambda: ocultar_frame(frame_nomeh))
f.grid(column=0,row=3,padx=5)

#JANELA CRIAR PERSONAGEM (ESTA CONCLUIDO).

def salvar_personagem():
    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    novo = criar_personagem(
    historia_selecionada,
    personame.get(),
    caminho_imagem,
    personapersona.get("1.0","end-1c"),
    persoapare.get("1.0","end-1c"),
    relaca.get("1.0","end-1c"),
    hispertex.get("1.0","end-1c"),
    poderes.get("1.0","end-1c"),
    habpertex.get("1.0","end-1c")
    )

    if caminho_imagem:
        extensao = os.path.splitext(caminho_imagem)[1]

        novo_caminho = os.path.join(storage.IMAGENS,f"{novo['id']}{extensao}")

        shutil.copy2(caminho_imagem, novo_caminho)

        novo["imagens"] = novo_caminho

    if novo:
        criar_label_personagem(novo,frame_lista_conteudo,selecionar_personagem)

        selecionar_historia(historia_selecionada)
        ocultar_frame(janepers)

def enter_personagem(event):
    salvar_personagem()

janepers = ctk.CTkFrame(janela,width=600,height=500)
janepers.grid_propagate(False)
janepers.grid_columnconfigure(0, weight=1)
janepers.grid_columnconfigure(1, weight=0)
janepers.grid_columnconfigure(2, weight=1)
janepers.grid_rowconfigure(0,weight=1)
janepers.grid_rowconfigure(1,weight=1)
janepers.grid_rowconfigure(2,weight=1)
janepers.grid_rowconfigure(3,weight=0)
janepers.grid_rowconfigure(4,weight=0)
janepers.grid_rowconfigure(5,weight=1)
janepers.grid_rowconfigure(6,weight=1)

janepers.place(relx=0.5, rely=0.5, anchor="center")
janepers.place_forget()

def imagem():
    global caminho_imagem

    caminho_imagem = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[
            ("Imagens", "*.png *.jpg *.jpeg *.webp"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho_imagem:
        return

    imagem_pil = Image.open(caminho_imagem)

    imagem_pil.thumbnail((250, 250))

    largura = imagem_pil.width
    altura = imagem_pil.height

    img_ctk = ctk.CTkImage(
    light_image=imagem_pil,
    dark_image=imagem_pil,
    size=(largura,altura)
    )

    preview.configure(image=img_ctk, text="")
    preview.image = img_ctk

preview = ctk.CTkLabel(janepers,text="[Clique para importar imagem]")
preview.grid(column=0, row=1, rowspan=3)
preview.bind("<Button-1>", lambda e: imagem())

perso = ctk.CTkLabel(janepers,text="Nome: ")
perso.grid(column=1,row=0)

personame = ctk.CTkEntry(janepers,placeholder_text="Insira o nome do personagem")
personame.bind("<Return>", enter_personagem)
personame.grid(column=2,row=0,sticky="we")
personame.focus()

personali = ctk.CTkLabel(janepers,text="Personalidade: ")
personali.grid(column=1,row=1)

personapersona = ctk.CTkTextbox(janepers,height=50)
personapersona.grid(column=2,row=1, sticky="we")

apa = ctk.CTkLabel(janepers,text="Aparencia: ")
apa.grid(column=1,row=2)

persoapare = ctk.CTkTextbox(janepers,height=50)
persoapare.grid(column=2,row=2, sticky="we")

rela = ctk.CTkLabel(janepers,text="Relações")
rela.grid(column=1, row=3)

relaca = ctk.CTkTextbox(janepers,height=50)
relaca.grid(column=2,row=3, sticky="we")

relabel =ctk.CTkLabel(janepers,text="Separe com ';', Ex: Esposa de X; Amiga de X",font=("Helvetica", 11))
relabel.grid(column=2,row=4, sticky="w")

hisper = ctk.CTkLabel(janepers,text=f"Historia do personagem")
hisper.grid(column=1,row=5)

hispertex = ctk.CTkTextbox(janepers,height=50)
hispertex.grid(column=2,row=5, sticky="we")

podelabel = ctk.CTkLabel(janepers,text="Poderes:")
podelabel.grid(column=1, row=6)

poderes = ctk.CTkTextbox(janepers,height=50)
poderes.grid(column=2,row=6, sticky="we")

habper = ctk.CTkLabel(janepers,text=f"Habilidades do personagem")
habper.grid(column=1,row=7)

habpertex = ctk.CTkTextbox(janepers,height=50)
habpertex.grid(column=2,row=7, sticky="we")

fecharperso = ctk.CTkButton(janepers,text="[Fechar]",command=lambda: ocultar_frame(janepers))
fecharperso.grid(column=1,row=8, sticky="se",pady=10,padx=10)

salvarperso = ctk.CTkButton(janepers,text="[Salvar Personagem]",command=lambda: salvar_personagem())
salvarperso.grid(column=2,row=8, sticky="se",pady=10,padx=10)


#JANELA CRIAR CAPITULO

def enter_capitulo(event):
    salvar_capitulo()

def salvar_capitulo():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return
    
    novo = criar_capitulo(
        historia_selecionada,
        capiname.get(),
        capiconteudo.get("1.0", "end-1c")
    )

    if novo:

        criar_label_capitulo(
            novo,
            frame_lista_conteudo,
            selecionar_capitulo
        )

        selecionar_capitulo(novo)

        ocultar_frame(janecapi)
        print(capiconteudo.get("1.0", "end-1c"))

janecapi = ctk.CTkFrame(janela,width=300,height=220)
janecapi.grid_propagate(False)
janecapi.grid_columnconfigure(0, weight=1)
janecapi.grid_rowconfigure(0,weight=0)
janecapi.grid_rowconfigure(1,weight=1)
janecapi.grid_rowconfigure(2,weight=1)
janecapi.grid_rowconfigure(3,weight=1)
janecapi.grid_rowconfigure(4,weight=1)

janecapi.place(relx=0.5, rely=0.5, anchor="center")
janecapi.place_forget()

capi = ctk.CTkLabel(janecapi,text="Insira abaixo o Capitulo")
capi.grid(column=0,row=0,columnspan=2)

capiname = ctk.CTkEntry(janecapi,placeholder_text="Nome do capítulo")
capiname.grid(column=0,row=1,sticky="nsew",columnspan=2)

capiconteudo = ctk.CTkTextbox(janecapi, width=300, height=150, activate_scrollbars=True)
capiconteudo.focus()
capiconteudo.bind("<Return>", enter_capitulo)
capiconteudo.grid(column=0,row=2,sticky="nsew",columnspan=2)

fecharsalvar = ctk.CTkButton(janecapi,text="[Fechar]",command=lambda: ocultar_frame(janecapi))
fecharsalvar.grid(column=0,row=3)

salvarcapit = ctk.CTkButton(janecapi,text="[Criar Capitulo]",command=lambda: salvar_capitulo())
salvarcapit.grid(column=1,row=3,columnspan=2)

#JANELA CRIAR SISTEMA DE PODERES

def mostrar_todos_sistemas_poder():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    sistemapoder = historia_selecionada["sistemas_poder"]

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"📂 Todos os sistemas de poder ({len(sistemapoder)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    # 3. Cria um frame interno para organizar os personagens em grade (grid)
    # Isso evita que vire uma linha vertical gigante de 500 itens
    grid_sistem = ctk.CTkFrame(frame_lista_conteudo, fg_color="transparent")
    grid_sistem.pack(fill="both", expand=True, padx=20)

    # Configura o grid para ter, por exemplo, 4 colunas adaptáveis
    for i in range(4):
        grid_sistem.grid_rowconfigure(i, weight=1)

    # 4. Varre os 500 personagens usando o loop 'for'
    for indice, sistemapoder in enumerate(historia_selecionada["sistemas_poder"]):
        # Calcula a linha e a coluna no grid com base no índice (ex: 4 por linha)
        linha = indice // 4
        coluna = indice % 4

        # Cria um pequeno card/botão para cada personagem
        botao_card = ctk.CTkButton(
            grid_sistem,
            text=sistemapoder["nome"],
            height=40,
            # Usamos uma função lambda para que, ao clicar, abra a ficha dele
            command=lambda s=sistemapoder: navegar(selecionar_sistemapoder, s) 
        )
        botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

def selecionar_sistemapoder(sistemapode):
    global sistema_de_poder_selecionado

    sistema_de_poder_selecionado = sistemapode

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um label para o personagem
    for chave, valor in sistemapode.items():
        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    print(sistemapode["nome"])

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda: edicao_sistempoder())
    edit.pack(pady=10)

def salvar_sistema_de_poder():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    novo = criar_sistemadepoder(
        historia_selecionada,
        powename.get(),
        powerconteudo.get("1.0", "end-1c"),
        regras.get("1.0", "end-1c"),
        vantagens.get("1.0", "end-1c"),fraquezas.get("1.0", "end-1c"))

    if novo:

        criar_label_sistema_poder(
            novo,
            frame_lista_conteudo,
            selecionar_sistemapoder)

        selecionar_sistemapoder(novo)

        ocultar_frame(janesispoder)

        print(novo)

def edicao_sistempoder():
    global sistema_de_poder_selecionado

    if sistema_de_poder_selecionado is None:
        print("Nenhum sistema de poder selecionado")
        return

    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    titulo = ctk.CTkLabel(frame_lista_conteudo,text="Modo Edição",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    # Nome

    ctk.CTkLabel(frame_lista_conteudo,text="Nome:").pack(anchor="w", padx=10)
    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0,sistema_de_poder_selecionado["nome"])
    nome.pack(fill="x", padx=10, pady=5)

    # Descrição

    ctk.CTkLabel(frame_lista_conteudo,text="Descrição:").pack(anchor="w", padx=10)

    descricao = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    descricao.insert("1.0",sistema_de_poder_selecionado["descricao"])
    descricao.pack(fill="x", padx=10, pady=5)

    # Regras

    ctk.CTkLabel(frame_lista_conteudo,text="Regras:").pack(anchor="w", padx=10)

    regras = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    regras.insert("1.0",sistema_de_poder_selecionado["regras"])
    regras.pack(fill="x", padx=10, pady=5)

    # Vantagens

    ctk.CTkLabel(
        frame_lista_conteudo,text="Vantagens:").pack(anchor="w", padx=10)
    
    vantagens = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    vantagens.insert("1.0",sistema_de_poder_selecionado["vantagens"])
    vantagens.pack(fill="x", padx=10, pady=5)

    # Fraquezas

    ctk.CTkLabel(frame_lista_conteudo,text="Fraquezas:").pack(anchor="w", padx=10)

    fraquezas = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    fraquezas.insert("1.0",sistema_de_poder_selecionado["fraquezas"])
    fraquezas.pack(fill="x", padx=10, pady=5)

    def salvar_edicao():

        sistema_de_poder_selecionado["nome"] = nome.get()
        sistema_de_poder_selecionado["descricao"] = descricao.get("1.0","end-1c")
        sistema_de_poder_selecionado["regras"] = regras.get("1.0","end-1c")
        sistema_de_poder_selecionado["vantagens"] = vantagens.get("1.0","end-1c")
        sistema_de_poder_selecionado["fraquezas"] = fraquezas.get("1.0","end-1c")

        historias.salvar_dados(historias.Historias)

        selecionar_sistemapoder(sistema_de_poder_selecionado)

    botao_salvar = ctk.CTkButton(frame_lista_conteudo,text="Salvar",command=lambda: salvar_edicao())
    botao_salvar.pack(pady=10)

janesispoder = ctk.CTkFrame(janela,width=600,height=500)
janesispoder.grid_propagate(False)
janesispoder.grid_columnconfigure(0,weight=0)
janesispoder.grid_columnconfigure(1,weight=1)
janesispoder.grid_rowconfigure(0,weight=1)
janesispoder.grid_rowconfigure(1,weight=1)
janesispoder.grid_rowconfigure(2,weight=1)
janesispoder.grid_rowconfigure(3,weight=1)
janesispoder.grid_rowconfigure(4,weight=1)
janesispoder.grid_rowconfigure(5,weight=1)

powerlabel = ctk.CTkLabel(janesispoder,text="Adicionar sistema de poderes")
powerlabel.grid(column=0,row=0,columnspan=2)

powerlabename = ctk.CTkLabel(janesispoder,text="Nome: ")
powerlabename.grid(column=0,row=1)

powename = ctk.CTkEntry(janesispoder,placeholder_text="Nome do sistema de poder")
powename.grid(column=1,row=1,columnspan=2,sticky="ew")

powerlabelconteudo = ctk.CTkLabel(janesispoder,text="Conteudo:")
powerlabelconteudo.grid(column=0,row=2)

powerconteudo = ctk.CTkTextbox(janesispoder,height=50, activate_scrollbars=True)
powerconteudo.grid(column=1,row=2,sticky="ew",columnspan=2)

powerlabelregras = ctk.CTkLabel(janesispoder,text="Regras:")
powerlabelregras.grid(column=0,row=3)

regras = ctk.CTkTextbox(janesispoder,width=300,height=50,activate_scrollbars=True)
regras.grid(column=1,row=3,sticky="ew",columnspan=2)

powerlabelvantagens = ctk.CTkLabel(janesispoder,text="Vantagens:")
powerlabelvantagens.grid(column=0,row=4)

vantagens = ctk.CTkTextbox(janesispoder,height=50,activate_scrollbars=True)
vantagens.grid(column=1,row=4,sticky="ew",columnspan=2)

powerlabelfraquezas = ctk.CTkLabel(janesispoder,text="Fraquezas:")
powerlabelfraquezas.grid(column=0,row=5)

fraquezas = ctk.CTkTextbox(janesispoder,height=50,activate_scrollbars=True)
fraquezas.grid(column=1,row=5,sticky="ew",columnspan=2)


powerfechar = ctk.CTkButton(janesispoder,text="[Fechar]", command=lambda: ocultar_frame(janesispoder))
powerfechar.grid(column=0,row=6)

powersalvar = ctk.CTkButton(janesispoder,text="[Criar Sistema de poder]",command=lambda: salvar_sistema_de_poder())
powersalvar.grid(column=1,row=6)

#MOSTRAR NO CONTEUDO

def excluir():
    global personagem_selecionado
    if personagem_selecionado == None:
        print("Selecione um personagem")
    else:
        print(f"Excluindo o personagem {personagem_selecionado["nome"]}")

lista_conteudo = ctk.CTkFrame(frame_conteudo,width=200,height=40)
lista_conteudo.grid_columnconfigure(0,weight=1)
lista_conteudo.grid_columnconfigure(1,weight=1)
lista_conteudo.grid_columnconfigure(2,weight=1)
lista_conteudo.grid_columnconfigure(3,weight=1)
lista_conteudo.grid_rowconfigure(0,weight=1)
lista_conteudo.grid(column=0,row=1,sticky="n",columnspan=5,pady=5)

botao_voltar = ctk.CTkButton(lista_conteudo,text="← Voltar",command=lambda: voltar())
botao_voltar.grid(column=0, row=0,sticky="n", padx=5, pady=5)

botao_pers= ctk.CTkButton(lista_conteudo, text="Personagem",command=lambda: navegar(mostrar_todos_personagens))
botao_pers.grid(column=1,row=0,sticky="n",padx=5,pady=5)

botao_capi= ctk.CTkButton(lista_conteudo, text="Capitulo",command=lambda: navegar(mostrar_todos_capitulos))
botao_capi.grid(column=2,row=0,sticky="n",padx=5,pady=5)

botao_arco= ctk.CTkButton(lista_conteudo, text="Arco",command=lambda: print("Arco"))
botao_arco.grid(column=3,row=0,sticky="n",padx=5,pady=5)

botao_image= ctk.CTkButton(lista_conteudo, text="Imagens",command=lambda: print("Imagens"))
botao_image.grid(column=4,row=0,sticky="n",padx=5,pady=5)

botao_sispower = ctk.CTkButton(lista_conteudo,text="Sistema de pd",command=lambda: navegar(mostrar_todos_sistemas_poder))
botao_sispower.grid(column=5,row=0,sticky="n",padx=5,pady=5)

botao_obser = ctk.CTkButton(lista_conteudo,text="Observação",command=lambda: print("Observação"))
botao_obser.grid(column=6,row=0,sticky="n",padx=5,pady=5)

botao_excluir= ctk.CTkButton(lista_conteudo,text="Excluir",command=lambda: excluir())
botao_excluir.grid(column=7,row=0,sticky="n",padx=5,pady=5)

carregar_interface()


janela.mainloop()