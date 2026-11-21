import customtkinter as ctk
import historias

from tkinter import filedialog, messagebox
from widgets import criar_especie, criar_label_especie, atualizar_especie, vincular_toplevel

class Especie:
    def __init__(self, janela, frame_conteudo, mostrar_no_conteudo,
                 obter_historia_selecionada=None, apos_criar=None, ao_criar_especie=None):

        self.janela = janela
        self.ao_criar_especie = ao_criar_especie
        self.frame_conteudo = frame_conteudo
        self.mostrar_no_conteudo = mostrar_no_conteudo

        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        self.especie_selecionada = None

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

    # ---------------------------------------------------------------
    # RELAÇÃO: tipo -> especie
    # ---------------------------------------------------------------

    def selecionar_especie(self, especie):
        self.especie_selecionada = especie

        self.limpar_frame_conteudo()

        
        # A coluna 1 se estica para o botão Editar ficar na borda direita
        self.frame_conteudo.grid_columnconfigure(1, weight=1)

        # Cabeçalho: título à esquerda e botão Editar à direita
        cabecalho = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 5))
        cabecalho.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.edicao_especie()
        ).grid(row=0, column=1, sticky="e")

        frame_info = ctk.CTkFrame(self.frame_conteudo, width=600, height=600)
        frame_info.grid_columnconfigure(0, weight=1)
        frame_info.grid(row=1, column=1,sticky="nsew",padx=20)

        ctk.CTkLabel(
            frame_info,
            text=f"🧬 Espécie {especie['nome']}",
            font=("Helvetica", 22, "bold"),
            anchor="w"
        ).grid(row=0, column=0,sticky="ew",padx=10, pady=(10, 5))

        ctk.CTkLabel(
            frame_info,
            text="Descrição:",
            font=("Arial", 16, "bold"),
            anchor="w"
        ).grid(row=1, column=0,sticky="ew",padx=10, pady=(5, 5))

        label = ctk.CTkLabel(
            frame_info,
            text=especie.get("descricao", ""),
            anchor="nw",
            justify="left",
            wraplength=300
        )
        label.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 15))

        label.bind("<Configure>", lambda e: label.configure(wraplength=e.width))   

    def mostrar_todos(self, event=None):
        historia = self._historia_selecionada()

        self.limpar_frame_conteudo()

        if historia is None:
            ctk.CTkLabel(
                self.frame_conteudo,
                text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
                font=("Helvetica", 18),
                justify="center"
            ).pack(expand=True)
            return

        especies = historia.get("especies", [])

        ctk.CTkLabel(
            self.frame_conteudo,
            text=f"🧬 Todas as Espécies ({len(especies)})",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10, anchor="w", padx=20)

        self.mostrar_no_conteudo(self.frame_conteudo, especies, self.selecionar_especie, "nome", 6, 6)

    def excluir(self, nome):
        historia = self._historia_selecionada()

        if historia is None:
            return

        especie = next(
            (p for p in historia["especies"] if p["nome"] == nome),
            None
        )

        if especie is None:
            return

        if not messagebox.askyesno(
            "Excluir", f'Deseja realmente excluir a especie "{nome}"?'
        ):
            return

        historia["especies"].remove(especie)

        historias.atualizar()

        if self.apos_criar:
            self.apos_criar(historia)

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        vincular_toplevel(self.toplevel, self.janela)
        self.toplevel.geometry("500x400")
        self.toplevel.title("Criar espécie")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel.withdraw)
        self.toplevel.withdraw()

        frame = ctk.CTkFrame(self.toplevel)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            frame, text="Nova espécie",
            font=("Helvetica", 22, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        ctk.CTkLabel(frame, text="Nome:").grid(
            row=1, column=0, sticky="w"
        )

        self.nome_especie_criacao = ctk.CTkEntry(
            frame, placeholder_text="Nome da espécie"
        )
        self.nome_especie_criacao.grid(
            row=2, column=0, sticky="ew", pady=(5, 12)
        )

        ctk.CTkLabel(frame, text="Descrição:").grid(
            row=3, column=0, sticky="nw"
        )

        self.descricao_especie_criacao = ctk.CTkTextbox(
            frame, height=150
        )
        self.descricao_especie_criacao.grid(
            row=4, column=0, sticky="nsew", pady=5
        )

        ctk.CTkButton(
            frame,
            text="Salvar espécie",
            command=self._salvar_criacao
        ).grid(row=5, column=0, sticky="ew", pady=(15, 0))


    def abrir_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            print("Selecione uma história primeiro")
            return

        self.nome_especie_criacao.delete(0, "end")
        self.descricao_especie_criacao.delete("1.0", "end")

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()


    def _salvar_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            print("Nenhuma história selecionada")
            return

        nome = self.nome_especie_criacao.get().strip()
        descricao = self.descricao_especie_criacao.get(
            "1.0", "end-1c"
        ).strip()

        if not nome:
            print("Digite o nome da espécie")
            return

        # Impede nomes duplicados na mesma história.
        if any(e["nome"].casefold() == nome.casefold()
            for e in historia.get("especies", [])):
            print("Já existe uma espécie com esse nome")
            return

        especie = criar_especie(historia, nome, descricao)

        if especie is None:
            return

        self.toplevel.withdraw()

        if self.apos_criar:
            self.apos_criar(historia)

        criar_label_especie(
            especie, self.frame_conteudo, self.selecionar_especie
        )

        if self.ao_criar_especie:
            self.ao_criar_especie(especie)


    def _criar_janela_edicao(self):
        self.janela_edicao = ctk.CTkToplevel(self.janela)
        vincular_toplevel(self.janela_edicao, self.janela)
        self.janela_edicao.geometry("500x400")
        self.janela_edicao.title("Editar espécie")
        self.janela_edicao.resizable(False, False)
        self.janela_edicao.protocol(
            "WM_DELETE_WINDOW", self.janela_edicao.withdraw
        )
        self.janela_edicao.withdraw()

        frame = ctk.CTkFrame(self.janela_edicao)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            frame, text="Editar espécie",
            font=("Helvetica", 22, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        ctk.CTkLabel(frame, text="Nome:").grid(
            row=1, column=0, sticky="w"
        )

        self.nome_especie_edicao = ctk.CTkEntry(frame)
        self.nome_especie_edicao.grid(
            row=2, column=0, sticky="ew", pady=(5, 12)
        )

        ctk.CTkLabel(frame, text="Descrição:").grid(
            row=3, column=0, sticky="w"
        )

        self.descricao_especie_edicao = ctk.CTkTextbox(
            frame, height=150
        )
        self.descricao_especie_edicao.grid(
            row=4, column=0, sticky="nsew", pady=5
        )

        ctk.CTkButton(
            frame,
            text="Salvar alterações",
            command=self._salvar_edicao
        ).grid(row=5, column=0, sticky="ew", pady=(15, 0))

    def edicao_especie(self):
        especie = self.especie_selecionada

        if especie is None:
            return

        if self._historia_selecionada() is None:
            return

        self.nome_especie_edicao.delete(0, "end")
        self.nome_especie_edicao.insert(0, especie.get("nome", ""))

        self.descricao_especie_edicao.delete("1.0", "end")
        self.descricao_especie_edicao.insert(
            "1.0", especie.get("descricao", "")
        )

        self.janela_edicao.deiconify()
        self.janela_edicao.lift()
        self.janela_edicao.focus_force()

    def _salvar_edicao(self):
        historia = self._historia_selecionada()
        especie = self.especie_selecionada

        if historia is None or especie is None:
            return

        nome = self.nome_especie_edicao.get()
        descricao = self.descricao_especie_edicao.get(
            "1.0", "end-1c"
        )

        if atualizar_especie(historia, especie, nome, descricao):
            self.janela_edicao.withdraw()

            if self.apos_criar:
                self.apos_criar(historia)
            else:
                self.selecionar_especie(especie)