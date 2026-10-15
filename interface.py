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

ctk.set_appearance_mode("dark")

historico = []

data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")

#JANELAS

janela = ctk.CTk()
janela.title("Criador de Mundos")

# Tamanho baseado na tela atual (em vez de um valor fixo), para que a janela
# caiba em qualquer monitor. Pode ser redimensionada ou maximizada normalmente.
_largura_tela = janela.winfo_screenwidth()
_altura_tela = janela.winfo_screenheight()
janela.geometry(f"{int(_largura_tela * 0.9)}x{int(_altura_tela * 0.9)}")
janela.minsize(min(800, _largura_tela), min(500, _altura_tela))

# Coluna 0 = barra lateral (largura mínima fixa); coluna 1 = conteúdo (expande).
janela.grid_columnconfigure(0, weight=0, minsize=240)
janela.grid_columnconfigure(1, weight=1)
# Linha 0 = caixa do perfil; linhas 1 e 2 dividem a altura restante.
janela.grid_rowconfigure(0, weight=0)
janela.grid_rowconfigure(1, weight=1)
janela.grid_rowconfigure(2, weight=1)

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

def quebrar_botoes_em_linhas(container, botoes, padx=5, pady=5):
    def _reorganizar(event=None):
        disponivel = container.winfo_width()
        if disponivel <= 1:
            return
        linha = 0
        coluna = 0
        usado = 0
        for botao in botoes:
            largura = botao.winfo_reqwidth() + 2 * padx
            if coluna > 0 and usado + largura > disponivel:
                linha += 1
                coluna = 0
                usado = 0
            botao.grid(row=linha, column=coluna, padx=padx, pady=pady, sticky="w")
            usado += largura
            coluna += 1

    container.bind("<Configure>", _reorganizar)
    container.after(100, _reorganizar)

#CONTEUDO

frame_conteudo = ctk.CTkFrame(janela)
for _c in range(5):
    frame_conteudo.grid_columnconfigure(_c, weight=1)
frame_conteudo.grid_rowconfigure(0, weight=0)
frame_conteudo.grid_rowconfigure(1, weight=0)
frame_conteudo.grid_rowconfigure(2, weight=1)
frame_conteudo.grid_rowconfigure(3, weight=0)
frame_conteudo.grid(column=1, row=0, rowspan=3, sticky="nsew", padx=5, pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0,columnspan=5, sticky="n",padx=5,pady=5)

#LABEL DO CONTEUDO

# Sem width/height fixos: o frame ocupa todo o espaço disponível (sticky nsew).
frame_lista_conteudo = ctk.CTkScrollableFrame(frame_conteudo,orientation="vertical")
frame_lista_conteudo.grid(column=0,row=2,columnspan=5, sticky="nsew",padx=10)

#CONTEUDO DO HISTORIA

frame_botoes = ctk.CTkFrame(frame_conteudo)
frame_botoes.grid(column=0,row=3,columnspan=5,sticky="ew",padx=10,pady=5)

Addper = ctk.CTkButton(frame_botoes,height=25,text="[Criar Personagem]",command=lambda: gerenciador_personagem.abrir_criacao())

Addarco = ctk.CTkButton(frame_botoes,height=25,text="[Criar Arco]",command=lambda: gerenciador_arco.abrir_criacao())

capitadic = ctk.CTkButton(frame_botoes,height=25,text="[Criar Capitulo]",command=lambda: gerenciador_capitulo.abrir_criacao())

Addposis = ctk.CTkButton(frame_botoes,height=25,text="[Criar Sistema de Poder]",command=lambda: gerenciador_sistema_poder.abrir_criacao())

Addespecie = ctk.CTkButton(frame_botoes,height=25, text="[Criar Espécies]", command=lambda: gerenciador_especies.abrir_criacao())

Addobs = ctk.CTkButton(frame_botoes,height=25,text="[Adicionar Observação]", command=lambda: gerenciador_observacao.abrir_criacao())

quebrar_botoes_em_linhas(
    frame_botoes,
    [Addper, Addarco, capitadic, Addposis, Addespecie, Addobs],
    padx=10,
    pady=8
)

#HISTORIAS

frame_historia = ctk.CTkFrame(janela,width=220)
frame_historia.grid_propagate(False)
frame_historia.grid_columnconfigure(0,weight=1)
frame_historia.grid_rowconfigure(0,weight=0)
frame_historia.grid_rowconfigure(1,weight=1)
frame_historia.grid_rowconfigure(2,weight=0)
frame_historia.grid(column=0,row=1,sticky="nsew",padx=10,pady=5)

