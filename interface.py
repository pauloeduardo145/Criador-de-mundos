import customtkinter as ctk
import sys
import tkinter as tk

from customtkinter.windows.widgets.ctk_scrollable_frame import CTkScrollableFrame

_check_if_valid_scroll_original = CTkScrollableFrame._check_if_valid_scroll

def _check_if_valid_scroll_patched(self, widget):
    if isinstance(widget, str):
        return False
    return _check_if_valid_scroll_original(self, widget)

CTkScrollableFrame._check_if_valid_scroll = _check_if_valid_scroll_patched

historia_selecionada = None
personagem_selecionado = None
caminho_imagem = None
galeria_imagens = None

from widgets import *
import historias
import uuid
from tkinter import filedialog
from datetime import datetime
import shutil
import os
import storage
from tkinter import messagebox

ctk.set_appearance_mode("dark")

historico = []

data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")

historia_selecionada = None
capitulo_selecionado = None
personagem_selecionado = None
sistema_de_poder_selecionado = None
observacao_selecionada = None
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

# Ícone da janela — .ico só é suportado nativamente no Windows;
# no Linux/Mac o Tkinter precisa do iconphoto com uma imagem (.png).
def _caminho_recurso(relativo):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relativo)
 
try:
    if sys.platform.startswith("win"):
        janela.iconbitmap(_caminho_recurso("icone_planeta.ico"))
    else:
        _icone_png = tk.PhotoImage(file=_caminho_recurso("icone_planeta.png"))
        janela.iconphoto(True, _icone_png)
except Exception as erro_icone:
    print(f"Não foi possível carregar o ícone da janela: {erro_icone}")

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

# FUNÇÃO DE PADRONIZAÇÃO E RECALCULA A AREA ROLÁVEL

def limpar_frame_conteudo():
    for widget in frame_lista_conteudo.winfo_children():
        widget.destroy()

    # Força o canvas a recalcular a área rolável com base no conteúdo atual
    frame_lista_conteudo.update_idletasks()
    frame_lista_conteudo._parent_canvas.configure(scrollregion=frame_lista_conteudo._parent_canvas.bbox("all"))
    frame_lista_conteudo._parent_canvas.yview_moveto(0)

def arearolavel():
    frame_lista_conteudo.update_idletasks()
    frame_lista_conteudo._parent_canvas.configure(scrollregion=frame_lista_conteudo._parent_canvas.bbox("all"))
    frame_lista_conteudo._parent_canvas.yview_moveto(0)

# ATALHOS DE NAVEGAÇÃO

def selecionar_tudo_entry(event):
    event.widget.select_range(0, "end")
    event.widget.icursor("end")
    return "break"

def selecionar_tudo_textbox(event):
    event.widget.tag_add("sel", "1.0", "end-1c")
    event.widget.mark_set("insert", "1.0")
    event.widget.see("insert")
    return "break"

def configurar_entry(entry):
    entry.bind("<Control-a>", selecionar_tudo_entry)
    entry.bind("<Control-A>", selecionar_tudo_entry)

def configurar_textbox(textbox):
    textbox.bind("<Control-a>", selecionar_tudo_textbox)
    textbox.bind("<Control-A>", selecionar_tudo_textbox)

#MOSTRAR NO CONTEUDO

def mostrar_cards_com_imagem(frame,itens,callback,chave_imagem="imagens",chave_nome="nome",tamanho=150):

    grid = ctk.CTkFrame(frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=20)

    for indice, item in enumerate(itens):

        linha = indice // 6
        coluna = indice % 6

        try:
            img_ctk = mostrar_imagem(item[chave_imagem], tamanho)

            card = ctk.CTkFrame(grid)
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

            botao = ctk.CTkButton(
                card,
                text=item[chave_nome],
                command=lambda i=item: navegar(callback, i)
            )
            botao.pack(pady=5)

        except Exception as erro:
            print(f"Erro ao carregar {item[chave_nome]}: {erro}")

