import customtkinter as ctk
from widgets import *
import historias
import uuid
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import shutil
import os
import storage
from tkinter import messagebox
import platform

ctk.set_appearance_mode("dark")

historico = []

data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")

historia_selecionada = None
capitulo_selecionado = None
personagem_selecionado = None
sistema_de_poder_selecionado = None
observacoes_selecionado = None
tela_anterior = None
caminho_imagem = None
galeria_imagens = None


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

frame_lista_conteudo = ctk.CTkScrollableFrame(frame_conteudo,width=600,height=520,orientation="vertical")
frame_lista_conteudo.grid(column=0,row=2,columnspan=5, sticky="nsew",padx=10)
#frame_lista_conteudo._scrollbar.configure(height=0)

#CONTEUDO DO HISTORIA

frame_botoes = ctk.CTkFrame(frame_conteudo,height=35)
frame_botoes.grid(column=0,row=3,sticky="w",padx=10,pady=5)

Addper = ctk.CTkButton(frame_botoes,height=25,text="[Criar Personagem]",command=lambda:histOria(janepers))
Addper.grid(column=0,row=3,sticky="w",padx=10,pady=10)

capitadic = ctk.CTkButton(frame_botoes,height=25,text="[Criar Capitulo]",command=lambda:histOria(janecapi))
capitadic.grid(column=1,row=3,sticky="w",padx=10,pady=10)

Addposis = ctk.CTkButton(frame_botoes,text="[Criar Sistema de Poder]",command=lambda: histOria(janesispoder))
Addposis.grid(column=2,row=3,)

Addobs = ctk.CTkButton(frame_botoes,text="[Adicionar observações]", command=lambda: (atualizar_optionmenu_personagens(),histOria(janeobser)))
Addobs.grid(column=3,row=3, sticky="w",padx=10,pady=10)

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
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=5)

lista = ctk.CTkFrame(frame_inf,width=220,height=250)
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

cap = ctk.CTkLabel(lista,text='Capitulos:')
cap.grid(column=0,row=2,sticky="w",padx=10,pady=5)

pers = ctk.CTkLabel(lista,text='Personagens:')
pers.grid(column=0,row=3,sticky="w",padx=10,pady=5)

ue = ctk.CTkLabel(lista,text='Ultima Edição:')
ue.grid(column=0,row=4,sticky="w",padx=10,pady=5)

sp = ctk.CTkLabel(lista,text='Sistema(as) de Poder(es):')
sp.grid(column=0,row=5,sticky="w",padx=10,pady=5)

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

    cap.configure(text=f"Capítulos: {len(historia['capitulos'])}")

    ue.configure(text=f"UE: {historia.get('ultima_edicao', 'Nunca')}")

    pers.configure(text=f"Personagens: {len(historia['personagens'])}")
    
    if historia_selecionada["sistemas_poder"]:
        sp.configure(text=f"Sistema P: {historia_selecionada['sistemas_poder'][0]['nome']}")
    else:
        sp.configure(text="Sistema P: Nenhum")


    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

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
        criar_label_sistema_poder(
            sistema,
            frame_lista_conteudo,
            selecionar_sistemapoder
        )

