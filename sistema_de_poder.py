import customtkinter as ctk
from tkinter import messagebox

from widgets import *
import historias
from entry_textbox import configurar_entry, configurar_textbox


class SistemaDePoder:

    def __init__(self, janela, frame_lista_conteudo, mostrar_no_conteudo,
                 obter_historia_selecionada, apos_criar=None):

        self.janela = janela
        self.frame_lista_conteudo = frame_lista_conteudo
        self.mostrar_no_conteudo = mostrar_no_conteudo
        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        self.sistema_selecionado = None

        self._criar_janela_criacao()
        self._criar_janela_edicao()

    # ---------------------------------------------------------------
    # JANELA DE CRIAÇÃO
    # ---------------------------------------------------------------

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("1000x590")
        self.toplevel.title("Criar sistema de poderes")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, width=1000, height=590)
        self.janela_criacao.pack(fill="both", expand=True)
        self.janela_criacao.grid_columnconfigure(0, weight=0)
        self.janela_criacao.grid_columnconfigure(1, weight=1)

        for i in range(7):  # inclui a linha dos botões
            self.janela_criacao.grid_rowconfigure(i, weight=1)

        powerlabel = ctk.CTkLabel(self.janela_criacao, text="Adicionar sistema de poderes")
        powerlabel.grid(column=0, row=0, columnspan=2)

        powerlabename = ctk.CTkLabel(self.janela_criacao, text="Nome: ")
        powerlabename.grid(column=0, row=1)

        self.entry_nome = ctk.CTkEntry(self.janela_criacao, placeholder_text="Nome do sistema de poder")
        self.entry_nome.grid(column=1, row=1, columnspan=2, sticky="ew")
        configurar_entry(self.entry_nome)

        powerlabelconteudo = ctk.CTkLabel(self.janela_criacao, text="Conteudo:")
        powerlabelconteudo.grid(column=0, row=2)

        self.text_conteudo = ctk.CTkTextbox(self.janela_criacao, height=50, activate_scrollbars=True)
        self.text_conteudo.grid(column=1, row=2, sticky="ew", columnspan=2)
        configurar_textbox(self.text_conteudo)

        powerlabelregras = ctk.CTkLabel(self.janela_criacao, text="Regras:")
        powerlabelregras.grid(column=0, row=3)

        self.text_regras = ctk.CTkTextbox(self.janela_criacao, width=300, height=50, activate_scrollbars=True)
        self.text_regras.grid(column=1, row=3, sticky="ew", columnspan=2)
        configurar_textbox(self.text_regras)

        powerlabelvantagens = ctk.CTkLabel(self.janela_criacao, text="Vantagens:")
        powerlabelvantagens.grid(column=0, row=4)

        self.text_vantagens = ctk.CTkTextbox(self.janela_criacao, height=50, activate_scrollbars=True)
        self.text_vantagens.grid(column=1, row=4, sticky="ew", columnspan=2)
        configurar_textbox(self.text_vantagens)

        powerlabelfraquezas = ctk.CTkLabel(self.janela_criacao, text="Fraquezas:")
        powerlabelfraquezas.grid(column=0, row=5)

        self.text_fraquezas = ctk.CTkTextbox(self.janela_criacao, height=50, activate_scrollbars=True)
        self.text_fraquezas.grid(column=1, row=5, sticky="ew", columnspan=2)
        configurar_textbox(self.text_fraquezas)

        powerfechar = ctk.CTkButton(self.janela_criacao, text="[Fechar]",
                                     command=lambda: self.toplevel.withdraw())
        powerfechar.grid(column=0, row=6)

        powersalvar = ctk.CTkButton(self.janela_criacao, text="[Criar Sistema de poder]",
                                     command=lambda: self.salvar())
        powersalvar.grid(column=1, row=6)


    # ---------------------------------------------------------------
    # UTILITÁRIOS
    # ---------------------------------------------------------------

    def _limpar_frame_conteudo(self):
        for widget in self.frame_lista_conteudo.winfo_children():
            widget.destroy()

        self.frame_lista_conteudo.update_idletasks()
        self.frame_lista_conteudo._parent_canvas.configure(
            scrollregion=self.frame_lista_conteudo._parent_canvas.bbox("all")
        )
        self.frame_lista_conteudo._parent_canvas.yview_moveto(0)

    def _arearolavel(self):
        self.frame_lista_conteudo.update_idletasks()
        self.frame_lista_conteudo._parent_canvas.configure(
            scrollregion=self.frame_lista_conteudo._parent_canvas.bbox("all")
        )
        self.frame_lista_conteudo._parent_canvas.yview_moveto(0)

    def abrir_criacao(self):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Selecione a historia primeiro")
            return

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    # ---------------------------------------------------------------
    # CRIAR / SALVAR
    # ---------------------------------------------------------------

    def salvar(self):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Nenhuma história selecionada")
            return

        novo = criar_sistemadepoder(
            historia_selecionada,
            self.entry_nome.get(),
            self.text_conteudo.get("1.0", "end-1c"),
            self.text_regras.get("1.0", "end-1c"),
            self.text_vantagens.get("1.0", "end-1c"),
            self.text_fraquezas.get("1.0", "end-1c")
        )

        if novo:

            criar_label_sistema_poder(
                novo,
                self.frame_lista_conteudo,
                self.selecionar_sistemapoder
            )

            self.selecionar_sistemapoder(novo)

            self.toplevel.withdraw()

            self.entry_nome.delete(0, "end")
            self.text_conteudo.delete("1.0", "end")
            self.text_regras.delete("1.0", "end")
            self.text_vantagens.delete("1.0", "end")
            self.text_fraquezas.delete("1.0", "end")

            if self.apos_criar:
                self.apos_criar(historia_selecionada)

            print(novo)

    # ---------------------------------------------------------------
    # SELECIONAR / LISTAR
    # ---------------------------------------------------------------

    def selecionar(self, sistema):
        self.selecionar_sistemapoder(sistema)

    def selecionar_sistemapoder(self, sistema):

        self.sistema_selecionado = sistema

        self._limpar_frame_conteudo()

        # Cabeçalho: título à esquerda e botão Editar à direita
        cabecalho = ctk.CTkFrame(self.frame_lista_conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            cabecalho,
            text=f"⚡ {sistema['nome']}",
            font=("Helvetica", 22, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.editar()
        ).pack(side="right")

        # O nome já está no título
        for chave, valor in sistema.items():

            if chave in ["id", "historia_id", "nome"]:
                continue

            ctk.CTkLabel(self.frame_lista_conteudo, text=f"{chave}:").pack(anchor="w", padx=10)
            ctk.CTkLabel(self.frame_lista_conteudo, text=str(valor), wraplength=900, justify="left").pack(anchor="w", padx=10)

    def mostrar_todos(self, event=None):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Nenhuma história selecionada")
            return

        sistemas = historia_selecionada["sistemas_poder"]

        self._limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_lista_conteudo,
            text=f"📂 Todos os sistemas de poder ({len(sistemas)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        self.mostrar_no_conteudo(self.frame_lista_conteudo, sistemas, self.selecionar_sistemapoder, "nome", 1, 1)

    # ---------------------------------------------------------------
    # EDITAR
    # ---------------------------------------------------------------

    def editar(self, *args):

        if self.obter_historia_selecionada() is None:
            print("Nenhuma história selecionada")
            return

        sistema = self.sistema_selecionado

        if sistema is None:
            print("Nenhum sistema de poder selecionado")
            return

        self.sistema_em_edicao = sistema

        self.entry_nome_edicao.delete(0, "end")
        self.entry_nome_edicao.insert(0, sistema["nome"])

        for chave, caixa in self.campos_edicao.items():
            caixa.delete("1.0", "end")
            caixa.insert("1.0", sistema.get(chave, ""))

        self.toplevel_edicao.deiconify()
        self.toplevel_edicao.lift()
        self.toplevel_edicao.focus_force()
        self.entry_nome_edicao.focus()

    def _salvar_edicao(self):

        historia_selecionada = self.obter_historia_selecionada()
        sistema = self.sistema_em_edicao

        if historia_selecionada is None or sistema is None:
            return

        nome = self.entry_nome_edicao.get().strip()

        if not nome:
            messagebox.showwarning(
                "Editar sistema de poder", "Digite um nome para o sistema de poder.",
                parent=self.toplevel_edicao
            )
            return

        if nome != sistema["nome"] and any(
            s["nome"] == nome for s in historia_selecionada["sistemas_poder"]
        ):
            messagebox.showwarning(
                "Editar sistema de poder", "Já existe um sistema de poder com esse nome.",
                parent=self.toplevel_edicao
            )
            return

        sistema["nome"] = nome

        for chave, caixa in self.campos_edicao.items():
            sistema[chave] = caixa.get("1.0", "end-1c")

        historias.atualizar()

        self.toplevel_edicao.withdraw()

        self.selecionar_sistemapoder(sistema)

    def _criar_janela_edicao(self):
        self.sistema_em_edicao = None

        self.toplevel_edicao = ctk.CTkToplevel(self.janela)
        self.toplevel_edicao.geometry("800x650")
        self.toplevel_edicao.title("Editar sistema de poderes")
        self.toplevel_edicao.resizable(False, False)
        self.toplevel_edicao.protocol("WM_DELETE_WINDOW", self.toplevel_edicao.withdraw)

        self.toplevel_edicao.withdraw()

        frame = ctk.CTkFrame(self.toplevel_edicao)
        frame.pack(fill="both", expand=True)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        for i in range(2, 6):
            frame.grid_rowconfigure(i, weight=1)

        ctk.CTkLabel(frame, text="Editar sistema de poderes").grid(
            column=0, row=0, columnspan=2, pady=10
        )

        ctk.CTkLabel(frame, text="Nome:").grid(column=0, row=1, padx=10)

        self.entry_nome_edicao = ctk.CTkEntry(frame, placeholder_text="Nome do sistema de poder")
        self.entry_nome_edicao.grid(column=1, row=1, sticky="ew", padx=10)
        self.entry_nome_edicao.bind("<Return>", lambda e: self._salvar_edicao())
        configurar_entry(self.entry_nome_edicao)

        campos = [
            ("descricao", "Descrição:"),
            ("regras", "Regras:"),
            ("vantagens", "Vantagens:"),
            ("fraquezas", "Fraquezas:"),
        ]

        self.campos_edicao = {}

        for indice, (chave, rotulo) in enumerate(campos):
            linha = 2 + indice

            ctk.CTkLabel(frame, text=rotulo).grid(column=0, row=linha, padx=10)

            caixa = ctk.CTkTextbox(frame, height=80, activate_scrollbars=True)
            caixa.grid(column=1, row=linha, sticky="nsew", padx=10, pady=5)
            configurar_textbox(caixa)

            self.campos_edicao[chave] = caixa

        ctk.CTkButton(
            frame, text="Fechar",
            command=lambda: self.toplevel_edicao.withdraw()
        ).grid(column=0, row=6, padx=10, pady=10)

        ctk.CTkButton(
            frame, text="Salvar",
            command=lambda: self._salvar_edicao()
        ).grid(column=1, row=6, padx=10, pady=10)

    # ---------------------------------------------------------------
    # EXCLUIR
    # ---------------------------------------------------------------

    def excluir(self, nome):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            return

        sistema = next(
            (s for s in historia_selecionada["sistemas_poder"] if s["nome"] == nome),
            None
        )

        if sistema is None:
            return

        if not messagebox.askyesno(
            "Excluir",
            f'Deseja realmente excluir o sistema de poder "{nome}"?'
        ):
            return

        historia_selecionada["sistemas_poder"].remove(sistema)

        if self.sistema_selecionado is sistema:
            self.sistema_selecionado = None

        historias.salvar_dados(historias.Historias)

        self.mostrar_todos()