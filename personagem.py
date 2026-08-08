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

        frame_imagem = ctk.CTkFrame(self.frame_conteudo)
        frame_imagem.grid(row=0, column=0, sticky="n", padx=20)

        frame_info = ctk.CTkFrame(self.frame_conteudo, width=600)
        frame_info.grid_columnconfigure(1, weight=1)
        frame_info.grid(row=0, column=1, sticky="nsew", padx=20)

        if personagem.get("imagens"):
            img = mostrar_imagem(personagem["imagens"], 500)

            foto = ctk.CTkLabel(frame_imagem, image=img, text="")
            foto.image = img
            foto.grid()

        labels_valor = []

        for chave, valor in personagem.items():

            if chave in ["imagens", "galeria", "id", "historia_id"]:
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

        edit = ctk.CTkButton(
            self.frame_conteudo, text="Editar",
            command=lambda *args: self.edicao_personagem(*args)
        )
        edit.grid(row=1, column=0, columnspan=2, pady=10)

    def edicao_personagem(self, *args):
        if self.personagem_selecionado is None:
            print("Nenhum personagem selecionado")
            return

        if "galeria" not in self.personagem_selecionado:
            self.personagem_selecionado["galeria"] = []

        if self._historia_selecionada() is None:
            print("Nenhuma história selecionada")
            return

        self._validar_imagem_personagem(self.personagem_selecionado)

        self.limpar_frame_conteudo()

        titulo = ctk.CTkLabel(
            self.frame_conteudo, text="Modo Edição", font=("Helvetica", 18, "bold")
        )
        titulo.pack(pady=10, anchor="w", padx=20)

        nome = ctk.CTkEntry(self.frame_conteudo)
        nome.insert(0, self.personagem_selecionado["nome"])
        nome.pack(fill="x", padx=10, pady=5)
        configurar_entry(nome)

        ctk.CTkLabel(self.frame_conteudo, text="Personalidade:").pack(padx=10, pady=5)
        personalidade = ctk.CTkTextbox(
            self.frame_conteudo, height=50, fg_color="#1E1E1E",
            text_color="white", border_color="gray"
        )
        personalidade.pack(fill="x", pady=10, padx=5)
        personalidade.insert("1.0", self.personagem_selecionado["personalidade"])
        configurar_textbox(personalidade)

        ctk.CTkLabel(self.frame_conteudo, text="Aparencia:").pack(padx=10, pady=5)
        aparencia = ctk.CTkTextbox(self.frame_conteudo, height=50)
        aparencia.pack(fill="x", pady=10, padx=5)
        aparencia.insert("1.0", self.personagem_selecionado["aparencia"])
        configurar_textbox(aparencia)

        ctk.CTkLabel(self.frame_conteudo, text="Historia:").pack(padx=10, pady=5)
        hispers = ctk.CTkTextbox(self.frame_conteudo, height=50)
        hispers.pack(fill="x", pady=10, padx=5)
        hispers.insert("1.0", self.personagem_selecionado["historia"])
        configurar_textbox(hispers)

        ctk.CTkLabel(self.frame_conteudo, text="Relações:").pack(padx=10, pady=5)
        relacoes = ctk.CTkTextbox(self.frame_conteudo, height=50)
        relacoes.pack(fill="x", pady=10, padx=5)
        relacoes.insert("1.0", self.personagem_selecionado["relacoes"])
        configurar_textbox(relacoes)

        ctk.CTkLabel(self.frame_conteudo, text="Poderes:").pack(padx=10, pady=5)
        poderes = ctk.CTkTextbox(self.frame_conteudo, height=50)
        poderes.pack(fill="x", pady=10, padx=5)
        poderes.insert("1.0", self.personagem_selecionado["poderes"])
        configurar_textbox(poderes)

        ctk.CTkLabel(self.frame_conteudo, text="Fraquezas:").pack(padx=10, pady=5)
        fraqueza = ctk.CTkTextbox(self.frame_conteudo, height=50)
        fraqueza.pack(fill="x", pady=10, padx=5)
        fraqueza.insert("1.0", self.personagem_selecionado["fraquezas"])
        configurar_textbox(fraqueza)

        ctk.CTkLabel(self.frame_conteudo, text="Habilidades:").pack(padx=10, pady=5)
        hapers = ctk.CTkTextbox(self.frame_conteudo, height=50)
        hapers.pack(fill="x", pady=10, padx=5)
        hapers.insert("1.0", self.personagem_selecionado["habilidades"])
        configurar_textbox(hapers)

        # IMAGEM PRINCIPAL

        preview = ctk.CTkLabel(self.frame_conteudo, text="[Clique para alterar imagem]")
        preview.pack(pady=10)

        if self.personagem_selecionado.get("imagens"):
            img = mostrar_imagem(self.personagem_selecionado["imagens"], 250)
            preview.configure(image=img, text="")
            preview.image = img

        def trocar_imagem():
            novo_caminho = filedialog.askopenfilename(
                title="Selecione uma imagem",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"),
                           ("Todos os arquivos", "*.*")]
            )

            if not novo_caminho:
                return

            self.caminho_imagem = novo_caminho

            img = mostrar_imagem(self.caminho_imagem, 250)
            preview.configure(image=img, text="")
            preview.image = img

        preview.bind("<Button-1>", lambda e: trocar_imagem())

        # GALERIA

        ctk.CTkLabel(self.frame_conteudo, text="Galeria do personagem").pack(pady=(15, 5))

        frame_galeria = ctk.CTkFrame(self.frame_conteudo)
        frame_galeria.pack(fill="x", padx=10, pady=5)

        def atualizar_galeria():
            for widget in frame_galeria.winfo_children():
                widget.destroy()

            for indice, item in enumerate(self.personagem_selecionado.get("galeria", [])):

                caminho = item.get("caminho")
                descricao = item.get("descricao", "")

                try:
                    img = mostrar_imagem(caminho, 100)

                    card = ctk.CTkFrame(frame_galeria)
                    card.grid(row=indice // 4, column=indice % 4, padx=5, pady=5)

                    label = ctk.CTkLabel(card, image=img, text="")
                    label.image = img
                    label.pack()

                    ctk.CTkLabel(card, text=descricao, wraplength=100).pack()

                    ctk.CTkButton(
                        card, text="Remover", width=80,
                        command=lambda i=item: remover_da_galeria(i)
                    ).pack(pady=2)

                except Exception as erro:
                    print(erro)

        def adicionar_na_galeria():
            caminho = filedialog.askopenfilename(
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

            if "galeria" not in self.personagem_selecionado:
                self.personagem_selecionado["galeria"] = []

            extensao = os.path.splitext(caminho)[1]
            nome_arquivo = f"{uuid.uuid4()}{extensao}"
            novo_caminho = os.path.join(storage.PASTA_GALERIA, nome_arquivo)

            shutil.copy2(caminho, novo_caminho)

            self.personagem_selecionado["galeria"].append(
                {"caminho": novo_caminho, "descricao": descricao}
            )

            atualizar_galeria()

        def remover_da_galeria(item):
            confirmar = messagebox.askyesno(
                "Remover imagem", "Deseja remover esta imagem da galeria?"
            )

            if not confirmar:
                return

            caminho = item.get("caminho")

            self.personagem_selecionado["galeria"].remove(item)

            if caminho and os.path.exists(caminho):
                try:
                    os.remove(caminho)
                    historias.atualizar()
                except Exception as erro:
                    print(f"Erro ao apagar arquivo: {erro}")

            historias.atualizar()
            atualizar_galeria()

        atualizar_galeria()

        ctk.CTkButton(
            self.frame_conteudo, text="Adicionar imagem à galeria",
            command=lambda: adicionar_na_galeria()
        ).pack(pady=5)

        # SALVAR / CANCELAR

        def salvar_edicao():
            self.personagem_selecionado["nome"] = nome.get()
            self.personagem_selecionado["personalidade"] = personalidade.get("1.0", "end-1c")
            self.personagem_selecionado["aparencia"] = aparencia.get("1.0", "end-1c")
            self.personagem_selecionado["historia"] = hispers.get("1.0", "end-1c")
            self.personagem_selecionado["relacoes"] = relacoes.get("1.0", "end-1c")
            self.personagem_selecionado["poderes"] = poderes.get("1.0", "end-1c")
            self.personagem_selecionado["fraquezas"] = fraqueza.get("1.0", "end-1c")
            self.personagem_selecionado["habilidades"] = hapers.get("1.0", "end-1c")

            if self.caminho_imagem:
                imagem_antiga = self.personagem_selecionado.get("imagens")

                extensao = os.path.splitext(self.caminho_imagem)[1]
                novo_caminho = os.path.join(
                    storage.PASTA_IMAGENS,
                    f"{self.personagem_selecionado['id']}{extensao}"
                )

                caminhos_iguais = (
                    imagem_antiga
                    and os.path.abspath(imagem_antiga) == os.path.abspath(novo_caminho)
                )

                shutil.copy2(self.caminho_imagem, novo_caminho)

                if imagem_antiga and not caminhos_iguais:
                    nome_arquivo = os.path.basename(imagem_antiga)

                    if nome_arquivo.startswith(self.personagem_selecionado["id"]):
                        if os.path.exists(imagem_antiga):
                            try:
                                os.remove(imagem_antiga)
                            except Exception as erro:
                                print(erro)

                self.personagem_selecionado["imagens"] = novo_caminho

            historias.atualizar()

            self.caminho_imagem = None

            self.selecionar_personagem(self.personagem_selecionado)

        def fechar_sem_salvar():
            confirmar = messagebox.askyesno(
                "Cancelar edição", "Deseja sair sem salvar as alterações?"
            )

            if confirmar:
                self.selecionar_personagem(self.personagem_selecionado)

        botao_salvar = ctk.CTkButton(
            self.frame_conteudo, text="Salvar", command=lambda: salvar_edicao()
        )
        botao_salvar.pack(pady=10)

        botao_fechar = ctk.CTkButton(
            self.frame_conteudo, text="Fechar sem salvar", command=fechar_sem_salvar
        )
        botao_fechar.pack(pady=10)

        self.arearolavel()

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

        mostrar_frame(self.janela_criacao)
        self.janela_criacao.focus()

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

            ocultar_frame(self.janela_criacao)

            self.caminho_imagem_criacao = None
            self.galeria_imagens_criacao = None

    def _criar_janela_criacao(self):
        self.janela_criacao = ctk.CTkFrame(self.janela, width=600, height=500)
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

        self.janela_criacao.place(relx=0.5, rely=0.5, anchor="center")
        self.janela_criacao.place_forget()

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
            command=lambda: ocultar_frame(self.janela_criacao)
        ).grid(column=1, row=9, sticky="se", pady=10, padx=10)

        ctk.CTkButton(
            self.janela_criacao, text="[Salvar Personagem]",
            command=lambda: self._salvar_criacao()
        ).grid(column=2, row=9, sticky="se", pady=10, padx=10)