def mostrar_todas_imagens_da_galeria():
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    personagens = [
        p for p in historia_selecionada["personagens"]
        if len(p.get("galeria", [])) > 0
    ]

    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"Personagens com Galeria ({len(personagens)})",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10)

    for personagem in personagens:
        btn = ctk.CTkButton(frame_lista_conteudo,text=personagem["nome"],command=lambda p=personagem: abrir_galeria_personagem(p))
        btn.pack(pady=5)

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

    if "galeria" not in personagem_selecionado:
        personagem_selecionado["galeria"] = []

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"Modo Edição",font=("Helvetica", 18, "bold"))
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

    fraq = ctk.CTkLabel(frame_lista_conteudo,text="Fraquezas:")
    fraq.pack(padx=10,pady=5)

    fraqueza = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    fraqueza.pack(fill="x",pady=10,padx=5)
    fraqueza.insert("1.0", personagem_selecionado["fraquezas"])

    ha = ctk.CTkLabel(frame_lista_conteudo,text="Habilidades:")
    ha.pack(padx=10,pady=5)

    hapers = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    hapers.pack(fill="x",pady=10,padx=5)
    hapers.insert("1.0", personagem_selecionado["habilidades"])

    # IMAGEM

    preview = ctk.CTkLabel(frame_lista_conteudo,text="[Clique para alterar imagem]")
    preview.pack(pady=10)

    ctk.CTkLabel(frame_lista_conteudo, text="Galeria do personagem").pack(pady=(15, 5))

    frame_galeria = ctk.CTkFrame(frame_lista_conteudo)
    frame_galeria.pack(fill="x", padx=10, pady=5)

    def atualizar_galeria():
        for widget in frame_galeria.winfo_children():
            widget.destroy()

        for indice, item in enumerate(personagem_selecionado.get("galeria", [])):

            caminho = item.get("caminho")
            descricao = item.get("descricao", "")

            try:
                img = Image.open(caminho)
                img.thumbnail((100, 100))

                img_ctk = ctk.CTkImage(light_image=img,dark_image=img,size=(img.width, img.height))

                card = ctk.CTkFrame(frame_galeria)
                card.grid(row=indice // 4, column=indice % 4, padx=5, pady=5)

                label = ctk.CTkLabel(card, image=img_ctk, text="")
                label.image = img_ctk
                label.pack()

                ctk.CTkLabel(card, text=descricao, wraplength=100).pack()

                ctk.CTkButton(card,text="Remover",width=80,command=lambda i=item: remover_da_galeria(i)).pack(pady=2)

            except Exception as erro:
                print(erro)
    

    def adicionar_na_galeria():

        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),
                    ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        janela_desc = ctk.CTkInputDialog(text="Digite a descrição da imagem:",title="Descrição da Galeria")

        descricao = janela_desc.get_input()

        if descricao is None:
            descricao = ""

        if "galeria" not in personagem_selecionado:
            personagem_selecionado["galeria"] = []

        extensao = os.path.splitext(caminho)[1]

        nome_arquivo = f"{uuid.uuid4()}{extensao}"

        novo_caminho = os.path.join(storage.PASTA_GALERIA,nome_arquivo)

        shutil.copy2(caminho, novo_caminho)

        personagem_selecionado["galeria"].append({"caminho": novo_caminho,"descricao": descricao})

        atualizar_galeria()

    atualizar_galeria()

    def remover_da_galeria(item):

        confirmar = messagebox.askyesno("Remover imagem","Deseja remover esta imagem da galeria?")

        if not confirmar:
            return

        caminho = item.get("caminho")

        personagem_selecionado["galeria"].remove(item)

        if caminho and os.path.exists(caminho):
            try:
                os.remove(caminho)
            except Exception as erro:
                print(f"Erro ao apagar arquivo: {erro}")
        
        historias.salvar_dados(historias.Historias)
        atualizar_galeria()

    ctk.CTkButton(frame_lista_conteudo,text="Adicionar imagem à galeria",command=lambda: adicionar_na_galeria()).pack(pady=5)

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
        personagem_selecionado["fraquezas"] = fraqueza.get("1.0","end-1c")
        personagem_selecionado["habilidades"] = hapers.get("1.0","end-1c")


        if caminho_imagem:

            imagem_antiga = personagem_selecionado.get("imagens")

            extensao = os.path.splitext(caminho_imagem)[1]

            novo_caminho = os.path.join(storage.PASTA_IMAGENS,f"{personagem_selecionado['id']}{extensao}")

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

        atualizar_galeria()

        historias.salvar_dados(historias.Historias)

        caminho_imagem = None

        selecionar_personagem(personagem_selecionado)

    def fechar_sem_salvar():
        confirmar = messagebox.askyesno("Cancelar edição","Deseja sair sem salvar as alterações?")

        if confirmar:
                selecionar_personagem(personagem_selecionado)

    botao_salvar = ctk.CTkButton(frame_lista_conteudo,text="Salvar",command=lambda: salvar_edicao())
    botao_salvar.pack(pady=10)

    botao_fechar = ctk.CTkButton(frame_lista_conteudo,text="Fechar sem salvar",command=fechar_sem_salvar)
    botao_fechar.pack(pady=10)