def mostrar_no_conteudo(frame, itens, callback, chave_nome):

    grid = ctk.CTkFrame(frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=20)

    for i in range(6):
        grid.grid_columnconfigure(i, weight=1)

    for indice, item in enumerate(itens):

        linha = indice // 6
        coluna = indice % 6

        ctk.CTkButton(
            grid,
            text=item[chave_nome],
            height=40,
            command=lambda i=item: navegar(callback, i)
        ).grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

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

    qtd = len(historia['capitulos'])

    if qtd == 1:
        cap.configure(text=f"Capítulo: {qtd}")
    else:
        cap.configure(text=f"Capítulos: {qtd}")

    ue.configure(text=f"UE: {historia.get('ultima_edicao', 'Nunca')}")

    pers.configure(text=f"Personagens: {len(historia['personagens'])}")
    
    if historia_selecionada["sistemas_poder"]:
        sp.configure(text=f"Sistema P: {historia_selecionada['sistemas_poder'][0]['nome']}")
    else:
        sp.configure(text="Sistema P: Nenhum")


    limpar_frame_conteudo()

    mostrar_no_conteudo(frame_lista_conteudo,historia["personagens"],selecionar_personagem,"nome")

    mostrar_no_conteudo(frame_lista_conteudo,historia["capitulos"],selecionar_capitulo,"nome")

    mostrar_no_conteudo(frame_lista_conteudo,historia["sistemas_poder"],selecionar_sistemapoder,"nome")

    mostrar_no_conteudo(frame_lista_conteudo,historia["observacoes"],selecionar_observacoes,"titulo")

#MOSTRAR TODOS...

def mostrar_todas_imagens_da_galeria(event=None):

    if historia_selecionada is None:

        limpar_frame_conteudo()

        ctk.CTkLabel(
            frame_lista_conteudo,
            text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
            font=("Helvetica", 18),
            justify="center"
        ).pack(expand=True)
        return

    limpar_frame_conteudo()

    personagens = [
        p for p in historia_selecionada["personagens"]
        if len(p.get("galeria", [])) > 0
    ]

    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"Personagens com Galeria ({len(personagens)})",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10)

    for personagem in personagens:
        btn = ctk.CTkButton(frame_lista_conteudo,text=personagem["nome"],command=lambda p=personagem: abrir_galeria_personagem(p))
        btn.pack(pady=5)

def mostrar_todos_personagens(event=None):

    if historia_selecionada is None:

        limpar_frame_conteudo()

        ctk.CTkLabel(
            frame_lista_conteudo,
            text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
            font=("Helvetica", 18),
            justify="center"
        ).pack(expand=True)
        return

    personagens = historia_selecionada.get("personagens", [])

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"📂 Todos os Personagens ({len(personagens)})",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    mostrar_no_conteudo(frame_lista_conteudo,personagens,selecionar_personagem,"nome")

def mostrar_todos_capitulos(event=None):
    if historia_selecionada is None:

        limpar_frame_conteudo()

        ctk.CTkLabel(
            frame_lista_conteudo,
            text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
            font=("Helvetica", 18),
            justify="center"
        ).pack(expand=True)
        return

    capitulo = historia_selecionada.get("capitulos", [])

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"📂 Todos os Capitulos ({len(capitulo)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    mostrar_no_conteudo(frame_lista_conteudo,capitulo,selecionar_capitulo,"nome")

def mostrar_todas_imagens(event=None):

    if historia_selecionada is None:

        limpar_frame_conteudo()

        ctk.CTkLabel(
            frame_lista_conteudo,
            text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
            font=("Helvetica", 18),
            justify="center"
        ).pack(expand=True)
        return

    limpar_frame_conteudo()

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

    mostrar_cards_com_imagem(frame_lista_conteudo,personagens_com_imagem,selecionar_personagem)

#SELECIONAR ...

def selecionar_personagem(personagem):
    global personagem_selecionado

    personagem_selecionado = personagem

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    linha = 0

    frame_imagem = ctk.CTkFrame(frame_lista_conteudo)
    frame_imagem.grid(row=0, column=0, sticky="n" ,padx=20)

    frame_info = ctk.CTkFrame(frame_lista_conteudo,width=600)
    frame_info.grid_columnconfigure(1, weight=1)
    frame_info.grid(row=0, column=1, sticky="nsew", padx=20)
    #frame_info.grid_propagate(False)

    if personagem.get("imagens"):
        img = mostrar_imagem(personagem["imagens"],500)

        foto = ctk.CTkLabel(frame_imagem, image=img, text="")
        foto.image = img
        foto.grid()

    # 2. Cria um label para o personagem
    labels_valor = []

    for chave, valor in personagem.items():
        
        if chave in ["imagens", "galeria", "id", "historia_id"]:
            continue
        
        ctk.CTkLabel(frame_info,text=f"{chave}:",font=("Arial", 16, "bold")).grid(row=linha, column=0, sticky="nsew",pady=(5, 15))

        valor_label = ctk.CTkLabel(frame_info,text=str(valor),anchor="w",wraplength=560,justify="left")
        valor_label.grid(row=linha, column=1, sticky="ew", padx=10,pady=(10, 30))
        labels_valor.append(valor_label)

        linha += 1

    def _atualizar_wraplength(evento, labels=labels_valor):
        # Usa a largura real do frame_info (o container), não a do próprio
        # label, para evitar o ciclo de realimentação em que o label pede
        # o mínimo, o grid concede o mínimo, e o texto quebra letra a letra.
        largura_disponivel = max(evento.width - 130, 100)
        for rotulo in labels:
            rotulo.configure(wraplength=largura_disponivel)

    frame_info.bind("<Configure>", _atualizar_wraplength)

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda *args: edicao_personagem(*args))
    edit.grid(row=1, column=0, columnspan=2, pady=10)

    print(personagem["nome"])

