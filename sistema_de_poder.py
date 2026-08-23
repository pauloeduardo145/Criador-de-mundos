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

    # ---------------------------------------------------------------
    # JANELA DE CRIAÇÃO
    # ---------------------------------------------------------------

    def _criar_janela_criacao(self):

        self.janela_criacao = ctk.CTkFrame(self.janela, width=600, height=500)
        self.janela_criacao.grid_propagate(False)
        self.janela_criacao.grid_columnconfigure(0, weight=0)
        self.janela_criacao.grid_columnconfigure(1, weight=1)

        for i in range(6):
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
                                     command=lambda: ocultar_frame(self.janela_criacao))
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

        mostrar_frame(self.janela_criacao)
        self.janela_criacao.focus()

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
                self.selecionar
            )

            self.selecionar(novo)

            ocultar_frame(self.janela_criacao)

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

        self.sistema_selecionado = sistema

        self._limpar_frame_conteudo()

        for chave, valor in sistema.items():

            if chave in ["id", "historia_id"]:
                continue

            ctk.CTkLabel(self.frame_lista_conteudo, text=f"{chave}:").pack(anchor="w", padx=10)
            ctk.CTkLabel(self.frame_lista_conteudo, text=str(valor), wraplength=900, justify="left").pack(anchor="w", padx=10)

        edit = ctk.CTkButton(self.frame_lista_conteudo, text="Editar", command=lambda *args: self.editar())
        edit.pack(pady=10)

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

        self.mostrar_no_conteudo(self.frame_lista_conteudo, sistemas, self.selecionar, "nome", 1, 1)

    # ---------------------------------------------------------------
    # EDITAR
    # ---------------------------------------------------------------

    def editar(self, *args):

        if self.sistema_selecionado is None:
            print("Nenhum sistema de poder selecionado")
            return

        self._limpar_frame_conteudo()

        titulo = ctk.CTkLabel(self.frame_lista_conteudo, text="Modo Edição", font=("Helvetica", 18, "bold"))
        titulo.pack(pady=10, anchor="w", padx=20)

        # Nome
        ctk.CTkLabel(self.frame_lista_conteudo, text="Nome:").pack(anchor="w", padx=10)
        nome = ctk.CTkEntry(self.frame_lista_conteudo)
        nome.insert(0, self.sistema_selecionado["nome"])
        nome.pack(fill="x", padx=10, pady=5)
        configurar_entry(nome)

        # Descrição
        ctk.CTkLabel(self.frame_lista_conteudo, text="Descrição:").pack(anchor="w", padx=10)
        descricao = ctk.CTkTextbox(self.frame_lista_conteudo, height=100)
        descricao.insert("1.0", self.sistema_selecionado["descricao"])
        descricao.pack(fill="x", padx=10, pady=5)
        configurar_textbox(descricao)

        # Regras
        ctk.CTkLabel(self.frame_lista_conteudo, text="Regras:").pack(anchor="w", padx=10)
        regras = ctk.CTkTextbox(self.frame_lista_conteudo, height=100)
        regras.insert("1.0", self.sistema_selecionado["regras"])
        regras.pack(fill="x", padx=10, pady=5)
        configurar_textbox(regras)

        # Vantagens
        ctk.CTkLabel(self.frame_lista_conteudo, text="Vantagens:").pack(anchor="w", padx=10)
        vantagens = ctk.CTkTextbox(self.frame_lista_conteudo, height=100)
        vantagens.insert("1.0", self.sistema_selecionado["vantagens"])
        vantagens.pack(fill="x", padx=10, pady=5)
        configurar_textbox(vantagens)

        # Fraquezas
        ctk.CTkLabel(self.frame_lista_conteudo, text="Fraquezas:").pack(anchor="w", padx=10)
        fraquezas = ctk.CTkTextbox(self.frame_lista_conteudo, height=100)
        fraquezas.insert("1.0", self.sistema_selecionado["fraquezas"])
        fraquezas.pack(fill="x", padx=10, pady=5)
        configurar_textbox(fraquezas)

        def salvar_edicao():

            self.sistema_selecionado["nome"] = nome.get()
            self.sistema_selecionado["descricao"] = descricao.get("1.0", "end-1c")
            self.sistema_selecionado["regras"] = regras.get("1.0", "end-1c")
            self.sistema_selecionado["vantagens"] = vantagens.get("1.0", "end-1c")
            self.sistema_selecionado["fraquezas"] = fraquezas.get("1.0", "end-1c")

            historias.salvar_dados(historias.Historias)

            self.selecionar(self.sistema_selecionado)

        botao_salvar = ctk.CTkButton(self.frame_lista_conteudo, text="Salvar", command=lambda: salvar_edicao())
        botao_salvar.pack(pady=10)

        self._arearolavel()

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