import customtkinter as ctk
from widgets import criar_arco, criar_titulo_arco
from tkinter import messagebox
import historias
from entry_textbox import configurar_entry, configurar_textbox


class Arco:
    def __init__(self, janela, frame_conteudo, obter_historia_selecionada=None, apos_criar=None,
                 limpar_frame_conteudo=None, arearolavel=None, abrir_capitulo=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo

        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        # Opcionais, usados por selecionar(): limpar a área de conteúdo,
        # recalcular a rolagem e abrir um capítulo ao clicar nele.
        self.limpar_frame_conteudo = limpar_frame_conteudo
        self.arearolavel = arearolavel
        self.abrir_capitulo = abrir_capitulo

        self.arco_selecionado = None

        # Compartilhada com a janela de criação de Capítulo, que também
        # precisa deixar o usuário escolher a qual arco o capítulo pertence.
        self.arco_var = ctk.StringVar(value="Sem arco")

        self._criar_janela_criacao()
        self._criar_janela_edicao()

    def _historia_selecionada(self):
        if self.obter_historia_selecionada is None:
            return None
        return self.obter_historia_selecionada()

    # ---------- Consultas usadas por outros gerenciadores (ex.: Capítulo) ----------

    def obter_nomes(self):
        historia = self._historia_selecionada()

        nomes = ["Sem arco"]

        if historia:
            nomes.extend(arco["nome"] for arco in historia.get("arcos", []))

        return nomes

    def atualizar_optionmenu(self, menu=None):
        nomes = self.obter_nomes()

        if menu is not None:
            menu.configure(values=nomes)

        if self.arco_var.get() not in nomes:
            self.arco_var.set("Sem arco")

    def obter_id_arco(self, nome_arco):
        if nome_arco == "Sem arco":
            return None

        historia = self._historia_selecionada()

        if not historia:
            return None

        for arco in historia.get("arcos", []):
            if arco["nome"] == nome_arco:
                return arco["id"]

        return None

    # ---------- Seleção ----------

    def selecionar_arco(self, arco):
        """Mostra o arco na área de conteúdo: nome, descrição e seus capítulos."""

        historia = self._historia_selecionada()

        if historia is None:
            return

        self.arco_selecionado = arco

        if self.limpar_frame_conteudo:
            self.limpar_frame_conteudo()
        else:
            for widget in self.frame_conteudo.winfo_children():
                widget.destroy()

        capitulos = [
            c for c in historia.get("capitulos", [])
            if c.get("arco_id") == arco["id"]
        ]

        cabecalho = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            cabecalho,
            text=f"📁 {arco['nome']}",
            font=("Helvetica", 22, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.editar(arco)
        ).pack(side="right")

        ctk.CTkLabel(
            self.frame_conteudo,
            text=arco.get("descricao", "").strip() or "Sem descrição.",
            wraplength=700,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            self.frame_conteudo,
            text=f"Capítulos ({len(capitulos)})",
            font=("Helvetica", 18, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        if not capitulos:
            ctk.CTkLabel(
                self.frame_conteudo,
                text="Nenhum capítulo neste arco."
            ).pack(anchor="w", padx=20)
        else:
            grid = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
            grid.pack(fill="x", padx=20)

            colunas = 4

            for i in range(colunas):
                grid.grid_columnconfigure(i, weight=1)

            for indice, capitulo in enumerate(capitulos):
                ctk.CTkButton(
                    grid,
                    text=capitulo["nome"],
                    height=40,
                    command=lambda c=capitulo: self._abrir_capitulo(c)
                ).grid(
                    row=indice // colunas,
                    column=indice % colunas,
                    padx=5, pady=5, sticky="ew"
                )

        if self.arearolavel:
            self.arearolavel()

    def _abrir_capitulo(self, capitulo):
        if self.abrir_capitulo:
            self.abrir_capitulo(capitulo)

    # ---------- Edição ----------

    def editar(self, arco=None):
        arco = arco or self.arco_selecionado

        if arco is None:
            print("Selecione um arco primeiro")
            return

        self.arco_em_edicao = arco

        self.arconame_edicao.delete(0, "end")
        self.arconame_edicao.insert(0, arco["nome"])

        self.arco_descricao_edicao.delete("1.0", "end")
        self.arco_descricao_edicao.insert("1.0", arco.get("descricao", ""))

        self.toplevel_edicao.deiconify()
        self.toplevel_edicao.lift()
        self.toplevel_edicao.focus_force()
        self.arconame_edicao.focus()

    def _salvar_edicao(self):
        historia = self._historia_selecionada()
        arco = self.arco_em_edicao

        if historia is None or arco is None:
            return

        nome = self.arconame_edicao.get().strip()
        descricao = self.arco_descricao_edicao.get("1.0", "end-1c")

        if not nome:
            messagebox.showwarning(
                "Editar arco", "Digite um nome para o arco.",
                parent=self.toplevel_edicao
            )
            return

        if any(a["nome"] == nome and a["id"] != arco["id"] for a in historia["arcos"]):
            messagebox.showwarning(
                "Editar arco", "Já existe um arco com esse nome.",
                parent=self.toplevel_edicao
            )
            return

        # Os capítulos apontam para o arco pelo id, então renomear é seguro.
        arco["nome"] = nome
        arco["descricao"] = descricao

        historias.atualizar()

        self.atualizar_optionmenu()

        self.toplevel_edicao.withdraw()

        # Atualiza o painel e as listas da história (o nome pode ter mudado)
        # e depois volta para a tela do arco editado.
        if self.apos_criar:
            self.apos_criar(historia)

        self.selecionar_arco(arco)

    def _criar_janela_edicao(self):
        self.arco_em_edicao = None

        self.toplevel_edicao = ctk.CTkToplevel(self.janela)
        self.toplevel_edicao.geometry("320x340")
        self.toplevel_edicao.title("Editar arco")
        self.toplevel_edicao.resizable(False, False)
        self.toplevel_edicao.protocol("WM_DELETE_WINDOW", self.toplevel_edicao.withdraw)

        self.toplevel_edicao.withdraw()

        frame = ctk.CTkFrame(self.toplevel_edicao)
        frame.pack(fill="both", expand=True)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Editar Arco").grid(
            column=0, row=0, columnspan=2, pady=10
        )

        self.arconame_edicao = ctk.CTkEntry(frame, placeholder_text="Nome do arco")
        self.arconame_edicao.grid(column=0, row=1, columnspan=2, sticky="ew", padx=10)
        self.arconame_edicao.bind("<Return>", lambda e: self._salvar_edicao())
        configurar_entry(self.arconame_edicao)

        self.arco_descricao_edicao = ctk.CTkTextbox(frame)
        self.arco_descricao_edicao.grid(
            column=0, row=2, columnspan=2, sticky="nsew", padx=10, pady=10
        )
        configurar_textbox(self.arco_descricao_edicao)

        ctk.CTkButton(
            frame, text="Fechar",
            command=lambda: self.toplevel_edicao.withdraw()
        ).grid(column=0, row=3, padx=5, pady=(0, 10))

        ctk.CTkButton(
            frame, text="Salvar",
            command=lambda: self._salvar_edicao()
        ).grid(column=1, row=3, padx=5, pady=(0, 10))

    # ---------- Exclusão ----------

    def excluir(self, nome):
        historia = self._historia_selecionada()

        if historia is None:
            return

        arco = next(
            (a for a in historia["arcos"] if a["nome"] == nome),
            None
        )

        if arco is None:
            return

        if not messagebox.askyesno(
            "Excluir", f'Deseja realmente excluir esse arco "{nome}"?'
        ):
            return

        historia["arcos"].remove(arco)

        historias.atualizar()

        self.atualizar_optionmenu()

        if self.apos_criar:
            self.apos_criar(historia)

    # ---------- Janela "Criar Arco" ----------

    def abrir_criacao(self):
        if self._historia_selecionada() is None:
            print("Selecione a historia primeiro")
            return

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    def _salvar_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            return

        if "arcos" not in historia:
            historia["arcos"] = []

        nome = self.arconame_criacao.get()
        descricao = self.arco_descriao.get("1.0", "end-1c")

        novo = criar_arco(historia, nome, descricao)

        if novo:
            criar_titulo_arco(novo, self.frame_conteudo, historia)

            self.toplevel.withdraw()

            historias.atualizar()

            self.atualizar_optionmenu()

            if self.apos_criar:
                self.apos_criar(historia)

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("300x300")
        self.toplevel.title("Criar arco")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, width=300, height=300)
        self.janela_criacao.pack(fill="both", expand=True)

        for i in range(2):
            self.janela_criacao.grid_columnconfigure(i, weight=1)

        for i in range(3):
            if i == 0:
                self.toplevel.rowconfigure(0, weight=0)

            self.toplevel.rowconfigure(i,weight=1)

        self.janela_criacao.place(relx=0.5, rely=0.5, anchor="center")
        #self.janela_criacao.place_forget()

        ctk.CTkLabel(self.janela_criacao, text="Criar Arco").grid(column=0, row=0, columnspan=2)

        self.arconame_criacao = ctk.CTkEntry(self.janela_criacao, width=300)
        self.arconame_criacao.grid(column=0, row=2, columnspan=2)
        configurar_entry(self.arconame_criacao)

        self.arco_descriao = ctk.CTkTextbox(self.janela_criacao, width=300)
        self.arco_descriao.grid(column=0, row=3, columnspan=2)
        configurar_textbox(self.arco_descriao)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: self.toplevel.withdraw()
        ).grid(column=0, row=4)

        ctk.CTkButton(
            self.janela_criacao, text="[Criar Arco]",
            command=lambda: self._salvar_criacao()
        ).grid(column=1, row=4, columnspan=4)