def selecionar_capitulo(capitulo):
    global capitulo_selecionado

    capitulo_selecionado = capitulo

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um label para o personagem
    for chave, valor in capitulo.items():
        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    print(capitulo["nome"])

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda *args: edicao_capitulo())
    edit.pack(pady=10)

def selecionar_observacoes(observa):
    global observacoes_selecionado

    observacoes_selecionado = observa

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um label para o sistema de poder
    for chave, valor in observa.items():

        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)
        
        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda *args: edicao_observacao())
    edit.pack(pady=10)

#EDIÇÃO

def edicao_capitulo(*args):
    global capitulo_selecionado

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    limpar_frame_conteudo()

    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"Modo Edição",
        font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0, capitulo_selecionado["nome"])
    nome.pack(fill="x", padx=10, pady=5)
    configurar_entry(nome)

    ALTURA_MIN = 80
    ALTURA_MAX = 375  # a partir daqui, a rolagem interna assume o controle

    def ajustar_altura(event=None):
        widget = conteudos
        widget.update_idletasks()

        # conta linhas EXIBIDAS (respeita o wrap="word"), não só quebras "\n"
        resultado = widget._textbox.count("1.0", "end", "displaylines")
        linhas = int(resultado[0]) if resultado else 1

        altura_por_linha = 21  # aproximação para a fonte padrão do CTkTextbox
        altura_desejada = linhas * altura_por_linha + 20  # + respiro

        nova_altura = max(ALTURA_MIN, min(altura_desejada, ALTURA_MAX))
        widget.configure(height=nova_altura)

        widget.edit_modified(False)

    conteudos = ctk.CTkTextbox(
        frame_lista_conteudo,
        wrap="word",
        activate_scrollbars=True  # só entra em ação quando bater no limite
    )
    conteudos.pack(fill="x", padx=10, pady=5)
    configurar_textbox(conteudos)
    conteudos.insert("1.0", capitulo_selecionado["conteudo"])

    ajustar_altura()
    conteudos.bind("<<Modified>>", ajustar_altura)

    def salvar_edicao():
        capitulo_selecionado["nome"] = nome.get()
        capitulo_selecionado["conteudo"] = conteudos.get("1.0", "end-1c")
        historias.salvar_dados(historias.Historias)
        selecionar_capitulo(capitulo_selecionado)

    botao_salvar = ctk.CTkButton(frame_lista_conteudo, text="Salvar", command=lambda *args: salvar_edicao())
    botao_salvar.pack(pady=10)

    contador = ctk.CTkLabel(frame_lista_conteudo, text="0 caracteres")
    contador.pack(padx=100)

    def atualizar(event=None):
        texto = conteudos.get("1.0", "end-1c")
        contador.configure(text=f"{len(texto)} caracteres")

    conteudos.bind("<KeyRelease>", atualizar)

    arearolavel()

