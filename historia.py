import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

import historias
from widgets import criar_historia, criar_label
from entry_textbox import configurar_entry


class Historia:
    """
    Gerencia a HISTÓRIA (singular): listar, criar, selecionar e excluir
    histórias, além do painel de informações e das seções de conteúdo
    (personagens, arcos, capítulos, sistemas de poder e observações).

    Não confundir com `historias.py`, que cuida apenas do carregamento e
    da persistência dos dados em disco.
    """

    def __init__(self, janela, frame_lista, painel_info, frame_lista_conteudo,
                 mostrar_secao, limpar_frame_conteudo, arearolavel,
                 secoes, apos_selecionar=None):

        self.janela = janela
        self.frame_lista = frame_lista
        self.frame_lista_conteudo = frame_lista_conteudo

        self.mostrar_secao = mostrar_secao
        self.limpar_frame_conteudo = limpar_frame_conteudo
        self.arearolavel = arearolavel

        # Lista de tuplas (titulo, chave_lista, callback_selecionar, chave_nome),
        # uma por seção exibida ao selecionar uma história.
        self.secoes = secoes

        self.apos_selecionar = apos_selecionar

        self.historia_selecionada = None

        self._criar_painel_info(painel_info)
        self._criar_janela_criacao()

    # ---------------------------------------------------------------
    # PAINEL DE INFORMAÇÕES
    # ---------------------------------------------------------------

    def _criar_painel_info(self, painel_info):

        self.nome_historia = ctk.CTkLabel(painel_info, text='Nome:')
        self.nome_historia.grid(column=0, row=0, sticky="w", padx=10, pady=5)

        self.arc = ctk.CTkLabel(painel_info, text='Arco:')
        self.arc.grid(column=0, row=1, sticky="w", padx=10, pady=5)

        self.cap = ctk.CTkLabel(painel_info, text='Capitulo:')
        self.cap.grid(column=0, row=2, sticky="w", padx=10, pady=5)

        self.pers = ctk.CTkLabel(painel_info, text='Personagem:')
        self.pers.grid(column=0, row=3, sticky="w", padx=10, pady=5)

        self.ue = ctk.CTkLabel(painel_info, text='Ultima Edição:')
        self.ue.grid(column=0, row=4, sticky="w", padx=10, pady=5)

        self.sp = ctk.CTkLabel(painel_info, text='Sistema(as) de Poder(es):')
        self.sp.grid(column=0, row=5, sticky="w", padx=10, pady=5)

    # ---------------------------------------------------------------
    # LISTAGEM
    # ---------------------------------------------------------------

    def carregar_lista(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        for indice, historia in enumerate(historias.Historias):
            criar_label(
                historia,
                self.frame_lista,
                self.selecionar,
                row=indice
            )

    # ---------------------------------------------------------------
    # SELECIONAR
    # ---------------------------------------------------------------

    def selecionar(self, historia):
        self.historia_selecionada = historia

        historia["ultima_edicao"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        self.nome_historia.configure(text=f"Nome: {historia['nome']}")

        qtdarco = len(historia["arcos"])

        if qtdarco <= 1:
            self.arc.configure(text=f"Arco: {qtdarco}")
        else:
            self.arc.configure(text=f"Arcos: {qtdarco}")

        qtdcap = len(historia["capitulos"])

        if qtdcap == 1:
            self.cap.configure(text=f"Capítulo: {qtdcap}")
        else:
            self.cap.configure(text=f"Capítulos: {qtdcap}")

        self.ue.configure(text=f"UE: {historia.get('ultima_edicao', 'Nunca')}")

        qtdper = len(historia["personagens"])

        if qtdper == 1:
            self.pers.configure(text=f"Personagem: {qtdper}")
        else:
            self.pers.configure(text=f"Personagens: {qtdper}")

        qtdsistema = len(historia["sistemas_poder"])

        if historia["sistemas_poder"]:
            if qtdsistema <= 1:
                self.sp.configure(text=f"Sistema de Poder: {qtdsistema}")
            else:
                self.sp.configure(text=f"Sistemas de Poderes: {qtdsistema}")
        else:
            self.sp.configure(text="Sistema P: Nenhum")

        self.limpar_frame_conteudo()

        for titulo, chave_lista, callback, chave_nome in self.secoes:
            self.mostrar_secao(
                self.frame_lista_conteudo,
                titulo,
                historia[chave_lista],
                callback,
                chave_nome
            )

        self.arearolavel()

        if self.apos_selecionar:
            self.apos_selecionar(historia)

    # ---------------------------------------------------------------
    # EXCLUSÃO
    # ---------------------------------------------------------------

    def excluir(self, nome):

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

        historias.atualizar()

        self.historia_selecionada = None

        self.carregar_lista()

        self.limpar_frame_conteudo()

    # ---------------------------------------------------------------
    # JANELA "CRIAR HISTÓRIA"
    # ---------------------------------------------------------------

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("300x150")
        self.toplevel.title("Criar história")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, fg_color="black", width=300, height=150)
        self.janela_criacao.pack(fill="both", expand=True)
        self.janela_criacao.grid_propagate(False)
        self.janela_criacao.grid_columnconfigure(0, weight=1)
        self.janela_criacao.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.janela_criacao, text="Criar Historia").grid(
            column=0, row=0, padx=10, pady=10, columnspan=2
        )

        def enter_historia(event):
            self._salvar_criacao()

        self.nome_criacao = ctk.CTkEntry(self.janela_criacao, placeholder_text="Nome da Historia")
        self.nome_criacao.bind("<Return>", enter_historia)
        self.nome_criacao.grid(column=0, row=1, sticky="nsew", columnspan=2, padx=10)
        configurar_entry(self.nome_criacao)

        ctk.CTkButton(
            self.janela_criacao, text="Fechar",
            command=lambda: self.toplevel.withdraw()
        ).grid(column=0, row=3, padx=5, pady=10)

        ctk.CTkButton(
            self.janela_criacao, text="Criar Historia",
            command=lambda: self._salvar_criacao()
        ).grid(column=1, row=3, padx=5, pady=10)

    def abrir_criacao(self):
        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()
        self.nome_criacao.focus()

    def _salvar_criacao(self):
        nova = criar_historia(self.nome_criacao.get())

        if nova:
            self.carregar_lista()

            self.nome_criacao.delete(0, "end")

            self.toplevel.withdraw()
