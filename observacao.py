import customtkinter as ctk
from tkinter import messagebox

from widgets import *
import historias
from entry_textbox import configurar_entry, configurar_textbox

# Tipos de relação de uma observação -> chave da lista correspondente na história.
# Ex.: "Personagem" -> "Protagonista" (um dos personagens da história).
TIPOS_RELACAO = {
    "Personagem": "personagens",
    "Arco": "arcos",
    "Capítulo": "capitulos",
    "Sistema de Poder": "sistemas_poder",
}


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
        self.var_tipo_relacao = ctk.StringVar(value="Personagem")
        self.var_relacao = ctk.StringVar(value="")

        self._criar_janela_criacao()
        self._criar_janela_edicao()

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
    # RELAÇÃO: tipo -> escolhido
    # ---------------------------------------------------------------

    def _nomes_do_tipo(self, tipo):
        historia_selecionada = self.obter_historia_selecionada()

        chave = TIPOS_RELACAO.get(tipo)

        if historia_selecionada is None or chave is None:
            return []

        return [item["nome"] for item in historia_selecionada.get(chave, [])]

    def _atualizar_escolhidos(self, option_escolhido, tipo, atual=None):
        """Preenche o menu 'escolhido' com os itens do tipo e seleciona um deles."""

        nomes = self._nomes_do_tipo(tipo)

        # Se o item atual foi renomeado/excluído, mantém o valor na lista para
        # que salvar não troque a relação sem o usuário perceber.
        if atual and atual not in nomes:
            nomes.insert(0, atual)

        if not nomes:
            nomes = [""]

        option_escolhido.configure(values=nomes)
        self.var_relacao.set(atual if atual in nomes else nomes[0])

    def _criar_seletor_relacao(self, pai):
        """Cria 'tipo -> escolhido' (ex.: Personagem -> Protagonista)."""

        frame = ctk.CTkFrame(pai, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        option_escolhido = ctk.CTkOptionMenu(
            frame, values=[""], variable=self.var_relacao, width=200
        )

        option_tipo = ctk.CTkOptionMenu(
            frame,
            values=list(TIPOS_RELACAO),
            variable=self.var_tipo_relacao,
            width=160,
            command=lambda tipo: self._atualizar_escolhidos(option_escolhido, tipo)
        )

        option_tipo.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(frame, text="→").grid(row=0, column=1, padx=8)
        option_escolhido.grid(row=0, column=2, sticky="ew")

        return frame, option_tipo, option_escolhido

    # ---------------------------------------------------------------
    # JANELA DE CRIAÇÃO
    # ---------------------------------------------------------------

    def _criar_janela_criacao(self):

        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("600x500")
        self.toplevel.title("Criar observação")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, width=600, height=500)
        self.janela_criacao.pack(fill="both", expand=True)
        self.janela_criacao.grid_propagate(False)

        self.janela_criacao.grid_columnconfigure(0, weight=0)
        self.janela_criacao.grid_columnconfigure(1, weight=1)

        for i in range(4):
            self.janela_criacao.grid_rowconfigure(i, weight=1)

        ctk.CTkLabel(self.janela_criacao, text="Relação:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        seletor, self.option_tipo_relacao, self.option_relacao = self._criar_seletor_relacao(
            self.janela_criacao
        )
        seletor.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

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
                                command=lambda:self.toplevel.withdraw())
        fechar.grid(row=3, column=0)

    def _preparar_relacao_criacao(self):
        self.var_tipo_relacao.set("Personagem")
        self._atualizar_escolhidos(self.option_relacao, "Personagem")

    def abrir_criacao(self):

        historia_selecionada = self.obter_historia_selecionada()

        if historia_selecionada is None:
            print("Selecione a historia primeiro")
            return

        self._preparar_relacao_criacao()

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

        novo = criar_observacoes(
            historia_selecionada,
            self.var_relacao.get(),
            self.entry_titulo.get(),
            self.text_conteudo.get("1.0", "end").strip(),
            self.var_tipo_relacao.get()
        )

        if novo:

            criar_label_obs(
                novo,
                self.frame_lista_conteudo,
                self.selecionar_observacoes
            )

            self.selecionar_observacoes(novo)
            ocultar_frame(self.janela_criacao)

            self.entry_titulo.delete(0, "end")
            self.text_conteudo.delete("1.0", "end")

            if self.apos_criar:
                self.apos_criar(historia_selecionada)

            self.toplevel.withdraw()

    # ---------------------------------------------------------------
    # SELECIONAR / LISTAR
    # ---------------------------------------------------------------

    def selecionar(self, observacao):
        # Nome usado pelo interface.py ao clicar numa observação da lista da história.
        self.selecionar_observacoes(observacao)

    def selecionar_observacoes(self, observacao):

        self.observacao_selecionada = observacao

        self._limpar_frame_conteudo()

        # Cabeçalho: título à esquerda e botão Editar à direita
        cabecalho = ctk.CTkFrame(self.frame_lista_conteudo, fg_color="transparent")
        cabecalho.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            cabecalho,
            text=f"📝 {observacao.get('titulo', '')}",
            font=("Helvetica", 22, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.editar()
        ).pack(side="right")

        # O título já aparece no cabeçalho
        for chave, valor in observacao.items():

            if chave == "titulo":
                continue

            ctk.CTkLabel(self.frame_lista_conteudo, text=f"{chave}:").pack(anchor="w", padx=10)
            ctk.CTkLabel(self.frame_lista_conteudo, text=str(valor), wraplength=900, justify="left").pack(anchor="w", padx=10)

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
                command=lambda o=observacao: self.navegar(self.selecionar_observacoes, o)
            )

            botao_card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="ew")

    # ---------------------------------------------------------------
    # EDITAR
    # ---------------------------------------------------------------

    def editar(self, *args):

        if self.obter_historia_selecionada() is None:
            print("Nenhuma história selecionada")
            return

        observacao = self.observacao_selecionada

        if observacao is None:
            print("Nenhuma observação selecionada")
            return

        self.observacao_em_edicao = observacao

        # Relação = tipo -> escolhido. No modelo, "tipo" guarda o tipo e "nome" o
        # item escolhido. Observações antigas não têm "tipo": eram sempre personagem.
        tipo_atual = observacao.get("tipo", "Personagem")

        if tipo_atual not in TIPOS_RELACAO:
            tipo_atual = "Personagem"

        self.var_tipo_relacao.set(tipo_atual)
        self._atualizar_escolhidos(
            self.option_relacao_edicao, tipo_atual, observacao.get("nome", "")
        )

        self.entry_titulo_edicao.delete(0, "end")
        self.entry_titulo_edicao.insert(0, observacao.get("titulo", ""))

        self.text_conteudo_edicao.delete("1.0", "end")
        self.text_conteudo_edicao.insert("1.0", observacao.get("conteudo", ""))

        self.toplevel_edicao.deiconify()
        self.toplevel_edicao.lift()
        self.toplevel_edicao.focus_force()
        self.entry_titulo_edicao.focus()

    def _salvar_edicao(self):

        historia_selecionada = self.obter_historia_selecionada()
        observacao = self.observacao_em_edicao

        if historia_selecionada is None or observacao is None:
            return

        titulo = self.entry_titulo_edicao.get().strip()

        if not titulo:
            messagebox.showwarning(
                "Editar observação", "Digite um título para a observação.",
                parent=self.toplevel_edicao
            )
            return

        if titulo != observacao.get("titulo") and any(
            o.get("titulo") == titulo for o in historia_selecionada["observacoes"]
        ):
            messagebox.showwarning(
                "Editar observação", "Já existe uma observação com esse título.",
                parent=self.toplevel_edicao
            )
            return

        observacao["tipo"] = self.var_tipo_relacao.get()
        observacao["nome"] = self.var_relacao.get()
        observacao["titulo"] = titulo
        observacao["conteudo"] = self.text_conteudo_edicao.get("1.0", "end-1c")

        historias.atualizar()

        self.toplevel_edicao.withdraw()

        self.selecionar_observacoes(observacao)

    def _criar_janela_edicao(self):
        self.observacao_em_edicao = None

        self.toplevel_edicao = ctk.CTkToplevel(self.janela)
        self.toplevel_edicao.geometry("600x500")
        self.toplevel_edicao.title("Editar observação")
        self.toplevel_edicao.resizable(False, False)
        self.toplevel_edicao.protocol("WM_DELETE_WINDOW", self.toplevel_edicao.withdraw)

        self.toplevel_edicao.withdraw()

        frame = ctk.CTkFrame(self.toplevel_edicao)
        frame.pack(fill="both", expand=True)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(frame, text="Editar Observação").grid(
            column=0, row=0, columnspan=2, pady=10
        )

        ctk.CTkLabel(frame, text="Relação:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

        seletor, self.option_tipo_relacao_edicao, self.option_relacao_edicao = (
            self._criar_seletor_relacao(frame)
        )
        seletor.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(frame, text="Título:").grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.entry_titulo_edicao = ctk.CTkEntry(frame)
        self.entry_titulo_edicao.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        configurar_entry(self.entry_titulo_edicao)

        ctk.CTkLabel(frame, text="Conteúdo:").grid(row=3, column=0, padx=10, pady=10, sticky="nw")

        self.text_conteudo_edicao = ctk.CTkTextbox(frame, height=180)
        self.text_conteudo_edicao.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        configurar_textbox(self.text_conteudo_edicao)

        ctk.CTkButton(
            frame, text="Fechar",
            command=lambda: self.toplevel_edicao.withdraw()
        ).grid(row=4, column=0, padx=10, pady=10)

        ctk.CTkButton(
            frame, text="Salvar",
            command=lambda: self._salvar_edicao()
        ).grid(row=4, column=1, padx=10, pady=10)

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