def selecionar_personagem(personagem):
    global personagem_selecionado

    personagem_selecionado = personagem

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    linha = 0

    frame_imagem = ctk.CTkFrame(frame_lista_conteudo)
    frame_imagem.grid(row=0, column=0, sticky="n" ,padx=20)

    frame_info = ctk.CTkFrame(frame_lista_conteudo,width=600)
    frame_info.grid_columnconfigure(1, weight=1)
    frame_info.grid(row=0, column=1, sticky="nsew", padx=20)
    #frame_info.grid_propagate(False)

    if personagem.get("imagens"):
        imagem_pil = Image.open(personagem["imagens"])
        imagem_pil.thumbnail((250, 250))

        img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(imagem_pil.width, imagem_pil.height))

        foto = ctk.CTkLabel(frame_imagem, image=img_ctk, text="")
        foto.image = img_ctk
        foto.grid()

    # 2. Cria um label para o personagem
    for chave, valor in personagem.items():
        
        if chave in ["imagens", "galeria", "id", "historia_id"]:
            continue
        
        ctk.CTkLabel(frame_info,text=f"{chave}:",font=("Arial", 16, "bold")).grid(row=linha, column=0, sticky="nsew",pady=(5, 15))

        ctk.CTkLabel(frame_info,text=str(valor),wraplength=800,justify="left").grid(row=linha, column=1, sticky="w", padx=10,pady=(10, 30))

        linha += 1

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda: edicao_personagem())
    edit.grid(row=1, column=0, columnspan=2, pady=10)

    print(personagem["nome"])

def abrir_galeria_personagem(personagem):
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # IMAGEM PRINCIPAL
    if personagem.get("imagens"):
        img = Image.open(personagem["imagens"])
        img.thumbnail((250, 250))
        img_ctk = ctk.CTkImage(light_image=img,dark_image=img,size=(img.width, img.height))

        label = ctk.CTkLabel(frame_lista_conteudo, image=img_ctk, text="")
        label.image = img_ctk
        label.pack(pady=10)

    # GALERIA
    titulo = ctk.CTkLabel(frame_lista_conteudo,text="Galeria:",font=("Helvetica", 16, "bold"))
    titulo.pack(pady=10)

    for item in personagem.get("galeria", []):

        if isinstance(item, dict):
            caminho = item.get("caminho") or item.get("imagem")
            descricao = item.get("descricao", "")
        else:
            caminho = item
            descricao = ""

        descricao = item.get("descricao", "")

        try:
            img = Image.open(caminho)
            img.thumbnail((200, 200))

            img_ctk = ctk.CTkImage(light_image=img,dark_image=img,size=(img.width, img.height))

            frame = ctk.CTkFrame(frame_lista_conteudo)
            frame.pack(pady=10)

            img_label = ctk.CTkLabel(frame, image=img_ctk, text="")
            img_label.image = img_ctk
            img_label.pack()

            desc = ctk.CTkLabel(frame, text=descricao, wraplength=400)
            desc.pack()

        except Exception as erro:
            print(f"Erro ao abrir imagem da galeria: {erro}")

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

def mostrar_todas_imagens():
    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    personagens_com_imagem = [
        p for p in historia_selecionada["personagens"]
        if p.get("imagens")
    ]

    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"🖼️ Todas as Imagens ({len(personagens_com_imagem)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    grid_imagens = ctk.CTkFrame(
        frame_lista_conteudo,
        fg_color="transparent"
    )
    grid_imagens.pack(fill="both", expand=True, padx=20)

    for indice, personagem in enumerate(personagens_com_imagem):

        linha = indice // 4
        coluna = indice % 4

        try:
            imagem_pil = Image.open(personagem["imagens"])

            imagem_pil.thumbnail((150, 150))

            img_ctk = ctk.CTkImage(
                light_image=imagem_pil,
                dark_image=imagem_pil,
                size=(imagem_pil.width, imagem_pil.height)
            )

            card = ctk.CTkFrame(grid_imagens)
            card.grid(
                row=linha,
                column=coluna,
                padx=10,
                pady=10
            )

            foto = ctk.CTkLabel(
                card,
                image=img_ctk,
                text=""
            )
            foto.image = img_ctk
            foto.pack(pady=5)

            nome = ctk.CTkButton(
                card,
                text=personagem["nome"],
                command=lambda p=personagem:
                navegar(selecionar_personagem, p)
            )
            nome.pack(pady=5)

        except Exception as erro:
            print(
                f"Erro ao carregar imagem de "
                f"{personagem['nome']}: {erro}"
            )