menu = ctk.CTkLabel(frame_historia,text='HISTÓRIAS')
menu.grid(column=0,row=0,sticky="n",padx=10,pady=5)

criah = ctk.CTkButton(frame_historia, text="[Criar historias]",command=lambda:gerenciador_historia.abrir_criacao())
criah.grid(column=0,row=2,sticky="s",padx=10,pady=6)

#LABEL DO HISTORIA

frame_lista = ctk.CTkScrollableFrame(frame_historia)
frame_lista.grid_columnconfigure(0,weight=1)
frame_lista.grid_rowconfigure(0,weight=0)
frame_lista.grid(column=0,row=1,sticky="nsew",padx=10,pady=5)
frame_lista._scrollbar.configure(height=0)

#INFORMAÇÕES

frame_inf = ctk.CTkFrame(janela,width=220)
frame_inf.grid_propagate(False)
frame_inf.grid_columnconfigure(0,weight=1)
frame_inf.grid_rowconfigure(0,weight=0)
frame_inf.grid_rowconfigure(1,weight=1)
frame_inf.grid(column=0,row=2,sticky="nsew",padx=10,pady=5)

inicio = ctk.CTkLabel(frame_inf,text='INFORMAÇÕES')
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=5)

lista = ctk.CTkFrame(frame_inf,width=200,height=100)
lista.grid_propagate(False)
lista.grid_columnconfigure(0,weight=1)
for _r in range(7):
    lista.grid_rowconfigure(_r,weight=0)
lista.grid(column=0,row=1,sticky="nsew",padx=10,pady=5)

# Os labels do painel de informações (Nome, Arco, Capítulo, Personagem,
# Última Edição, Sistema de Poder) agora são criados pela classe Historia,
# que recebe este frame `lista` como painel_info.

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

#FUNÇÕES GENÉRICAS DE LISTAGEM (usadas por Personagem, Capítulo, Sistema de Poder e Observações)

def colunas_disponiveis(largura_item, minimo=1, maximo=10):
    # Calcula quantas colunas cabem na largura atual da área de conteúdo.
    largura = frame_lista_conteudo.winfo_width()
    if largura <= 1:
        largura = janela.winfo_width() - 300
    return max(minimo, min(maximo, largura // largura_item))

def mostrar_cards_com_imagem(frame,itens,callback,chave_imagem="imagens",chave_nome="nome",tamanho=150):

    grid = ctk.CTkFrame(frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=20)

    n_colunas = colunas_disponiveis(tamanho + 40)

    for indice, item in enumerate(itens):

        linha = indice // n_colunas
        coluna = indice % n_colunas

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

    # Os parâmetros li/col são mantidos por compatibilidade, mas o número de
    # colunas agora se adapta à largura da tela.
    n_colunas = colunas_disponiveis(170)

    for i in range(n_colunas):
        grid.grid_columnconfigure(i, weight=1)

    for indice, item in enumerate(itens):

        linha = indice // n_colunas
        coluna = indice % n_colunas

        ctk.CTkButton(
            grid,
            text=item[chave_nome],
            height=40,
            command=lambda i=item: navegar(callback, i)
        ).grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

def mostrar_secao(frame, titulo, itens, callback, chave_nome):

    secao = ctk.CTkFrame(frame, fg_color="transparent")
    secao.pack(fill="x", padx=10, pady=10)

    label = ctk.CTkLabel(
        secao,
        text=f"{titulo} ({len(itens)})",
        font=("Helvetica", 18, "bold")
    )
    label.pack(anchor="w", pady=(5, 5))

    mostrar_no_conteudo(
        secao,
        itens,
        callback,
        chave_nome,
        6,
        6
    )

#GERENCIADORES (ARCO, CAPITULO, PERSONAGEM)

from arco import Arco
from capitulo import Capitulo
from personagem import Personagem
from sistema_de_poder import SistemaDePoder
from observacao import Observacao
from historia import Historia
from especie import Especie

def selecionar_sistemapoder(sistemapode):
    gerenciador_sistema_poder.selecionar(sistemapode)

def selecionar_observacoes(observacao):
    gerenciador_observacao.selecionar(observacao)

def selecionar_personagem(personagem):
    gerenciador_personagem.selecionar_personagem(personagem)

def selecionar_capitulo(capitulo):
    gerenciador_capitulo.selecionar_capitulo(capitulo)

def selecionar_arco(arco):
    gerenciador_arco.selecionar_arco(arco)

def selecionar_especie(especie):
    gerenciador_especies.selecionar_especie(especie)

gerenciador_historia = Historia(
    janela,
    frame_lista,
    lista,
    frame_lista_conteudo,
    mostrar_secao,
    limpar_frame_conteudo,
    arearolavel,
    secoes=[
        ("Personagens", "personagens", selecionar_personagem, "nome"),
        ("Arcos", "arcos", selecionar_arco, "nome"),
        ("Capítulos", "capitulos", selecionar_capitulo, "nome"),
        ("Sistemas de Poder", "sistemas_poder", selecionar_sistemapoder, "nome"),
        ("Observações", "observacoes", selecionar_observacoes, "titulo"),
        ("Especies", "especies", selecionar_especie, "nome")
    ]
)

gerenciador_arco = Arco(
    janela,
    frame_lista_conteudo,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h),
    limpar_frame_conteudo=limpar_frame_conteudo,
    arearolavel=arearolavel,
    abrir_capitulo=lambda c: navegar(selecionar_arco, c)
)

gerenciador_capitulo = Capitulo(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    gerenciador_arco,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h)
)

