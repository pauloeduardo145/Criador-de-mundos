import customtkinter as ctk

class Config:

    def __init__(self, janela, modo_escuro=None):
        self.modo_escuro = modo_escuro
        self.janela = janela
        self.config_atual = {}  # substitua por storage.carregar_config() quando integrar

    def janela_confg(self):

        self.janela_config = ctk.CTkToplevel(self.janela)
        self.janela_config.geometry("1000x450")
        self.janela_config.title("Configurações")
        self.janela_config.resizable(False, False)
        self.janela_config.protocol("WM_DELETE_WINDOW", self.janela_config.withdraw)
        self.janela_config.grid_columnconfigure(0, weight=0)
        self.janela_config.grid_columnconfigure(1, weight=0)
        self.janela_config.grid_columnconfigure(2, weight=3)

        self.janela_config.withdraw()

        self.frame_barra = ctk.CTkFrame(self.janela_config, width=250, height=450)
        self.frame_barra.grid(column=0, row=0, sticky="nsew", padx=0)
        self.frame_barra.grid_propagate(False)

        self.frame_barra.grid_columnconfigure(0, weight=1)
        self.frame_barra.grid_columnconfigure(1, weight=1)

        barra = ctk.CTkFrame(self.janela_config, width=5, height=450, fg_color="white")
        barra.grid(column=1, row=0, padx=0, pady=0)

        self.frame_conteudo = ctk.CTkFrame(self.janela_config, height=450)
        self.frame_conteudo.grid(column=2, row=0, sticky="nsew")
        self.frame_conteudo.grid_propagate(False)

        botoes = [
            ("Geral", self.exibir_geral),
            ("Aparência", self.exibir_aparencia),
            ("Sobre", self.exibir_sobre),
        ]

        for indice, (texto, comando) in enumerate(botoes):
            self.frame_barra.rowconfigure(indice, weight=0)
            ctk.CTkButton(
                self.frame_barra, text=texto, width=20, height=30, command=comando
            ).grid(column=0, row=indice, sticky="ewn", columnspan=2, padx=5, pady=2)

        self.exibir_geral()  # painel inicial

    def mostrar(self):
        self.janela_config.deiconify()

    def esconder(self):
        self.janela_config.withdraw()

    def _limpar_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def _salvar_e_atualizar(self, chave, valor):
        self.config_atual[chave] = valor
        # substitua pela chamada real, ex.: storage.salvar_config(self.config_atual)

    def exibir_geral(self):
        self._limpar_conteudo()
        ctk.CTkLabel(
            self.frame_conteudo, text="Configurações Gerais",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")

        var_notificacoes = ctk.BooleanVar(value=self.config_atual.get("notificacoes", True))
        ctk.CTkSwitch(
            self.frame_conteudo, text="Ativar notificações", variable=var_notificacoes,
            command=lambda: self._salvar_e_atualizar("notificacoes", var_notificacoes.get())
        ).pack(pady=10, padx=20, anchor="w")

    def _alterar_tema(self, novo_tema):
        ctk.set_appearance_mode(novo_tema)
        if self.modo_escuro is not None:
            self.modo_escuro.set(novo_tema == "Escuro")
        self._salvar_e_atualizar("tema", novo_tema)

    def exibir_aparencia(self):
        self._limpar_conteudo()
        ctk.CTkLabel(
            self.frame_conteudo, text="Aparência",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")

        ctk.CTkLabel(self.frame_conteudo, text="Tema:").pack(padx=20, anchor="w")
        ctk.CTkOptionMenu(
            self.frame_conteudo, values=["Claro", "Escuro", "Sistema"],
            command=self._alterar_tema
        ).pack(pady=10, padx=20, anchor="w")

    def exibir_sobre(self):
        from updater import VERSAO_ATUAL
        self._limpar_conteudo()
        ctk.CTkLabel(
            self.frame_conteudo, text="Sobre o Criador de Mundos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        ctk.CTkLabel(self.frame_conteudo, text=f"Versão atual {VERSAO_ATUAL}").pack(padx=20, anchor="w")
        ctk.CTkButton(self.frame_conteudo, text="Verificar atualizações").pack(pady=15, padx=20, anchor="w")