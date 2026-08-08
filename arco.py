import customtkinter as ctk
from widgets import mostrar_frame, ocultar_frame, criar_arco, criar_titulo_arco
from tkinter import messagebox
import historias


class Arco:
    def __init__(self, janela, frame_conteudo, obter_historia_selecionada=None, apos_criar=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo

        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        # Compartilhada com a janela de criação de Capítulo, que também
        # precisa deixar o usuário escolher a qual arco o capítulo pertence.
        self.arco_var = ctk.StringVar(value="Sem arco")

        self._criar_janela_criacao()

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

        mostrar_frame(self.janela_criacao)
        self.janela_criacao.focus()

    def _salvar_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            return

        if "arcos" not in historia:
            historia["arcos"] = []

        novo = criar_arco(historia, self.arconame_criacao.get())

        if novo:
            criar_titulo_arco(novo, self.frame_conteudo, historia)

            ocultar_frame(self.janela_criacao)

            historias.atualizar()

            self.atualizar_optionmenu()

            if self.apos_criar:
                self.apos_criar(historia)

    def _criar_janela_criacao(self):
        self.janela_criacao = ctk.CTkFrame(self.janela, width=300, height=220)
        self.janela_criacao.grid_propagate(False)

        for i in range(2):
            self.janela_criacao.grid_columnconfigure(i, weight=1)

        self.janela_criacao.place(relx=0.5, rely=0.5, anchor="center")
        self.janela_criacao.place_forget()

        ctk.CTkLabel(self.janela_criacao, text="Criar Arco").grid(column=0, row=0, columnspan=2)

        self.arconame_criacao = ctk.CTkEntry(self.janela_criacao, width=300)
        self.arconame_criacao.grid(column=0, row=2, columnspan=2)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: ocultar_frame(self.janela_criacao)
        ).grid(column=0, row=3)

        ctk.CTkButton(
            self.janela_criacao, text="[Criar Arco]",
            command=lambda: self._salvar_criacao()
        ).grid(column=1, row=3, columnspan=2)