gerenciador_personagem = Personagem(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    mostrar_cards_com_imagem,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h),
    abrir_criacao_especie=lambda: gerenciador_especies.abrir_criacao(),
    abrir_criacao_sistema_poder=lambda: gerenciador_sistema_poder.abrir_criacao()
)

gerenciador_sistema_poder = SistemaDePoder(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h),
    ao_criar_sistema=lambda sistema: gerenciador_personagem.atualizar_sistemas(sistema)
)

gerenciador_observacao = Observacao(
    janela,
    frame_lista_conteudo,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h),
    # "navegar" só é definido mais abaixo no arquivo; a lambda resolve o
    # nome no momento da chamada (late binding), então funciona normalmente.
    navegar=lambda funcao, *args: navegar(funcao, *args)
)

gerenciador_especies = Especie(
    janela,
    frame_lista_conteudo,
    mostrar_no_conteudo,
    obter_historia_selecionada=lambda: gerenciador_historia.historia_selecionada,
    apos_criar=lambda h: gerenciador_historia.selecionar(h),
    ao_criar_especie=lambda e: gerenciador_personagem.atualizar_especies(e))

def edicao_sistempoder(*args):
    gerenciador_sistema_poder.editar()

def mostrar_todos_sistemas_poder(event=None):
    gerenciador_sistema_poder.mostrar_todos(event)

def edicao_observacao(*args):
    gerenciador_observacao.editar()

def mostrar_todas_observacoes(event=None):
    gerenciador_observacao.mostrar_todos(event)

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

def edicao_capitulo(*args):
    gerenciador_capitulo.edicao_capitulo()

def mostrar_todos_capitulos(event=None):
    gerenciador_capitulo.mostrar_todos(event)

def edicao_especie(*args):
    gerenciador_especies.edicao_especie()

def mostrar_todas_especies(*args):
    gerenciador_especies.mostrar_todos()

#RECEBER INFORMAÇÕES DA HISTORIA SELECIONADA

def navegar(funcao, *args):
    historico.append((funcao, args))
    funcao(*args)

def voltar():

    if len(historico) > 1:
        historico.pop()

        funcao, args = historico[-1]

        funcao(*args)

#SELECIONAR ...