def excluir():
    global personagem_selecionado

    if personagem_selecionado is None:
        print("Selecione um personagem")
        return

    confirmar = messagebox.askyesno(
        "Excluir personagem",
        f"Deseja realmente excluir '{personagem_selecionado['nome']}'?"
    )

    if not confirmar:
        return

    try:
        if personagem_selecionado.get("imagens"):
            if os.path.exists(personagem_selecionado["imagens"]):
                os.remove(personagem_selecionado["imagens"])

        historia_selecionada["personagens"].remove(personagem_selecionado)

        historias.salvar_dados(historias.Historias)

        personagem_selecionado = None

        selecionar_historia(historia_selecionada)

    except Exception as erro:
        print(f"Erro ao excluir personagem: {erro}")

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
    fraquezas.get("1.0","end-1c"),
    habpertex.get("1.0","end-1c")
    )

    if caminho_imagem:
        extensao = os.path.splitext(caminho_imagem)[1]

        novo_caminho = os.path.join(storage.PASTA_IMAGENS,f"{novo['id']}{extensao}")

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

    caminho_imagem = filedialog.askopenfilename(title="Selecione uma imagem",filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),("Todos os arquivos", "*.*")])

    if not caminho_imagem:
        return

    imagem_pil = Image.open(caminho_imagem)

    imagem_pil.thumbnail((250, 250))

    largura = imagem_pil.width
    altura = imagem_pil.height

    img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(largura,altura))

    preview.configure(image=img_ctk, text="")
    preview.image = img_ctk

def adicionar_imagem():
    galeria_imagens.append(caminho_imagem)

def galeria():
    galeria_imagens = []

    galeria_imagens = filedialog.askopenfilename(title="Selecione uma imagem",filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),("Todos os arquivos", "*.*")])

    if not galeria_imagens:
        return

    imagem_pil = Image.open(galeria_imagens)

    imagem_pil.thumbnail((250, 250))

    largura = imagem_pil.width
    altura = imagem_pil.height

    img_ctk = ctk.CTkImage(light_image=imagem_pil,dark_image=imagem_pil,size=(largura,altura))

    preview.configure(image=img_ctk, text="")
    preview.image = img_ctk

    addimag = ctk.CTkButton(frame_lista_conteudo, text="Imagem",command=lambda: adicionar_imagem())
    addimag.pack(pady=5)

preview = ctk.CTkLabel(janepers,text="[Clique para importar imagem principal]")
preview.grid(column=0, row=1, rowspan=3)
preview.bind("<Button-1>", lambda e: imagem())

gale = ctk.CTkLabel(janepers,text="[Galeria de imagens]")
gale.grid(column=0, row=4, rowspan=3)
gale.bind("<Button-1>", lambda e: galeria())

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

fraquezas = ctk.CTkLabel(janepers,text="Fraquezas:")
fraquezas.grid(column=1, row=7)

fraquezas = ctk.CTkTextbox(janepers,height=50)
fraquezas.grid(column=2,row=7, sticky="we")

habper = ctk.CTkLabel(janepers,text=f"Habilidades do personagem")
habper.grid(column=1,row=8)

habpertex = ctk.CTkTextbox(janepers,height=50)
habpertex.grid(column=2,row=8, sticky="we")

fecharperso = ctk.CTkButton(janepers,text="[Fechar]",command=lambda: ocultar_frame(janepers))
fecharperso.grid(column=1,row=9, sticky="se",pady=10,padx=10)

salvarperso = ctk.CTkButton(janepers,text="[Salvar Personagem]",command=lambda: salvar_personagem())
salvarperso.grid(column=2,row=9, sticky="se",pady=10,padx=10)


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
        linha = indice // 6
        coluna = indice % 6

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

    # 2. Cria um label para o sistema de poder
    for chave, valor in sistemapode.items():

        if chave in [ "id", "historia_id"]:

            continue

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

    ctk.CTkLabel(frame_lista_conteudo,text="Vantagens:").pack(anchor="w", padx=10)
    
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