def edicao_personagem(*args):
    global personagem_selecionado

    if "galeria" not in personagem_selecionado:
        personagem_selecionado["galeria"] = []

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(frame_lista_conteudo,text=f"Modo Edição",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0,personagem_selecionado["nome"])
    nome.pack(fill="x",padx=10,pady=5)
    configurar_entry(nome)

    p = ctk.CTkLabel(frame_lista_conteudo,text="Personalidade:")
    p.pack(padx=10,pady=5)

    personalidade = ctk.CTkTextbox(frame_lista_conteudo,height=50,fg_color="#1E1E1E",text_color="white", border_color="gray")
    personalidade.pack(fill="x",pady=10,padx=5)
    personalidade.insert("1.0", personagem_selecionado["personalidade"])
    configurar_textbox(personalidade)

    pe = ctk.CTkLabel(frame_lista_conteudo,text="Aparencia:")
    pe.pack(padx=10,pady=5) 

    aparencia = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    aparencia.pack(fill="x",pady=10,padx=5)
    aparencia.insert("1.0", personagem_selecionado["aparencia"])
    configurar_textbox(aparencia)

    his = ctk.CTkLabel(frame_lista_conteudo,text="Historia:")
    his.pack(padx=10,pady=5)

    hispers = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    hispers.pack(fill="x",pady=10,padx=5)
    hispers.insert("1.0", personagem_selecionado["historia"])
    configurar_textbox(hispers)

    r = ctk.CTkLabel(frame_lista_conteudo,text="Relações:")
    r.pack(padx=10,pady=5)

    relacoes = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    relacoes.pack(fill="x",pady=10,padx=5)
    relacoes.insert("1.0", personagem_selecionado["relacoes"])
    configurar_textbox(relacoes)

    po = ctk.CTkLabel(frame_lista_conteudo,text="Poderes:")
    po.pack(padx=10,pady=5)

    poderes = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    poderes.pack(fill="x",pady=10,padx=5)
    poderes.insert("1.0", personagem_selecionado["poderes"])
    configurar_textbox(poderes)

    fraq = ctk.CTkLabel(frame_lista_conteudo,text="Fraquezas:")
    fraq.pack(padx=10,pady=5)

    fraqueza = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    fraqueza.pack(fill="x",pady=10,padx=5)
    fraqueza.insert("1.0", personagem_selecionado["fraquezas"])
    configurar_textbox(fraqueza)

    ha = ctk.CTkLabel(frame_lista_conteudo,text="Habilidades:")
    ha.pack(padx=10,pady=5)

    hapers = ctk.CTkTextbox(frame_lista_conteudo,height=50)
    hapers.pack(fill="x",pady=10,padx=5)
    hapers.insert("1.0", personagem_selecionado["habilidades"])
    configurar_textbox(hapers)

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
                img = mostrar_imagem(caminho,100)

                card = ctk.CTkFrame(frame_galeria)
                card.grid(row=indice // 4, column=indice % 4, padx=5, pady=5)

                label = ctk.CTkLabel(card, image=img, text="")
                label.image = img
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

        img = mostrar_imagem(caminho_imagem,250)

        preview.configure(image=img, text="")
        preview.image = img

    if personagem_selecionado.get("imagens"):

        img = mostrar_imagem(personagem_selecionado["imagens"], 250)

        preview.configure(image=img, text="")
        preview.image = img

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

    arearolavel()

    botao_fechar = ctk.CTkButton(frame_lista_conteudo,text="Fechar sem salvar",command=fechar_sem_salvar)
    botao_fechar.pack(pady=10)

def abrir_galeria_personagem(personagem):
    limpar_frame_conteudo()

    # IMAGEM PRINCIPAL
    if personagem.get("imagens"):
        img_ctk = mostrar_imagem(personagem["imagens"],250)

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
            img_ctk = mostrar_imagem(caminho,200)

            frame = ctk.CTkFrame(frame_lista_conteudo)
            frame.pack(pady=10)

            img_label = ctk.CTkLabel(frame, image=img_ctk, text="")
            img_label.image = img_ctk
            img_label.pack()

            desc = ctk.CTkLabel(frame, text=descricao, wraplength=400)
            desc.pack()

        except Exception as erro:
            print(f"Erro ao abrir imagem da galeria: {erro}")

def edicao_observacao(*args):
    global observacoes_selecionado

    if historia_selecionada is None:
        print("Nenhuma história selecionada")
        return

    if observacoes_selecionado is None:
        print("Nenhuma observação selecionada")
        return

    # Limpa o frame
    limpar_frame_conteudo()

    # Título
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text="Modo Edição (Observação)",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    # Relação
    ctk.CTkLabel(frame_lista_conteudo, text="Relação:").pack(padx=10, pady=5)

    relacao = ctk.CTkEntry(frame_lista_conteudo)
    relacao.insert(0, observacoes_selecionado.get("relacao", ""))
    relacao.pack(fill="x", padx=10, pady=5)
    configurar_entry(relacao)

    # Título
    ctk.CTkLabel(frame_lista_conteudo, text="Título:").pack(padx=10, pady=5)

    titulo_obs = ctk.CTkEntry(frame_lista_conteudo)
    titulo_obs.insert(0, observacoes_selecionado.get("titulo", ""))
    titulo_obs.pack(fill="x", padx=10, pady=5)
    configurar_entry(titulo_obs)

    # Conteúdo
    ctk.CTkLabel(frame_lista_conteudo, text="Conteúdo:").pack(padx=10, pady=5)

    conteudo = ctk.CTkTextbox(frame_lista_conteudo, height=150)
    conteudo.insert("1.0", observacoes_selecionado.get("conteudo", ""))
    conteudo.pack(fill="both", expand=True, padx=10, pady=5)
    configurar_textbox(conteudo)

    def salvar_edicao():

        observacoes_selecionado["relacao"] = relacao.get()
        observacoes_selecionado["titulo"] = titulo_obs.get()
        observacoes_selecionado["conteudo"] = conteudo.get("1.0", "end-1c")

        historias.salvar_dados(historias.Historias)

        selecionar_observacoes(observacoes_selecionado)

    def fechar_sem_salvar():
        confirmar = messagebox.askyesno(
            "Cancelar edição",
            "Deseja sair sem salvar as alterações?"
        )

        if confirmar:
            selecionar_observacoes(observacoes_selecionado)

    # Botões
    ctk.CTkButton(
        frame_lista_conteudo,
        text="Salvar",
        command=salvar_edicao
    ).pack(pady=10)

    ctk.CTkButton(
        frame_lista_conteudo,
        text="Fechar sem salvar",
        command=fechar_sem_salvar
    ).pack(pady=10)

#EXCLUIR

def excluir_personagem(nome):

    personagem = next(
        (p for p in historia_selecionada["personagens"] if p["nome"] == nome),
        None
    )

    if personagem is None:
        return

    if not messagebox.askyesno(
        "Excluir",
        f'Deseja realmente excluir o personagem "{nome}"?'
    ):
        return

    historia_selecionada["personagens"].remove(personagem)

    historias.salvar_dados(historias.Historias)
    selecionar_historia(historia_selecionada)

def excluir_capitulo(nome):

    capitulo = next(
        (c for c in historia_selecionada["capitulos"] if c["nome"] == nome),
        None
    )

    if capitulo is None:
        return

    if not messagebox.askyesno(
        "Excluir",
        f'Deseja realmente excluir o capítulo "{nome}"?'
    ):
        return

    historia_selecionada["capitulos"].remove(capitulo)

    historias.salvar_dados(historias.Historias)
    selecionar_historia(historia_selecionada)

def excluir_observacao(titulo):

    observacao = next(
        (o for o in historia_selecionada["observacoes"] if o["titulo"] == titulo),
        None
    )

    if observacao is None:
        return

    if not messagebox.askyesno(
        "Excluir",
        f'Deseja realmente excluir a observação "{titulo}"?'
    ):
        return

    historia_selecionada["observacoes"].remove(observacao)

    historias.salvar_dados(historias.Historias)
    selecionar_historia(historia_selecionada)

def excluir_historia(nome):

    historia = next(
        (h for h in historias.Historias if h["nome"] == nome),
        None
    )

    if historia is None:
        return

    if not messagebox.askyesno(
        "Excluir",
        f'Deseja realmente excluir a história "{nome}"?'
    ):
        return

    historias.Historias.remove(historia)

    historias.salvar_dados(historias.Historias)

    global historia_selecionada
    historia_selecionada = None

    carregar_interface()

    limpar_frame_conteudo()

def excluir_item(*args):

    limpar_frame_conteudo()

    tipo_var = ctk.StringVar(value="Personagem")
    item_var = ctk.StringVar(value="")

    option_item = None

    def atualizar_lista_exclusao(opcao):

        nonlocal option_item

        if opcao == "Personagem":
            itens = [p["nome"] for p in historia_selecionada["personagens"]]

        elif opcao == "História":
            itens = [historia_selecionada["nome"]]

        elif opcao == "Capítulo":
            itens = [c["nome"] for c in historia_selecionada["capitulos"]]

        elif opcao == "Observação":
            itens = [o["titulo"] for o in historia_selecionada["observacoes"]]

        else:
            itens = []

        if option_item is not None:
            option_item.destroy()

        if itens:
            item_var.set(itens[0])
        else:
            item_var.set("")

        option_item = ctk.CTkOptionMenu(
            frame_lista_conteudo,
            variable=item_var,
            values=itens
        )

        option_item.pack(pady=10)

    def confirmar_exclusao():

        tipo = tipo_var.get()
        item = item_var.get()

        if tipo == "Personagem":
            excluir_personagem(item)

        elif tipo == "Capítulo":
            excluir_capitulo(item)

        elif tipo == "Observação":
            excluir_observacao(item)

        elif tipo == "História":
            excluir_historia(item)

    ctk.CTkOptionMenu(
        frame_lista_conteudo,
        values=[
            "Personagem",
            "História",
            "Capítulo",
            "Observação"
        ],
        variable=tipo_var,
        command=atualizar_lista_exclusao
    ).pack(pady=10)

    atualizar_lista_exclusao("Personagem")

    ctk.CTkButton(
        frame_lista_conteudo,
        text="Excluir",
        command=confirmar_exclusao
    ).pack(pady=15)
#CAIXA

from perfil import Perfil

caixa_frame = ctk.CTkFrame(janela,width= 200,height=20)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,padx=10,pady=5)

