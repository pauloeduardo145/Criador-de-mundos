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

from widgets import *
import historias
from datetime import datetime
import os
from tkinter import messagebox

ctk.set_appearance_mode("dark")

historico = []

data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")

historia_selecionada = None

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

Addper = ctk.CTkButton(frame_botoes,height=25,text="[Criar Personagem]",command=lambda: gerenciador_personagem.abrir_criacao())
Addper.grid(column=0,row=3,sticky="w",padx=10,pady=10)

Addarco = ctk.CTkButton(frame_botoes,height=25,text="[Criar Arco]",command=lambda: gerenciador_arco.abrir_criacao())
Addarco.grid(column=1,row=3,sticky="w",padx=10,pady=10)

capitadic = ctk.CTkButton(frame_botoes,height=25,text="[Criar Capitulo]",command=lambda: gerenciador_capitulo.abrir_criacao())
capitadic.grid(column=2,row=3,sticky="w",padx=10,pady=10)

Addposis = ctk.CTkButton(frame_botoes,text="[Criar Sistema de Poder]",command=lambda: gerenciador_sistema_poder.abrir_criacao())
Addposis.grid(column=3,row=3,)

Addobs = ctk.CTkButton(frame_botoes,text="[Adicionar observação]", command=lambda: gerenciador_observacao.abrir_criacao())
Addobs.grid(column=4,row=3, sticky="w",padx=10,pady=10)

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

arc = ctk.CTkLabel(lista,text='Arcos:')
arc.grid(column=0,row=1,sticky="w",padx=10,pady=5)

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

from entry_textbox import configurar_entry,configurar_textbox

#FUNÇÕES GENÉRICAS DE LISTAGEM (usadas por Personagem, Capítulo, Sistema de Poder e Observações)

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

def mostrar_no_conteudo(frame, itens, callback, chave_nome,li,col):

    grid = ctk.CTkFrame(frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=20)

    for i in range(6):
        grid.grid_columnconfigure(i, weight=1)

    for indice, item in enumerate(itens):

        linha = indice // li
        coluna = indice % col

        ctk.CTkButton(
            grid,
            text=item[chave_nome],
            height=40,
            command=lambda i=item: navegar(callback, i)
        ).grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

#GERENCIADORES (ARCO, CAPITULO, PERSONAGEM)

from arco import Arco
from capitulo import Capitulo
from personagem import Personagem
from sistema_de_poder import SistemaDePoder
from observacao import Observacao

gerenciador_arco = Arco(
    janela,
    frame_lista_conteudo,
    obter_historia_selecionada=lambda: historia_selecionada,
    apos_criar=lambda h: selecionar_historia(h)
)

gerenciador_capitulo = Capitulo(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    gerenciador_arco,
    obter_historia_selecionada=lambda: historia_selecionada,
    apos_criar=lambda h: selecionar_historia(h)
)

gerenciador_personagem = Personagem(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    mostrar_cards_com_imagem,
    obter_historia_selecionada=lambda: historia_selecionada,
    apos_criar=lambda h: selecionar_historia(h)
)

gerenciador_sistema_poder = SistemaDePoder(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    obter_historia_selecionada=lambda: historia_selecionada,
    apos_criar=lambda h: selecionar_historia(h)
)

gerenciador_observacao = Observacao(
    janela,
    frame_lista_conteudo,
    obter_historia_selecionada=lambda: historia_selecionada,
    apos_criar=lambda h: selecionar_historia(h),
    # "navegar" só é definido mais abaixo no arquivo; a lambda resolve o
    # nome no momento da chamada (late binding), então funciona normalmente.
    navegar=lambda funcao, *args: navegar(funcao, *args)
)

def selecionar_sistemapoder(sistemapode):
    gerenciador_sistema_poder.selecionar(sistemapode)

def edicao_sistempoder(*args):
    gerenciador_sistema_poder.editar()

def mostrar_todos_sistemas_poder(event=None):
    gerenciador_sistema_poder.mostrar_todos(event)

def selecionar_observacoes(observacao):
    gerenciador_observacao.selecionar(observacao)

def edicao_observacao(*args):
    gerenciador_observacao.editar()

def mostrar_todas_observacoes(event=None):
    gerenciador_observacao.mostrar_todos(event)

def selecionar_personagem(personagem):
    gerenciador_personagem.selecionar_personagem(personagem)

def edicao_personagem(*args):
    gerenciador_personagem.edicao_personagem()

def abrir_galeria_personagem(personagem):
    gerenciador_personagem.abrir_galeria_personagem(personagem)

def mostrar_todos_personagens(event=None):
    gerenciador_personagem.mostrar_todos(event)

def mostrar_todas_imagens(event=None):
    gerenciador_personagem.mostrar_todas_imagens(event)

def mostrar_todas_imagens_da_galeria(event=None):
    gerenciador_personagem.mostrar_todas_imagens_da_galeria(event)

def selecionar_capitulo(capitulo):
    gerenciador_capitulo.selecionar_capitulo(capitulo)

def edicao_capitulo(*args):
    gerenciador_capitulo.edicao_capitulo()

def mostrar_todos_capitulos(event=None):
    gerenciador_capitulo.mostrar_todos(event)

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

    qtdarco = len(historia["arcos"])

    if qtdarco <= 1:
        arc.configure(text=f"Arco: {len(historia["arcos"])}")
    else:
        arc.configure(text=f"Arcos: {len(historia["arcos"])}")

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

    mostrar_no_conteudo(frame_lista_conteudo,historia["personagens"],selecionar_personagem,"nome",6,6)

    mostrar_no_conteudo(frame_lista_conteudo,historia["capitulos"],selecionar_capitulo,"nome",6,6)

    mostrar_no_conteudo(frame_lista_conteudo,historia["sistemas_poder"],selecionar_sistemapoder,"nome",6,6)

    mostrar_no_conteudo(frame_lista_conteudo,historia["observacoes"],selecionar_observacoes,"titulo",6,6)

#SELECIONAR ...

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
            itens = [h["nome"] for h in historias.Historias]

        elif opcao == "Arco":
            itens = [a["nome"] for a in historia_selecionada["arcos"]]

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
            gerenciador_personagem.excluir(item)

        elif tipo == "Arco":
            gerenciador_arco.excluir(item)

        elif tipo == "Capítulo":
            gerenciador_capitulo.excluir(item)

        elif tipo == "Observação":
            gerenciador_observacao.excluir(item)

        elif tipo == "História":
            excluir_historia(item)

    ctk.CTkOptionMenu(
        frame_lista_conteudo,
        values=[
            "Personagem",
            "História",
            "Arco",
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
    if historia_selecionada and gerenciador_capitulo.capitulo_selecionado is None:
        gerenciador_capitulo.abrir_criacao()

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