def excluir_item(*args):

    limpar_frame_conteudo()

    tipo_var = ctk.StringVar(value="Escolha")
    item_var = ctk.StringVar(value="Nenhum")

    option_item = None

    def atualizar_lista_exclusao(opcao):

        nonlocal option_item

        if opcao == "Personagem":
            itens = [p["nome"] for p in gerenciador_historia.historia_selecionada["personagens"]]

        elif opcao == "História":
            itens = [h["nome"] for h in historias.Historias]

        elif opcao == "Arco":
            itens = [a["nome"] for a in gerenciador_historia.historia_selecionada["arcos"]]

        elif opcao == "Capítulo":
            itens = [c["nome"] for c in gerenciador_historia.historia_selecionada["capitulos"]]

        elif opcao == "Observação":
            itens = [o["titulo"] for o in gerenciador_historia.historia_selecionada["observacoes"]]

        elif opcao == "Sistemapoder":
            itens = [s["nome"] for s in gerenciador_historia.historia_selecionada["sistemas_poder"]]

        elif opcao == "Especie":
            itens = [e["nome"] for e in gerenciador_historia.historia_selecionada["especies"]]

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

        elif tipo == "Sistemapoder":
            gerenciador_sistema_poder.excluir(item)

        elif tipo == "História":
            gerenciador_historia.excluir(item)

        elif tipo == "Especie":
            gerenciador_especies.excluir(item)

    ctk.CTkOptionMenu(
        frame_lista_conteudo,
        values=[
            "Personagem",
            "História",
            "Arco",
            "Capítulo",
            "Observação",
            "Sistemapoder",
            "Especie"
        ],
        variable=tipo_var,
        command=atualizar_lista_exclusao
    ).pack(pady=10)

    ctk.CTkButton(
        frame_lista_conteudo,
        text="Excluir",
        command=confirmar_exclusao
    ).pack(pady=15)

#CAIXA

from perfil import Perfil

caixa_frame = ctk.CTkFrame(janela,width=220,height=30)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,sticky="ew",padx=10,pady=5)

perfil_config = ctk.CTkButton(caixa_frame,height=10,text="👤",fg_color="black",width=4,font=("Helvetica", 7), command=lambda: Perfil(janela).abrir_perfil())
perfil_config.grid(column=0,row=0,sticky="n",padx=5,pady=5)

#MOSTRAR NO CONTEUDO

lista_conteudo = ctk.CTkFrame(frame_conteudo)
lista_conteudo.grid(column=0,row=1,sticky="ew",columnspan=5,padx=10,pady=5)

botao_voltar = ctk.CTkButton(lista_conteudo,text="← Voltar",command=lambda: voltar())

botao_pers= ctk.CTkButton(lista_conteudo, text="Personagem",command=lambda: navegar(mostrar_todos_personagens))

botao_capi= ctk.CTkButton(lista_conteudo, text="Capitulo",command=lambda: navegar(mostrar_todos_capitulos))

botao_image= ctk.CTkButton(lista_conteudo, text="Imagens",command=lambda: navegar(mostrar_todas_imagens))

botao_image_galeria= ctk.CTkButton(lista_conteudo, text="Galeria",command=lambda: navegar(mostrar_todas_imagens_da_galeria))

botao_sispower = ctk.CTkButton(lista_conteudo,text="Sistema de pd",command=lambda: navegar(mostrar_todos_sistemas_poder))

botao_obser = ctk.CTkButton(lista_conteudo,text="Observação",command=lambda: navegar(mostrar_todas_observacoes))

botao_especie = ctk.CTkButton(lista_conteudo, text="Especie",command=lambda: navegar(mostrar_todas_especies))

botao_excluir= ctk.CTkButton(lista_conteudo,text="Excluir",command=lambda: excluir_item())

quebrar_botoes_em_linhas(
    lista_conteudo,
    [
        botao_voltar, botao_pers, botao_capi, botao_image,
        botao_image_galeria, botao_sispower, botao_obser,
        botao_especie, botao_excluir
    ],
    padx=5,
    pady=5
)

#ATALHOS GLOBAIS

def sh():
    if gerenciador_historia.historia_selecionada is not None:
        pass
    else:
        gerenciador_historia.abrir_criacao()

janela.bind("<F5>", lambda e: gerenciador_historia.selecionar(gerenciador_historia.historia_selecionada))

janela.bind("<Control-n>", lambda event: sh())

def sc():
    if gerenciador_historia.historia_selecionada and gerenciador_capitulo.capitulo_selecionado is None:
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

from confg import Config

config = Config(janela)
config.janela_confg()

gerenciador_historia.carregar_lista()

def carregar():
    import os
    import json

    historia_json = os.path.expanduser("~/Documentos/Criador de Mundos/historias.json")

    chaves = ["personagens", "capitulos", "sistemas_poder", "observacoes", "arcos", "especies"]

    with open(historia_json, "r", encoding="utf-8") as f:
        historias = json.load(f)

    for historia in historias:
        for chave in chaves:
            if chave not in historia:
                historia[chave] = []

    with open(historia_json, "w", encoding="utf-8") as f:
        json.dump(historias, f, ensure_ascii=False, indent=4)

    return historias

carregar()

janela.mainloop()