perfil_config = ctk.CTkButton(caixa_frame,height=10,text="👤",fg_color="black",width=4,font=("Helvetica", 7), command=lambda: Perfil(janela).abrir_perfil())
perfil_config.grid(column=0,row=0,sticky="n",padx=5,pady=5)

exit_button = ctk.CTkButton(caixa_frame,height=10,text='Exit',fg_color="black",width=4,font=("Helvetica", 7),command=lambda: janela.quit())
exit_button.grid(column=1,row=0,sticky="n",padx=5,pady=5)

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
    carregar_interface()
    ocultar_frame(frame_nomeh)

nome = ctk.CTkEntry(frame_nomeh,placeholder_text="Nome da Historia")
nome.bind("<Return>", enter_historia)
nome.grid(column=0,row=1,sticky="nsew",columnspan=2)
nome.focus()
configurar_entry(nome)

criar_h = ctk.CTkButton(frame_nomeh,text="Criar Historia",command=lambda: (criar_historia(nome.get()),carregar_interface(),ocultar_frame(frame_nomeh),print(historias.Historias),print(len(historias.Historias))))
criar_h.grid(column=1,row=3,padx=5,pady=10,sticky="s")

f = ctk.CTkButton(frame_nomeh,text="Fechar",command=lambda: ocultar_frame(frame_nomeh))
f.grid(column=0,row=3,padx=5)

