import customtkinter as ctk
from widgets import mostrar_frame, ocultar_frame, criar_capitulo, criar_label_capitulo
from entry_textbox import configurar_entry, configurar_textbox
from tkinter import messagebox
import historias

class Capitulo:
    def __init__(self, janela, frame_conteudo,mostrar_no_conteudo, gerenciador_arco,
                 obter_historia_selecionada=None, apos_criar=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo
        self.mostrar_no_conteudo = mostrar_no_conteudo
        self.gerenciador_arco = gerenciador_arco

        self.capitulo_selecionado = None
        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        self._criar_janela_criacao()
        self._criar_janela_edicao()

    def limpar_frame_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        # Força o canvas a recalcular a área rolável com base no conteúdo atual
        self.frame_conteudo.update_idletasks()
        self.frame_conteudo._parent_canvas.configure(
            scrollregion=self.frame_conteudo._parent_canvas.bbox("all")
        )
        self.frame_conteudo._parent_canvas.yview_moveto(0)

    def arearolavel(self):
        self.frame_conteudo.update_idletasks()
        self.frame_conteudo._parent_canvas.configure(
            scrollregion=self.frame_conteudo._parent_canvas.bbox("all")
        )
        self.frame_conteudo._parent_canvas.yview_moveto(0)

    def _historia_selecionada(self):
        if self.obter_historia_selecionada is None:
            return None
        return self.obter_historia_selecionada()

    def selecionar_capitulo(self, capitulo):

        self.capitulo_selecionado = capitulo

        # 1. Limpa o frame central para remover o que estava antes
        self.limpar_frame_conteudo()

        # 2. Cabeçalho: título à esquerda e botão Editar à direita
        cabecalho = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            cabecalho,
            text=f"📖 {capitulo['nome']}",
            font=("Helvetica", 22, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.edicao_capitulo()
        ).pack(side="right")

        # 3. Cria um label para cada campo do capítulo (o nome já está no título)
        for chave, valor in capitulo.items():

            if chave == "nome":
                continue

            ctk.CTkLabel(self.frame_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

            ctk.CTkLabel(self.frame_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

        self.arearolavel()

    # ---------- Edição ----------

    def edicao_capitulo(self, *args):

        historia = self._historia_selecionada()

        if historia is None or self.capitulo_selecionado is None:
            print("Nenhuma história ou capítulo selecionado")
            return

        capitulo = self.capitulo_selecionado

        self.capitulo_em_edicao = capitulo

        self.capiname_edicao.delete(0, "end")
        self.capiname_edicao.insert(0, capitulo["nome"])

        # Arcos disponíveis e arco atual do capítulo
        arcos = historia.get("arcos", [])

        nomes_arcos = ["Sem arco"] + [arco["nome"] for arco in arcos]

        arco_atual = next(
            (arco["nome"] for arco in arcos if arco["id"] == capitulo.get("arco_id")),
            "Sem arco"
        )

        self.arco_option_edicao.configure(values=nomes_arcos)
        self.arco_var_edicao.set(arco_atual)

        self.capiconteudo_edicao.delete("1.0", "end")
        self.capiconteudo_edicao.insert("1.0", capitulo.get("conteudo", ""))

        self._atualizar_contador_edicao()

        self.toplevel_edicao.deiconify()
        self.toplevel_edicao.lift()
        self.toplevel_edicao.focus_force()
        self.capiname_edicao.focus()

    def _atualizar_contador_edicao(self, event=None):
        texto = self.capiconteudo_edicao.get("1.0", "end-1c")

        self.contador_edicao.configure(text=f"{len(texto)} caracteres")

    def _salvar_edicao(self):

        historia = self._historia_selecionada()
        capitulo = self.capitulo_em_edicao

        if historia is None or capitulo is None:
            return

        nome = self.capiname_edicao.get().strip()

        if not nome:
            messagebox.showwarning(
                "Editar capítulo", "Digite um nome para o capítulo.",
                parent=self.toplevel_edicao
            )
            return

        if nome != capitulo["nome"] and any(
            c["nome"] == nome for c in historia["capitulos"]
        ):
            messagebox.showwarning(
                "Editar capítulo", "Já existe um capítulo com esse nome.",
                parent=self.toplevel_edicao
            )
            return

        capitulo["nome"] = nome
        capitulo["arco_id"] = self.gerenciador_arco.obter_id_arco(
            self.arco_var_edicao.get()
        )
        capitulo["conteudo"] = self.capiconteudo_edicao.get("1.0", "end-1c")

        historias.atualizar()

        self.toplevel_edicao.withdraw()

        self.selecionar_capitulo(capitulo)

    def _criar_janela_edicao(self):
        self.capitulo_em_edicao = None

        # Variável exclusiva da edição (a do criar capítulo é compartilhada)
        self.arco_var_edicao = ctk.StringVar(value="Sem arco")

        self.toplevel_edicao = ctk.CTkToplevel(self.janela)
        self.toplevel_edicao.geometry("800x600")
        self.toplevel_edicao.title("Editar capítulo")
        self.toplevel_edicao.resizable(False, False)
        self.toplevel_edicao.protocol("WM_DELETE_WINDOW", self.toplevel_edicao.withdraw)

        self.toplevel_edicao.withdraw()

        frame = ctk.CTkFrame(self.toplevel_edicao)
        frame.pack(fill="both", expand=True)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(frame, text="Editar Capítulo").grid(
            column=0, row=0, columnspan=2, pady=10
        )

        self.capiname_edicao = ctk.CTkEntry(frame, placeholder_text="Nome do capítulo")
        self.capiname_edicao.grid(column=0, row=1, columnspan=2, sticky="ew", padx=10)
        self.capiname_edicao.bind("<Return>", lambda e: self._salvar_edicao())
        configurar_entry(self.capiname_edicao)

        self.arco_option_edicao = ctk.CTkOptionMenu(
            frame,
            variable=self.arco_var_edicao,
            values=["Sem arco"],
            width=250
        )
        self.arco_option_edicao.grid(
            column=0, row=2, columnspan=2, padx=10, pady=5, sticky="ew"
        )

        self.capiconteudo_edicao = ctk.CTkTextbox(
            frame, wrap="word", activate_scrollbars=True
        )
        self.capiconteudo_edicao.grid(
            column=0, row=3, columnspan=2, sticky="nsew", padx=10, pady=5
        )
        configurar_textbox(self.capiconteudo_edicao)
        self.capiconteudo_edicao.bind("<KeyRelease>", self._atualizar_contador_edicao)

        self.contador_edicao = ctk.CTkLabel(frame, text="0 caracteres")
        self.contador_edicao.grid(column=0, row=4, columnspan=2)

        ctk.CTkButton(
            frame, text="Fechar",
            command=lambda: self.toplevel_edicao.withdraw()
        ).grid(column=0, row=5, padx=5, pady=10)

        ctk.CTkButton(
            frame, text="Salvar",
            command=lambda: self._salvar_edicao()
        ).grid(column=1, row=5, padx=5, pady=10)

    # ---------- Listagem (usada pela navegação principal) ----------

    def mostrar_todos(self, event=None):
        historia = self._historia_selecionada()

        if historia is None:
            self.limpar_frame_conteudo()

            ctk.CTkLabel(
                self.frame_conteudo,
                text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
                font=("Helvetica", 18),
                justify="center"
            ).pack(expand=True)
            return

        capitulos = historia.get("capitulos", [])
        arcos = historia.get("arcos", [])

        # 1. Limpa o frame central para remover o que estava antes
        self.limpar_frame_conteudo()

        # 2. Cria um título para a seção
        titulo = ctk.CTkLabel(
            self.frame_conteudo,
            text=f"📂 Todos os Capitulos ({len(capitulos)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        # 3. Agrupa os capítulos por arco, na ordem em que os arcos foram criados
        ids_de_arcos = {arco["id"] for arco in arcos}

        capitulos_sem_arco = [
            capitulo for capitulo in capitulos
            if capitulo.get("arco_id") not in ids_de_arcos
        ]

        algum_grupo_exibido = False

        for arco in arcos:

            capitulos_do_arco = [
                capitulo for capitulo in capitulos
                if capitulo.get("arco_id") == arco["id"]
            ]

            if not capitulos_do_arco:
                continue

            algum_grupo_exibido = True

            ctk.CTkLabel(
                self.frame_conteudo,
                text=arco["nome"],
                font=("Helvetica", 16, "bold"),
                anchor="w"
            ).pack(fill="x", padx=20, pady=(15, 5))

            self.mostrar_no_conteudo(
                self.frame_conteudo, capitulos_do_arco, self.selecionar_capitulo, "nome", 6, 6
            )

        if capitulos_sem_arco:

            algum_grupo_exibido = True

            ctk.CTkLabel(
                self.frame_conteudo,
                text="Sem arco",
                font=("Helvetica", 16, "bold"),
                anchor="w"
            ).pack(fill="x", padx=20, pady=(15, 5))

            self.mostrar_no_conteudo(
                self.frame_conteudo, capitulos_sem_arco, self.selecionar_capitulo, "nome", 6, 6
            )

        if not algum_grupo_exibido:
            ctk.CTkLabel(
                self.frame_conteudo,
                text="Nenhum capítulo criado ainda.",
                font=("Helvetica", 14)
            ).pack(pady=10, padx=20, anchor="w")

        self.arearolavel()

    # ---------- Exclusão ----------

    def excluir(self, nome):
        historia = self._historia_selecionada()

        if historia is None:
            return

        capitulo = next(
            (c for c in historia["capitulos"] if c["nome"] == nome),
            None
        )

        if capitulo is None:
            return

        if not messagebox.askyesno(
            "Excluir", f'Deseja realmente excluir o capítulo "{nome}"?'
        ):
            return

        historia["capitulos"].remove(capitulo)

        historias.atualizar()

        if self.apos_criar:
            self.apos_criar(historia)

    # ---------- Janela "Criar Capítulo" ----------

    def abrir_criacao(self):
        if self._historia_selecionada() is None:
            print("Nenhuma história selecionada")
            return
        
        self.gerenciador_arco.atualizar_optionmenu(self.arco_option)

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    def _salvar_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            print("Nenhuma história selecionada")
            return

        # Obtém o arco selecionado NO MOMENTO em que o capítulo é salvo
        nome_arco = self.gerenciador_arco.arco_var.get()
        arco_id = self.gerenciador_arco.obter_id_arco(nome_arco)

        novo = criar_capitulo(
            historia,
            self.capiname_criacao.get(),
            arco_id,
            self.capiconteudo_criacao.get("1.0", "end-1c")
        )

        if novo:

            criar_label_capitulo(
                novo,
                self.frame_conteudo,
                self.selecionar_capitulo
            )

            self.selecionar_capitulo(novo)

            if self.apos_criar:
                self.apos_criar(historia)
        
        self.toplevel.withdraw()

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("1000x600")
        self.toplevel.title("Criar capitulo")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, width=1000, height=590)
        self.janela_criacao.pack(fill="both", expand=False)
        self.janela_criacao.grid_propagate(False)
        self.janela_criacao.grid_columnconfigure(0, weight=1)
        self.janela_criacao.grid_rowconfigure(0, weight=0)
        self.janela_criacao.grid_rowconfigure(1, weight=1)
        self.janela_criacao.grid_rowconfigure(2, weight=0)
        self.janela_criacao.grid_rowconfigure(3, weight=3)
        self.janela_criacao.grid_rowconfigure(4, weight=1)

        def enter_capitulo(event):
            self._salvar_criacao()

        ctk.CTkLabel(self.janela_criacao, text="Insira abaixo o Capitulo").grid(column=0, row=0, columnspan=2)

        self.capiname_criacao = ctk.CTkEntry(self.janela_criacao, placeholder_text="Nome do capítulo")
        self.capiname_criacao.grid(column=0, row=1, sticky="ew", columnspan=2)
        configurar_entry(self.capiname_criacao)

        self.arco_option = ctk.CTkOptionMenu(
            self.janela_criacao,
            variable=self.gerenciador_arco.arco_var,
            values=["Sem arco"],
            width=250
        )
        self.arco_option.grid(column=0, row=2, columnspan=2, padx=10, pady=5, sticky="ew")

        self.gerenciador_arco.atualizar_optionmenu(self.arco_option)

        self.capiconteudo_criacao = ctk.CTkTextbox(
            self.janela_criacao, width=300, height=150, activate_scrollbars=True
        )
        self.capiconteudo_criacao.bind("<Return>", enter_capitulo)
        self.capiconteudo_criacao.grid(column=0, row=3, sticky="nwse", columnspan=2)
        configurar_textbox(self.capiconteudo_criacao)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: self.toplevel.withdraw()
        ).grid(column=0, row=4, sticky="sw")

        ctk.CTkButton(
            self.janela_criacao, text="[Criar Capitulo]",
            command=lambda: self._salvar_criacao()
        ).grid(column=1, row=4,sticky="se" ,columnspan=2)