import customtkinter as ctk
from widgets import mostrar_frame, ocultar_frame, criar_capitulo, criar_label_capitulo
from entry_textbox import configurar_entry, configurar_textbox
from tkinter import messagebox
import historias

class Capitulo:
    def __init__(self, janela, frame_conteudo, mostrar_no_conteudo, gerenciador_arco,
                 obter_historia_selecionada=None, apos_criar=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo
        self.mostrar_no_conteudo = mostrar_no_conteudo
        self.gerenciador_arco = gerenciador_arco

        self.capitulo_selecionado = None
        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        self._criar_janela_criacao()

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

        # 2. Cria um label para cada campo do capítulo
        for chave, valor in capitulo.items():
            ctk.CTkLabel(self.frame_conteudo,text=f"{chave}:").pack(anchor="w",padx=10)

            ctk.CTkLabel(self.frame_conteudo,text=str(valor),wraplength=900,justify="left").pack(anchor="w",padx=10)

        edit = ctk.CTkButton(self.frame_conteudo,text="Editar", command=lambda *args: self.edicao_capitulo())
        edit.pack(pady=10)

        self.arearolavel()

    def edicao_capitulo(self, *args):

        historia = self._historia_selecionada()

        if historia is None or self.capitulo_selecionado is None:
            print("Nenhuma história ou capítulo selecionado")
            return

        capitulo_selecionado = self.capitulo_selecionado

        self.limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_conteudo,
            text="Modo Edição",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        # =========================
        # NOME
        # =========================

        ctk.CTkLabel(
            self.frame_conteudo,
            text="Nome:"
        ).pack(anchor="w", padx=10)

        nome = ctk.CTkEntry(self.frame_conteudo)
        nome.insert(0, capitulo_selecionado["nome"])
        nome.pack(fill="x", padx=10, pady=5)
        configurar_entry(nome)

        # =========================
        # ARCO
        # =========================

        ctk.CTkLabel(
            self.frame_conteudo,
            text="Arco:"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        # Pega todos os arcos da história
        arcos = historia.get("arcos", [])

        nomes_arcos = ["Sem arco"]

        nomes_arcos.extend(
            arco["nome"]
            for arco in arcos
        )

        # Descobre o nome do arco atualmente associado
        arco_atual = "Sem arco"

        arco_id_atual = capitulo_selecionado.get("arco_id")

        if arco_id_atual is not None:

            for arco in arcos:

                if arco["id"] == arco_id_atual:
                    arco_atual = arco["nome"]
                    break

        # Variável exclusiva desta edição
        arco_var_edicao = ctk.StringVar(
            value=arco_atual
        )

        arco_option = ctk.CTkOptionMenu(
            self.frame_conteudo,
            variable=arco_var_edicao,
            values=nomes_arcos,
            width=250
        )

        arco_option.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # =========================
        # CONTEÚDO
        # =========================

        ALTURA_MIN = 80
        ALTURA_MAX = 375

        conteudos = ctk.CTkTextbox(
            self.frame_conteudo,
            wrap="word",
            activate_scrollbars=True
        )

        conteudos.pack(
            fill="x",
            padx=10,
            pady=5
        )

        configurar_textbox(conteudos)

        conteudos.insert(
            "1.0",
            capitulo_selecionado.get("conteudo", "")
        )

        def ajustar_altura(event=None):

            widget = conteudos
            widget.update_idletasks()

            resultado = widget._textbox.count(
                "1.0",
                "end",
                "displaylines"
            )

            linhas = int(resultado[0]) if resultado else 1

            altura_por_linha = 21
            altura_desejada = linhas * altura_por_linha + 20

            nova_altura = max(
                ALTURA_MIN,
                min(altura_desejada, ALTURA_MAX)
            )

            widget.configure(height=nova_altura)

            widget.edit_modified(False)

        ajustar_altura()

        conteudos.bind(
            "<<Modified>>",
            ajustar_altura
        )

        # =========================
        # SALVAR
        # =========================

        def obter_id_arco_edicao():

            nome_arco = arco_var_edicao.get()

            if nome_arco == "Sem arco":
                return None

            for arco in historia.get("arcos", []):

                if arco["nome"] == nome_arco:
                    return arco["id"]

            return None

        def salvar_edicao():

            arco_id = obter_id_arco_edicao()

            capitulo_selecionado["nome"] = nome.get()

            capitulo_selecionado["arco_id"] = arco_id

            capitulo_selecionado["conteudo"] = conteudos.get(
                "1.0",
                "end-1c"
            )

            print("Capítulo salvo:")
            print("Nome:", capitulo_selecionado["nome"])
            print("Arco:", arco_var_edicao.get())
            print("ID do arco:", arco_id)

            historias.atualizar()

            self.selecionar_capitulo(
                capitulo_selecionado
            )

        botao_salvar = ctk.CTkButton(
            self.frame_conteudo,
            text="Salvar",
            command=salvar_edicao
        )

        botao_salvar.pack(pady=10)

        # =========================
        # CONTADOR
        # =========================

        contador = ctk.CTkLabel(
            self.frame_conteudo,
            text="0 caracteres"
        )

        contador.pack(padx=100)

        def atualizar(event=None):

            texto = conteudos.get(
                "1.0",
                "end-1c"
            )

            contador.configure(
                text=f"{len(texto)} caracteres"
            )

        atualizar()

        conteudos.bind(
            "<KeyRelease>",
            atualizar
        )

        self.arearolavel()

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

        mostrar_frame(self.janela_criacao)
        self.janela_criacao.focus()

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

            ocultar_frame(self.janela_criacao)

            if self.apos_criar:
                self.apos_criar(historia)

    def _criar_janela_criacao(self):
        self.janela_criacao = ctk.CTkFrame(self.janela, width=300, height=220)
        self.janela_criacao.grid_propagate(False)
        self.janela_criacao.grid_columnconfigure(0, weight=1)
        self.janela_criacao.grid_rowconfigure(0, weight=0)

        for i in range(5):
            self.janela_criacao.grid_rowconfigure(i, weight=1)

        self.janela_criacao.place(relx=0.5, rely=0.5, anchor="center")
        self.janela_criacao.place_forget()

        def enter_capitulo(event):
            self._salvar_criacao()

        ctk.CTkLabel(self.janela_criacao, text="Insira abaixo o Capitulo").grid(column=0, row=0, columnspan=2)

        self.capiname_criacao = ctk.CTkEntry(self.janela_criacao, placeholder_text="Nome do capítulo")
        self.capiname_criacao.grid(column=0, row=1, sticky="nsew", columnspan=2)
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
        self.capiconteudo_criacao.grid(column=0, row=3, sticky="nsew", columnspan=2)
        configurar_textbox(self.capiconteudo_criacao)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: ocultar_frame(self.janela_criacao)
        ).grid(column=0, row=3)

        ctk.CTkButton(
            self.janela_criacao, text="[Criar Capitulo]",
            command=lambda: self._salvar_criacao()
        ).grid(column=1, row=3, columnspan=2)