#JANELA CRIAR PERSONAGEM (ESTA CONCLUIDO).

def salvar_personagem():
    global caminho_imagem

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

    if galeria_imagens is not None:
        novo["galeria"] = galeria_imagens.copy()
    else:
        novo["galeria"] = []

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

    img_ctk = mostrar_imagem(caminho_imagem,250)

    preview.configure(image=img_ctk, text="")
    preview.image = img_ctk

def adicionar_imagem():
    galeria_imagens.append(caminho_imagem)

def galeria():
    global galeria_imagens

    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[
            ("Imagens", "*.png *.jpg *.jpeg *.webp"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho:
        return

    janela_desc = ctk.CTkInputDialog(
        text="Digite a descrição da imagem:",
        title="Descrição da Galeria"
    )

    descricao = janela_desc.get_input()

    if descricao is None:
        descricao = ""

    extensao = os.path.splitext(caminho)[1]

    nome_arquivo = f"{uuid.uuid4()}{extensao}"

    novo_caminho = os.path.join(
        storage.PASTA_GALERIA,
        nome_arquivo
    )

    shutil.copy2(caminho, novo_caminho)

    if galeria_imagens is None:
        galeria_imagens = []

    galeria_imagens.append({
        "caminho": novo_caminho,
        "descricao": descricao
    })

    print(galeria_imagens)

preview = ctk.CTkLabel(janepers,text="[Clique para importar imagem principal]")
preview.grid(column=0, row=3, rowspan=3)
preview.bind("<Button-1>", lambda e: imagem())

perso = ctk.CTkLabel(janepers,text="Nome: ")
perso.grid(column=1,row=0)

personame = ctk.CTkEntry(janepers,placeholder_text="Insira o nome do personagem")
personame.bind("<Return>", enter_personagem)
personame.grid(column=2,row=0,sticky="we")
personame.focus()
configurar_entry(personame)

personali = ctk.CTkLabel(janepers,text="Personalidade: ")
personali.grid(column=1,row=1)

personapersona = ctk.CTkTextbox(janepers,height=50)
personapersona.grid(column=2,row=1, sticky="we")
configurar_textbox(personapersona)

apa = ctk.CTkLabel(janepers,text="Aparencia: ")
apa.grid(column=1,row=2)

persoapare = ctk.CTkTextbox(janepers,height=50)
persoapare.grid(column=2,row=2, sticky="we")
configurar_textbox(persoapare)

rela = ctk.CTkLabel(janepers,text="Relações")
rela.grid(column=1, row=3)

relaca = ctk.CTkTextbox(janepers,height=50)
relaca.grid(column=2,row=3, sticky="we")
configurar_textbox(relaca)

relabel =ctk.CTkLabel(janepers,text="Separe com ';', Ex: Esposa de X; Amiga de X",font=("Helvetica", 11))
relabel.grid(column=2,row=4, sticky="w")

hisper = ctk.CTkLabel(janepers,text=f"Historia do personagem")
hisper.grid(column=1,row=5)

hispertex = ctk.CTkTextbox(janepers,height=50)
hispertex.grid(column=2,row=5, sticky="we")
configurar_textbox(hispertex)

podelabel = ctk.CTkLabel(janepers,text="Poderes:")
podelabel.grid(column=1, row=6)

poderes = ctk.CTkTextbox(janepers,height=50)
poderes.grid(column=2,row=6, sticky="we")
configurar_textbox(poderes)

fraquezas = ctk.CTkLabel(janepers,text="Fraquezas:")
fraquezas.grid(column=1, row=7)

fraquezas = ctk.CTkTextbox(janepers,height=50)
fraquezas.grid(column=2,row=7, sticky="we")
configurar_textbox(fraquezas)

habper = ctk.CTkLabel(janepers,text=f"Habilidades do personagem")
habper.grid(column=1,row=8)

habpertex = ctk.CTkTextbox(janepers,height=50)
habpertex.grid(column=2,row=8, sticky="we")
configurar_textbox(habpertex)

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
        selecionar_historia(historia_selecionada)
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
configurar_entry(capiname)

capiconteudo = ctk.CTkTextbox(janecapi, width=300, height=150, activate_scrollbars=True)
capiconteudo.focus()
capiconteudo.bind("<Return>", enter_capitulo)
capiconteudo.grid(column=0,row=2,sticky="nsew",columnspan=2)
configurar_textbox(capiconteudo)

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
    limpar_frame_conteudo()

    # 2. Cria um título para a seção
    titulo = ctk.CTkLabel(
        frame_lista_conteudo,
        text=f"📂 Todos os sistemas de poder ({len(sistemapoder)})",
        font=("Helvetica", 18, "bold")
    )
    titulo.pack(pady=10, anchor="w", padx=20)

    mostrar_no_conteudo(frame_lista_conteudo,historia_selecionada["sistemas_poder"],sistema_de_poder_selecionado,"nome")

def selecionar_sistemapoder(sistemapode):
    global sistema_de_poder_selecionado

    sistema_de_poder_selecionado = sistemapode

    # 1. Limpa o frame central para remover o que estava antes
    limpar_frame_conteudo()

    # 2. Cria um label para o sistema de poder
    for chave, valor in sistemapode.items():

        if chave in [ "id", "historia_id"]:

            continue

        ctk.CTkLabel(frame_lista_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)
        
        ctk.CTkLabel(frame_lista_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

    print(sistemapode["nome"])

    edit = ctk.CTkButton(frame_lista_conteudo,text="Editar", command=lambda *args: edicao_sistempoder())
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

def edicao_sistempoder(*args):
    global sistema_de_poder_selecionado

    if sistema_de_poder_selecionado is None:
        print("Nenhum sistema de poder selecionado")
        return

    limpar_frame_conteudo()

    titulo = ctk.CTkLabel(frame_lista_conteudo,text="Modo Edição",font=("Helvetica", 18, "bold"))
    titulo.pack(pady=10, anchor="w", padx=20)

    # Nome

    ctk.CTkLabel(frame_lista_conteudo,text="Nome:").pack(anchor="w", padx=10)
    nome = ctk.CTkEntry(frame_lista_conteudo)
    nome.insert(0,sistema_de_poder_selecionado["nome"])
    nome.pack(fill="x", padx=10, pady=5)
    configurar_entry(nome)

    # Descrição

    ctk.CTkLabel(frame_lista_conteudo,text="Descrição:").pack(anchor="w", padx=10)

    descricao = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    descricao.insert("1.0",sistema_de_poder_selecionado["descricao"])
    descricao.pack(fill="x", padx=10, pady=5)
    configurar_textbox(descricao)

    # Regras

    ctk.CTkLabel(frame_lista_conteudo,text="Regras:").pack(anchor="w", padx=10)

    regras = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    regras.insert("1.0",sistema_de_poder_selecionado["regras"])
    regras.pack(fill="x", padx=10, pady=5)
    configurar_textbox(regras)

    # Vantagens

    ctk.CTkLabel(frame_lista_conteudo,text="Vantagens:").pack(anchor="w", padx=10)
    
    vantagens = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    vantagens.insert("1.0",sistema_de_poder_selecionado["vantagens"])
    vantagens.pack(fill="x", padx=10, pady=5)
    configurar_textbox(vantagens)

    # Fraquezas

    ctk.CTkLabel(frame_lista_conteudo,text="Fraquezas:").pack(anchor="w", padx=10)

    fraquezas = ctk.CTkTextbox(frame_lista_conteudo,height=100)
    fraquezas.insert("1.0",sistema_de_poder_selecionado["fraquezas"])
    fraquezas.pack(fill="x", padx=10, pady=5)
    configurar_textbox(fraquezas)

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

    arearolavel()

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
configurar_entry(powename)

powerlabelconteudo = ctk.CTkLabel(janesispoder,text="Conteudo:")
powerlabelconteudo.grid(column=0,row=2)

powerconteudo = ctk.CTkTextbox(janesispoder,height=50, activate_scrollbars=True)
powerconteudo.grid(column=1,row=2,sticky="ew",columnspan=2)
configurar_textbox(powerconteudo)

powerlabelregras = ctk.CTkLabel(janesispoder,text="Regras:")
powerlabelregras.grid(column=0,row=3)

regras = ctk.CTkTextbox(janesispoder,width=300,height=50,activate_scrollbars=True)
regras.grid(column=1,row=3,sticky="ew",columnspan=2)
configurar_textbox(regras)

powerlabelvantagens = ctk.CTkLabel(janesispoder,text="Vantagens:")
powerlabelvantagens.grid(column=0,row=4)

vantagens = ctk.CTkTextbox(janesispoder,height=50,activate_scrollbars=True)
vantagens.grid(column=1,row=4,sticky="ew",columnspan=2)
configurar_textbox(vantagens)

powerlabelfraquezas = ctk.CTkLabel(janesispoder,text="Fraquezas:")
powerlabelfraquezas.grid(column=0,row=5)

fraquezas = ctk.CTkTextbox(janesispoder,height=50,activate_scrollbars=True)
fraquezas.grid(column=1,row=5,sticky="ew",columnspan=2)
configurar_textbox(fraquezas)

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

    limpar_frame_conteudo()

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
            text=observacao["titulo"],
            command=lambda o=observacao: navegar(selecionar_observacoes, o)
        )

        botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

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
configurar_entry(obstitulo)

obsconteudo = ctk.CTkTextbox(janeobser, height=180)
obsconteudo.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
configurar_textbox(obsconteudo)

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

botao_excluir= ctk.CTkButton(lista_conteudo,text="Excluir",command=lambda: excluir_item())
botao_excluir.grid(column=8,row=0,sticky="n",padx=5,pady=5)

#ATALHOS GLOBAIS

def sh():
    if historia_selecionada is not None:
        pass
    else:
        mostrar_frame(frame_nomeh)

janela.bind("<F5>", lambda e: selecionar_historia(historia_selecionada))

janela.bind("<Control-n>", lambda event: sh())

def sc():
    if historia_selecionada and capitulo_selecionado is None:
        mostrar_frame(janecapi)

janela.bind("<Control-Key-c>", lambda event: sc())

# ATALHOS DE NAVEGAÇÃO

janela.bind("<Control-Key-1>", lambda event: navegar(mostrar_todos_personagens))
janela.bind("<Control-Key-2>", lambda event: navegar(mostrar_todos_capitulos))
janela.bind("<Control-Key-3>", lambda event: navegar(mostrar_todas_imagens))
janela.bind("<Control-Key-4>", lambda event: navegar(mostrar_todas_imagens_da_galeria))
janela.bind("<Control-Key-5>", lambda event: navegar(mostrar_todos_sistemas_poder))
janela.bind("<Control-Key-6>", lambda event: navegar(mostrar_todas_observacoes))
janela.bind("<Alt-Left>", lambda event: voltar())

#ATALHOS DE EDIÇÃO

janela.bind("<Control-Key-e>", edicao_personagem)
janela.bind("<Control-Key-i>", edicao_capitulo)
janela.bind("<Key-Delete>", excluir_item)
janela.bind("<Control-Key-Delete>", excluir_item)

carregar_interface()

janela.mainloop()