#CRIAR JANELA OBSERVAÇÕES

def salvar_observacoes():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    novo = criar_observacoes(
        historia_selecionada,
        var_relacao.get(),
        obstitulo.get(),
        obsconteudo.get("1.0", "end").strip()
    )

    if novo:

        criar_label_obs(
            novo,
            frame_lista_conteudo,
            selecionar_observacoes
        )

        selecionar_observacoes(novo)
        ocultar_frame(janeobser)

        print(novo)

def mostrar_todas_observacoes():

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    observacoes = historia_selecionada.get("observacoes", [])

    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"📂 Todas as observações/curiosidades ({len(observacoes)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    grid_obs = ctk.CTkFrame(frame_lista_conteudo, fg_color="transparent")
    grid_obs.pack(fill="both", expand=True, padx=20)

    for indice, observacao in enumerate(observacoes):

        linha = indice // 6
        coluna = indice % 6

        botao_card = ctk.CTkButton(
            grid_obs,
            text=observacao["nome"],
            command=lambda o=observacao: navegar(selecionar_observacoes, o)
        )

        botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

def selecionar_observacoes(observa):
    global observacoes_selecionado

    observacoes_selecionado = observa

    # 1. Limpa o frame central para remover o que estava antes
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # 2. Cria um label para o sistema de poder
    for chave, valor in observa.items():

        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)
        
        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

janeobser = ctk.CTkFrame(janela, width=600, height=500)
janeobser.grid_propagate(False)

janeobser.grid_columnconfigure(0, weight=0)
janeobser.grid_columnconfigure(1, weight=1)

for i in range(4):
    janeobser.grid_rowconfigure(i, weight=1)

var_relacao = ctk.StringVar(value="")

obsrelacao = ctk.CTkOptionMenu(janeobser,values=[""],variable=var_relacao,width=250)
obsrelacao.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

def atualizar_optionmenu_personagens():
    if historia_selecionada is None:
        obsrelacao.configure(values=[""])
        var_relacao.set("")
        return

    nomes = [p["nome"] for p in historia_selecionada["personagens"]]

    if not nomes:
        nomes = [""]

    obsrelacao.configure(values=nomes)
    var_relacao.set(nomes[0])

ctk.CTkLabel(janeobser, text="Título:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
obstitulo = ctk.CTkEntry(janeobser)
obstitulo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

obsconteudo = ctk.CTkTextbox(janeobser, height=180)
obsconteudo.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

salvaobs = ctk.CTkButton(janeobser,text="[Salva]",command=lambda: salvar_observacoes())
salvaobs.grid(row=3,column=1)

f = ctk.CTkButton(janeobser,text="Fechar",command=lambda: ocultar_frame(janeobser))
f.grid(row=3,column=0)

#MOSTRAR NO CONTEUDO

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

botao_image= ctk.CTkButton(lista_conteudo, text="Imagens",command=lambda: navegar(mostrar_todas_imagens))
botao_image.grid(column=4,row=0,sticky="n",padx=5,pady=5)

botao_image_galeria= ctk.CTkButton(lista_conteudo, text="Galeria",command=lambda: navegar(mostrar_todas_imagens_da_galeria))
botao_image_galeria.grid(column=5,row=0,sticky="n",padx=5,pady=5)

botao_sispower = ctk.CTkButton(lista_conteudo,text="Sistema de pd",command=lambda: navegar(mostrar_todos_sistemas_poder))
botao_sispower.grid(column=6,row=0,sticky="n",padx=5,pady=5)

botao_obser = ctk.CTkButton(lista_conteudo,text="Observação",command=lambda: navegar(mostrar_todas_observacoes))
botao_obser.grid(column=7,row=0,sticky="n",padx=5,pady=5)

botao_excluir= ctk.CTkButton(lista_conteudo,text="Excluir",command=lambda: excluir())
botao_excluir.grid(column=8,row=0,sticky="n",padx=5,pady=5)

carregar_interface()


janela.mainloop()