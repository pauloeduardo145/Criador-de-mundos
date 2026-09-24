import customtkinter as ctk
from widgets import mostrar_imagem, mostrar_frame, ocultar_frame, criar_personagem, criar_label_personagem
from entry_textbox import configurar_entry, configurar_textbox
from tkinter import filedialog, messagebox
import os
import shutil
import storage
import uuid
import historias


class Personagem:
    def __init__(self, janela, frame_conteudo, mostrar_no_conteudo, mostrar_cards_com_imagem,
                 obter_historia_selecionada=None, apos_criar=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo
        self.mostrar_no_conteudo = mostrar_no_conteudo
        self.mostrar_cards_com_imagem = mostrar_cards_com_imagem

        self.obter_historia_selecionada = obter_historia_selecionada
        self.apos_criar = apos_criar

        self.personagem_selecionado = None
        self.caminho_imagem = None

        # Estado da janela de criação (formulário "Criar Personagem")
        self.caminho_imagem_criacao = None
        self.galeria_imagens_criacao = None

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

    def _validar_imagem_personagem(self, personagem):
        alterou = False

        caminho_imagem = personagem.get("imagens")

        if caminho_imagem and not os.path.exists(caminho_imagem):
            print(f"Imagem não encontrada, removendo referência: {caminho_imagem}")
            personagem["imagens"] = None
            alterou = True

        galeria = personagem.get("galeria")

        if galeria:
            galeria_valida = []

            for item in galeria:
                caminho = item.get("caminho") if isinstance(item, dict) else item

                if caminho and not os.path.exists(caminho):
                    print(f"Imagem da galeria não encontrada, removendo referência: {caminho}")
                    alterou = True
                    continue

                galeria_valida.append(item)

            personagem["galeria"] = galeria_valida

        if alterou:
            historias.atualizar()

        return alterou

    def selecionar_personagem(self, personagem):
        self.personagem_selecionado = personagem

        self._validar_imagem_personagem(personagem)

        self.limpar_frame_conteudo()

        linha = 0

        # A coluna 1 se estica para o botão Editar ficar na borda direita
        self.frame_conteudo.grid_columnconfigure(1, weight=1)

        # Cabeçalho: título à esquerda e botão Editar à direita
        cabecalho = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 5))
        cabecalho.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cabecalho,
            text=f"👤 {personagem['nome']}",
            font=("Helvetica", 22, "bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            cabecalho,
            text="✏️ Editar",
            width=90,
            command=lambda: self.edicao_personagem()
        ).grid(row=0, column=1, sticky="e")

        frame_imagem = ctk.CTkFrame(self.frame_conteudo)
        frame_imagem.grid(row=1, column=0, sticky="n", padx=20)

        frame_info = ctk.CTkFrame(self.frame_conteudo, width=600)
        frame_info.grid_columnconfigure(1, weight=1)
        frame_info.grid(row=1, column=1, sticky="nsew", padx=20)

        if personagem.get("imagens"):
            img = mostrar_imagem(personagem["imagens"], 500)

            foto = ctk.CTkLabel(frame_imagem, image=img, text="")
            foto.image = img
            foto.grid()

        labels_valor = []

        for chave, valor in personagem.items():

            if chave in ["imagens", "galeria", "id", "historia_id", "nome"]:
                continue

            ctk.CTkLabel(
                frame_info, text=f"{chave}:", font=("Arial", 16, "bold")
            ).grid(row=linha, column=0, sticky="nsew", pady=(5, 15))

            valor_label = ctk.CTkLabel(
                frame_info, text=str(valor), anchor="w", wraplength=560, justify="left"
            )
            valor_label.grid(row=linha, column=1, sticky="ew", padx=10, pady=(10, 30))
            labels_valor.append(valor_label)

            linha += 1

        def _atualizar_wraplength(evento, labels=labels_valor):
            largura_disponivel = max(evento.width - 130, 100)
            for rotulo in labels:
                rotulo.configure(wraplength=largura_disponivel)

        frame_info.bind("<Configure>", _atualizar_wraplength)

    # ---------- Edição ----------

    def edicao_personagem(self, *args):
        personagem = self.personagem_selecionado

        if personagem is None:
            print("Nenhum personagem selecionado")
            return

        if self._historia_selecionada() is None:
            print("Nenhuma história selecionada")
            return

        if "galeria" not in personagem:
            personagem["galeria"] = []

        self._validar_imagem_personagem(personagem)

        self.personagem_em_edicao = personagem
        self.caminho_imagem = None  # nova imagem principal ainda não escolhida

        self.nome_edicao.delete(0, "end")
        self.nome_edicao.insert(0, personagem["nome"])

        for chave, caixa in self.campos_edicao.items():
            caixa.delete("1.0", "end")
            caixa.insert("1.0", personagem.get(chave, ""))

        self._mostrar_preview_edicao(personagem.get("imagens"))
        self._atualizar_galeria_edicao()

        self.toplevel_edicao.deiconify()
        self.toplevel_edicao.lift()
        self.toplevel_edicao.focus_force()
        self.nome_edicao.focus()

    # -- imagem principal --

    def _mostrar_preview_edicao(self, caminho):
        for widget in self.frame_preview_edicao.winfo_children():
            widget.destroy()

        preview = ctk.CTkLabel(self.frame_preview_edicao, text="[Clique para alterar imagem]")
        preview.pack()

        if caminho:
            try:
                img = mostrar_imagem(caminho, 250)
                preview.configure(image=img, text="")
                preview.image = img
            except Exception as erro:
                print(erro)

        preview.bind("<Button-1>", lambda e: self._trocar_imagem_edicao())

    def _trocar_imagem_edicao(self):
        novo_caminho = filedialog.askopenfilename(
            parent=self.toplevel_edicao,
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),
                       ("Todos os arquivos", "*.*")]
        )

        if not novo_caminho:
            return

        self.caminho_imagem = novo_caminho

        self._mostrar_preview_edicao(self.caminho_imagem)

    # -- galeria --

    def _atualizar_galeria_edicao(self):
        for widget in self.frame_galeria_edicao.winfo_children():
            widget.destroy()

        personagem = self.personagem_em_edicao

        if personagem is None:
            return

        for indice, item in enumerate(personagem.get("galeria", [])):

            caminho = item.get("caminho")
            descricao = item.get("descricao", "")

            try:
                img = mostrar_imagem(caminho, 100)

                card = ctk.CTkFrame(self.frame_galeria_edicao)
                card.grid(row=indice // 4, column=indice % 4, padx=5, pady=5)

                label = ctk.CTkLabel(card, image=img, text="")
                label.image = img
                label.pack()

                ctk.CTkLabel(card, text=descricao, wraplength=100).pack()

                ctk.CTkButton(
                    card, text="Remover", width=80,
                    command=lambda i=item: self._remover_da_galeria_edicao(i)
                ).pack(pady=2)

            except Exception as erro:
                print(erro)

    def _adicionar_na_galeria_edicao(self):
        personagem = self.personagem_em_edicao

        if personagem is None:
            return

        caminho = filedialog.askopenfilename(
            parent=self.toplevel_edicao,
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),
                       ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        janela_desc = ctk.CTkInputDialog(
            text="Digite a descrição da imagem:", title="Descrição da Galeria"
        )
        descricao = janela_desc.get_input()

        if descricao is None:
            descricao = ""

        if "galeria" not in personagem:
            personagem["galeria"] = []

        extensao = os.path.splitext(caminho)[1]
        nome_arquivo = f"{uuid.uuid4()}{extensao}"
        novo_caminho = os.path.join(storage.PASTA_GALERIA, nome_arquivo)

        shutil.copy2(caminho, novo_caminho)

        personagem["galeria"].append(
            {"caminho": novo_caminho, "descricao": descricao}
        )

        historias.atualizar()

        self._atualizar_galeria_edicao()

    def _remover_da_galeria_edicao(self, item):
        personagem = self.personagem_em_edicao

        if personagem is None:
            return

        confirmar = messagebox.askyesno(
            "Remover imagem", "Deseja remover esta imagem da galeria?",
            parent=self.toplevel_edicao
        )

        if not confirmar:
            return

        caminho = item.get("caminho")

        personagem["galeria"].remove(item)

        if caminho and os.path.exists(caminho):
            try:
                os.remove(caminho)
            except Exception as erro:
                print(f"Erro ao apagar arquivo: {erro}")

        historias.atualizar()
        self._atualizar_galeria_edicao()

    # -- salvar --

    def _salvar_edicao(self):
        historia = self._historia_selecionada()
        personagem = self.personagem_em_edicao

        if historia is None or personagem is None:
            return

        nome = self.nome_edicao.get().strip()

        if not nome:
            messagebox.showwarning(
                "Editar personagem", "Digite um nome para o personagem.",
                parent=self.toplevel_edicao
            )
            return

        if nome != personagem["nome"] and any(
            p["nome"] == nome for p in historia["personagens"]
        ):
            messagebox.showwarning(
                "Editar personagem", "Já existe um personagem com esse nome.",
                parent=self.toplevel_edicao
            )
            return

        personagem["nome"] = nome

        for chave, caixa in self.campos_edicao.items():
            personagem[chave] = caixa.get("1.0", "end-1c")

        if self.caminho_imagem:
            imagem_antiga = personagem.get("imagens")

            extensao = os.path.splitext(self.caminho_imagem)[1]
            novo_caminho = os.path.join(
                storage.PASTA_IMAGENS,
                f"{personagem['id']}{extensao}"
            )

            caminhos_iguais = (
                imagem_antiga
                and os.path.abspath(imagem_antiga) == os.path.abspath(novo_caminho)
            )

            shutil.copy2(self.caminho_imagem, novo_caminho)

            if imagem_antiga and not caminhos_iguais:
                nome_arquivo = os.path.basename(imagem_antiga)

                if nome_arquivo.startswith(personagem["id"]):
                    if os.path.exists(imagem_antiga):
                        try:
                            os.remove(imagem_antiga)
                        except Exception as erro:
                            print(erro)

            personagem["imagens"] = novo_caminho

        historias.atualizar()

        self.caminho_imagem = None

        self.toplevel_edicao.withdraw()

        self.selecionar_personagem(personagem)

    # -- janela --

    def _criar_janela_edicao(self):
        self.personagem_em_edicao = None

        self.toplevel_edicao = ctk.CTkToplevel(self.janela)
        self.toplevel_edicao.geometry("760x760")
        self.toplevel_edicao.title("Editar personagem")
        self.toplevel_edicao.resizable(False, False)
        self.toplevel_edicao.protocol("WM_DELETE_WINDOW", self.toplevel_edicao.withdraw)

        self.toplevel_edicao.withdraw()

        self.toplevel_edicao.grid_columnconfigure(0, weight=1)
        self.toplevel_edicao.grid_rowconfigure(0, weight=1)

        # Corpo rolável (são muitos campos) + rodapé fixo com os botões
        corpo = ctk.CTkScrollableFrame(self.toplevel_edicao)
        corpo.grid(row=0, column=0, sticky="nsew")

        rodape = ctk.CTkFrame(self.toplevel_edicao)
        rodape.grid(row=1, column=0, sticky="ew")
        rodape.grid_columnconfigure(0, weight=1)
        rodape.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(corpo, text="Editar Personagem", font=("Helvetica", 18, "bold")).pack(
            pady=10
        )

        ctk.CTkLabel(corpo, text="Nome:").pack(anchor="w", padx=10)

        self.nome_edicao = ctk.CTkEntry(corpo, placeholder_text="Nome do personagem")
        self.nome_edicao.pack(fill="x", padx=10, pady=5)
        configurar_entry(self.nome_edicao)

        campos = [
            ("personalidade", "Personalidade:"),
            ("aparencia", "Aparência:"),
            ("historia", "História:"),
            ("relacoes", "Relações:"),
            ("poderes", "Poderes:"),
            ("fraquezas", "Fraquezas:"),
            ("habilidades", "Habilidades:"),
        ]

        self.campos_edicao = {}

        for chave, rotulo in campos:
            ctk.CTkLabel(corpo, text=rotulo).pack(anchor="w", padx=10, pady=(10, 0))

            caixa = ctk.CTkTextbox(corpo, height=80)
            caixa.pack(fill="x", padx=10, pady=5)
            configurar_textbox(caixa)

            self.campos_edicao[chave] = caixa

        # Imagem principal (o label é recriado a cada abertura)
        self.frame_preview_edicao = ctk.CTkFrame(corpo, fg_color="transparent")
        self.frame_preview_edicao.pack(pady=10)

        # Galeria
        ctk.CTkLabel(corpo, text="Galeria do personagem").pack(pady=(15, 5))

        self.frame_galeria_edicao = ctk.CTkFrame(corpo)
        self.frame_galeria_edicao.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            corpo, text="Adicionar imagem à galeria",
            command=lambda: self._adicionar_na_galeria_edicao()
        ).pack(pady=5)

        ctk.CTkButton(
            rodape, text="Fechar",
            command=lambda: self.toplevel_edicao.withdraw()
        ).grid(row=0, column=0, padx=5, pady=10)

        ctk.CTkButton(
            rodape, text="Salvar",
            command=lambda: self._salvar_edicao()
        ).grid(row=0, column=1, padx=5, pady=10)

    def abrir_galeria_personagem(self, personagem):
        self._validar_imagem_personagem(personagem)

        self.limpar_frame_conteudo()

        if personagem.get("imagens"):
            img_ctk = mostrar_imagem(personagem["imagens"], 250)

            label = ctk.CTkLabel(self.frame_conteudo, image=img_ctk, text="")
            label.image = img_ctk
            label.pack(pady=10)

        titulo = ctk.CTkLabel(
            self.frame_conteudo, text="Galeria:", font=("Helvetica", 16, "bold")
        )
        titulo.pack(pady=10)

        for item in personagem.get("galeria", []):

            if isinstance(item, dict):
                caminho = item.get("caminho") or item.get("imagem")
                descricao = item.get("descricao", "")
            else:
                caminho = item
                descricao = ""

            try:
                img_ctk = mostrar_imagem(caminho, 200)

                frame = ctk.CTkFrame(self.frame_conteudo)
                frame.pack(pady=10)

                img_label = ctk.CTkLabel(frame, image=img_ctk, text="")
                img_label.image = img_ctk
                img_label.pack()

                desc = ctk.CTkLabel(frame, text=descricao, wraplength=400)
                desc.pack()

            except Exception as erro:
                print(f"Erro ao abrir imagem da galeria: {erro}")

    # ---------- Listagens (usadas pela navegação principal) ----------

    def _aviso_sem_historia(self):
        self.limpar_frame_conteudo()

        ctk.CTkLabel(
            self.frame_conteudo,
            text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
            font=("Helvetica", 18),
            justify="center"
        ).pack(expand=True)

    def mostrar_todos(self, event=None):
        historia = self._historia_selecionada()

        if historia is None:
            self._aviso_sem_historia()
            return

        personagens = historia.get("personagens", [])

        self.limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_conteudo,
            text=f"📂 Todos os Personagens ({len(personagens)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        self.mostrar_no_conteudo(self.frame_conteudo, personagens, self.selecionar_personagem, "nome", 6, 6)

    def mostrar_todas_imagens(self, event=None):
        historia = self._historia_selecionada()

        if historia is None:
            self._aviso_sem_historia()
            return

        self.limpar_frame_conteudo()

        personagens_com_imagem = [
            p for p in historia["personagens"]
            if p.get("imagens")
        ]

        titulo = ctk.CTkLabel(
            self.frame_conteudo,
            text=f"🖼️ Todas as Imagens ({len(personagens_com_imagem)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        self.mostrar_cards_com_imagem(self.frame_conteudo, personagens_com_imagem, self.selecionar_personagem)

    def mostrar_todas_imagens_da_galeria(self, event=None):
        historia = self._historia_selecionada()

        if historia is None:
            self._aviso_sem_historia()
            return

        self.limpar_frame_conteudo()

        personagens = [
            p for p in historia["personagens"]
            if len(p.get("galeria", [])) > 0
        ]

        titulo = ctk.CTkLabel(
            self.frame_conteudo,
            text=f"Personagens com Galeria ({len(personagens)})",
            font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10)

        for personagem in personagens:
            btn = ctk.CTkButton(
                self.frame_conteudo, text=personagem["nome"],
                command=lambda p=personagem: self.abrir_galeria_personagem(p)
            )
            btn.pack(pady=5)

    # ---------- Exclusão ----------

    def excluir(self, nome):
        historia = self._historia_selecionada()

        if historia is None:
            return

        personagem = next(
            (p for p in historia["personagens"] if p["nome"] == nome),
            None
        )

        if personagem is None:
            return

        if not messagebox.askyesno(
            "Excluir", f'Deseja realmente excluir o personagem "{nome}"?'
        ):
            return

        historia["personagens"].remove(personagem)

        historias.atualizar()

        if self.apos_criar:
            self.apos_criar(historia)

    # ---------- Janela "Criar Personagem" ----------

    def abrir_criacao(self):
        if self._historia_selecionada() is None:
            print("Selecione a historia primeiro")
            return

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    def _escolher_imagem_principal(self):
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"), ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        self.caminho_imagem_criacao = caminho

        img_ctk = mostrar_imagem(caminho, 250)
        self.preview_criacao.configure(image=img_ctk, text="")
        self.preview_criacao.image = img_ctk

    def _adicionar_imagem_galeria_criacao(self):
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"), ("Todos os arquivos", "*.*")]
        )

        if not caminho:
            return

        janela_desc = ctk.CTkInputDialog(text="Digite a descrição da imagem:", title="Descrição da Galeria")
        descricao = janela_desc.get_input()

        if descricao is None:
            descricao = ""

        extensao = os.path.splitext(caminho)[1]
        nome_arquivo = f"{uuid.uuid4()}{extensao}"
        novo_caminho = os.path.join(storage.PASTA_GALERIA, nome_arquivo)

        shutil.copy2(caminho, novo_caminho)

        if self.galeria_imagens_criacao is None:
            self.galeria_imagens_criacao = []

        self.galeria_imagens_criacao.append({"caminho": novo_caminho, "descricao": descricao})

    def _salvar_criacao(self):
        historia = self._historia_selecionada()

        if historia is None:
            print("Nenhuma história selecionada")
            return

        novo = criar_personagem(
            historia,
            self.personame_criacao.get(),
            self.caminho_imagem_criacao,
            self.personalidade_criacao.get("1.0", "end-1c"),
            self.aparencia_criacao.get("1.0", "end-1c"),
            self.relacoes_criacao.get("1.0", "end-1c"),
            self.historia_criacao.get("1.0", "end-1c"),
            self.poderes_criacao.get("1.0", "end-1c"),
            self.fraquezas_criacao.get("1.0", "end-1c"),
            self.habilidades_criacao.get("1.0", "end-1c")
        )

        if self.galeria_imagens_criacao is not None:
            novo["galeria"] = self.galeria_imagens_criacao.copy()
        else:
            novo["galeria"] = []

        if self.caminho_imagem_criacao:
            extensao = os.path.splitext(self.caminho_imagem_criacao)[1]
            novo_caminho = os.path.join(storage.PASTA_IMAGENS, f"{novo['id']}{extensao}")
            shutil.copy2(self.caminho_imagem_criacao, novo_caminho)
            novo["imagens"] = novo_caminho

        if novo:
            criar_label_personagem(novo, self.frame_conteudo, self.selecionar_personagem)

            if self.apos_criar:
                self.apos_criar(historia)

            self.caminho_imagem_criacao = None
            self.galeria_imagens_criacao = None

        self.toplevel.withdraw()

    def _criar_janela_criacao(self):
        self.toplevel = ctk.CTkToplevel(self.janela)
        self.toplevel.geometry("1000x590")
        self.toplevel.title("Criar personagem")
        self.toplevel.resizable(False, False)
        self.toplevel.protocol("WM_DELETE_WINDOW",self.toplevel.withdraw)

        self.toplevel.withdraw()

        self.janela_criacao = ctk.CTkFrame(self.toplevel, width=1000, height=590)
        self.janela_criacao.pack(fill="both", expand=True)
        self.janela_criacao.grid_propagate(False)
        self.janela_criacao.grid_columnconfigure(0, weight=1)
        self.janela_criacao.grid_columnconfigure(1, weight=0)
        self.janela_criacao.grid_columnconfigure(2, weight=1)
        self.janela_criacao.grid_rowconfigure(0, weight=1)
        self.janela_criacao.grid_rowconfigure(1, weight=1)
        self.janela_criacao.grid_rowconfigure(2, weight=1)
        self.janela_criacao.grid_rowconfigure(3, weight=0)
        self.janela_criacao.grid_rowconfigure(4, weight=0)
        self.janela_criacao.grid_rowconfigure(5, weight=1)
        self.janela_criacao.grid_rowconfigure(6, weight=1)

        def enter_personagem(event):
            self._salvar_criacao()

        self.preview_criacao = ctk.CTkLabel(self.janela_criacao, text="[Clique para importar imagem principal]")
        self.preview_criacao.grid(column=0, row=3, rowspan=3)
        self.preview_criacao.bind("<Button-1>", lambda e: self._escolher_imagem_principal())

        ctk.CTkLabel(self.janela_criacao, text="Nome: ").grid(column=1, row=0)

        self.personame_criacao = ctk.CTkEntry(self.janela_criacao, placeholder_text="Insira o nome do personagem")
        self.personame_criacao.bind("<Return>", enter_personagem)
        self.personame_criacao.grid(column=2, row=0, sticky="we")
        configurar_entry(self.personame_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Personalidade: ").grid(column=1, row=1)
        self.personalidade_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.personalidade_criacao.grid(column=2, row=1, sticky="we")
        configurar_textbox(self.personalidade_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Aparencia: ").grid(column=1, row=2)
        self.aparencia_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.aparencia_criacao.grid(column=2, row=2, sticky="we")
        configurar_textbox(self.aparencia_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Relações").grid(column=1, row=3)
        self.relacoes_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.relacoes_criacao.grid(column=2, row=3, sticky="we")
        configurar_textbox(self.relacoes_criacao)

        ctk.CTkLabel(
            self.janela_criacao,
            text="Separe com ';', Ex: Esposa de X; Amiga de X",
            font=("Helvetica", 11)
        ).grid(column=2, row=4, sticky="w")

        ctk.CTkLabel(self.janela_criacao, text="Historia do personagem").grid(column=1, row=5)
        self.historia_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.historia_criacao.grid(column=2, row=5, sticky="we")
        configurar_textbox(self.historia_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Poderes:").grid(column=1, row=6)
        self.poderes_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.poderes_criacao.grid(column=2, row=6, sticky="we")
        configurar_textbox(self.poderes_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Fraquezas:").grid(column=1, row=7)
        self.fraquezas_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.fraquezas_criacao.grid(column=2, row=7, sticky="we")
        configurar_textbox(self.fraquezas_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Habilidades do personagem").grid(column=1, row=8)
        self.habilidades_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.habilidades_criacao.grid(column=2, row=8, sticky="we")
        configurar_textbox(self.habilidades_criacao)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: self.toplevel.withdraw()
        ).grid(column=1, row=9, sticky="se", pady=10, padx=10)

        ctk.CTkButton(
            self.janela_criacao, text="[Salvar Personagem]",
            command=lambda: self._salvar_criacao()
        ).grid(column=2, row=9, sticky="se", pady=10, padx=10)