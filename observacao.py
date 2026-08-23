import customtkinter as ctk
from tkinter import messagebox

from widgets import *
import historias
from entry_textbox import configurar_entry, configurar_textbox


class Observacao:

    def __init__(self, janela, frame_lista_conteudo,
                 obter_historia_selecionada, apos_criar=None, navegar=None):

        self.janela = janela
        self.frame_lista_conteudo = frame_lista_conteudo
        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar
        # Callback opcional (mesmo formato do "navegar" do interface.py) para
        # manter o histórico de navegação ao clicar em um card da listagem.
        # Se não for informado, seleciona diretamente sem registrar histórico.
        self.navegar = navegar if navegar is not None else (lambda funcao, *args: funcao(*args))

        self.observacao_selecionada = None
        self.var_relacao = ctk.StringVar(value="")

        self._criar_janela_criacao()

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

    # ---------------------------------------------------------------
    # JANELA DE CRIAÇÃO
    # ---------------------------------------------------------------

    def _criar_janela_criacao(self):

        self.janela_criacao = ctk.CTkFrame(self.janela, width=600, height=500)
        self.janela_criacao.grid_propagate(False)

        self.janela_criacao.grid_columnconfigure(0, weight=0)
        self.janela_criacao.grid_columnconfigure(1, weight=1)

        for i in range(4):
            self.janela_criacao.grid_rowconfigure(i, weight=1)

        self.option_relacao = ctk.CTkOptionMenu(
            self.janela_criacao, values=[""], variable=self.var_relacao, width=250
        )
        self.option_relacao.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.janela_criacao, text="Título:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.entry_titulo = ctk.CTkEntry(self.janela_criacao)
        self.entry_titulo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        configurar_entry(self.entry_titulo)

        self.text_conteudo = ctk.CTkTextbox(self.janela_criacao, height=180)
        self.text_conteudo.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        configurar_textbox(self.text_conteudo)

        salvaobs = ctk.CTkButton(self.janela_criacao, text="[Salva]", command=lambda: self.salvar())
        salvaobs.grid(row=3, column=1)

        fechar = ctk.CTkButton(self.janela_criacao, text="Fechar",
                                command=lambda: ocultar_frame(self.janela_criacao))
        fechar.grid(row=3, column=0)

    def _atualizar_optionmenu_personagens(self):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            self.option_relacao.configure(values=[""])
            self.var_relacao.set("")
            return

        nomes = [p["nome"] for p in historia_selecionada["personagens"]]

        if not nomes:
            nomes = [""]

        self.option_relacao.configure(values=nomes)
        self.var_relacao.set(nomes[0])

    def abrir_criacao(self):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Selecione a historia primeiro")
            return

        self._atualizar_optionmenu_personagens()

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

        novo = criar_observacoes(
            historia_selecionada,
            self.var_relacao.get(),
            self.entry_titulo.get(),
            self.text_conteudo.get("1.0", "end").strip()
        )

        if novo:

            criar_label_obs(
                novo,
                self.frame_lista_conteudo,
                self.selecionar
            )

            self.selecionar(novo)
            ocultar_frame(self.janela_criacao)

            self.entry_titulo.delete(0, "end")
            self.text_conteudo.delete("1.0", "end")

            if self.apos_criar:
                self.apos_criar(historia_selecionada)

            print(novo)

    # ---------------------------------------------------------------
    # SELECIONAR / LISTAR
    # ---------------------------------------------------------------

    def selecionar(self, observacao):

        self.observacao_selecionada = observacao

        self._limpar_frame_conteudo()

        for chave, valor in observacao.items():
            ctk.CTkLabel(self.frame_lista_conteudo, text=f"{chave}:").pack(anchor="w", padx=10)
            ctk.CTkLabel(self.frame_lista_conteudo, text=str(valor), wraplength=900, justify="left").pack(anchor="w", padx=10)

        edit = ctk.CTkButton(self.frame_lista_conteudo, text="Editar", command=lambda *args: self.editar())
        edit.pack(pady=10)

    def mostrar_todos(self, event=None):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Nenhuma história selecionada")
            return

        observacoes = historia_selecionada.get("observacoes", [])

        self._limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_lista_conteudo,
            text=f"📂 Todas as observações/curiosidades ({len(observacoes)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        grid_obs = ctk.CTkFrame(self.frame_lista_conteudo, fg_color="transparent")
        grid_obs.pack(fill="both", expand=True, padx=20)

        for indice, observacao in enumerate(observacoes):

            linha = indice // 6
            coluna = indice % 6

            botao_card = ctk.CTkButton(
                grid_obs,
                text=observacao["titulo"],
                command=lambda o=observacao: self.navegar(self.selecionar, o)
            )

            botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

    # ---------------------------------------------------------------
    # EDITAR
    # ---------------------------------------------------------------

    def editar(self, *args):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Nenhuma história selecionada")
            return

        if self.observacao_selecionada is None:
            print("Nenhuma observação selecionada")
            return

        self._limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_lista_conteudo,
            text="Modo Edição (Observação)",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        # Relação
        ctk.CTkLabel(self.frame_lista_conteudo, text="Relação:").pack(padx=10, pady=5)

        relacao = ctk.CTkEntry(self.frame_lista_conteudo)
        relacao.insert(0, self.observacao_selecionada.get("relacao", ""))
        relacao.pack(fill="x", padx=10, pady=5)
        configurar_entry(relacao)

        # Título
        ctk.CTkLabel(self.frame_lista_conteudo, text="Título:").pack(padx=10, pady=5)

        titulo_obs = ctk.CTkEntry(self.frame_lista_conteudo)
        titulo_obs.insert(0, self.observacao_selecionada.get("titulo", ""))
        titulo_obs.pack(fill="x", padx=10, pady=5)
        configurar_entry(titulo_obs)

        # Conteúdo
        ctk.CTkLabel(self.frame_lista_conteudo, text="Conteúdo:").pack(padx=10, pady=5)

        conteudo = ctk.CTkTextbox(self.frame_lista_conteudo, height=150)
        conteudo.insert("1.0", self.observacao_selecionada.get("conteudo", ""))
        conteudo.pack(fill="both", expand=True, padx=10, pady=5)
        configurar_textbox(conteudo)

        def salvar_edicao():

            self.observacao_selecionada["relacao"] = relacao.get()
            self.observacao_selecionada["titulo"] = titulo_obs.get()
            self.observacao_selecionada["conteudo"] = conteudo.get("1.0", "end-1c")

            historias.salvar_dados(historias.Historias)

            self.selecionar(self.observacao_selecionada)

        def fechar_sem_salvar():
            confirmar = messagebox.askyesno(
                "Cancelar edição",
                "Deseja sair sem salvar as alterações?"
            )

            if confirmar:
                self.selecionar(self.observacao_selecionada)

        ctk.CTkButton(
            self.frame_lista_conteudo,
            text="Salvar",
            command=salvar_edicao
        ).pack(pady=10)

        ctk.CTkButton(
            self.frame_lista_conteudo,
            text="Fechar sem salvar",
            command=fechar_sem_salvar
        ).pack(pady=10)

        self._arearolavel()

    # ---------------------------------------------------------------
    # EXCLUIR
    # ---------------------------------------------------------------

    def excluir(self, titulo):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            return

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

        if self.observacao_selecionada is observacao:
            self.observacao_selecionada = None

        historias.salvar_dados(historias.Historias)

        self.mostrar_todos()