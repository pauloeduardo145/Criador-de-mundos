import customtkinter as ctk
from widgets import mostrar_imagem, mostrar_frame, ocultar_frame, criar_personagem, criar_label_personagem, vincular_toplevel
from entry_textbox import configurar_entry, configurar_textbox
from tkinter import messagebox
from seletores import escolher_arquivo
import os
import shutil
import storage
import uuid
import historias

ESPECIE_PADRAO = "Selecionar espécie"
SISTEMA_PADRAO = "Selecionar sistema de poder"


class Personagem:
    def __init__(self, janela, frame_conteudo, mostrar_no_conteudo, mostrar_cards_com_imagem,
                 obter_historia_selecionada=None, apos_criar=None, abrir_criacao_especie=None,
                 abrir_criacao_sistema_poder=None):

        self.janela = janela
        self.abrir_criacao_especie = abrir_criacao_especie
        self.abrir_criacao_sistema_poder = abrir_criacao_sistema_poder
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

    def _nome_especie(self, id_especie):
        historia = self._historia_selecionada()

        if historia is None or not id_especie:
            return "—"

        return next(
            (e["nome"] for e in historia.get("especies", []) if e["id"] == id_especie),
            "—"
        )

    def _nomes_especies(self):
        historia = self._historia_selecionada()
        especies = historia.get("especies", []) if historia else []
        return [e["nome"] for e in especies]

    def _preencher_menu_especie(self, menu, selecionada=None):
        nomes = self._nomes_especies()
        menu.configure(values=[ESPECIE_PADRAO] + nomes)
        menu.set(selecionada if selecionada in nomes else ESPECIE_PADRAO)

    def _carregar_especies_edicao(self, id_especie_atual):
        historia = self._historia_selecionada()
        especies = historia.get("especies", []) if historia else []

        atual = next((e["nome"] for e in especies if e["id"] == id_especie_atual), None)
        self._preencher_menu_especie(self.especie_edicao, atual)

    def _ao_escolher_especie(self, menu, valor):
        if valor != ESPECIE_PADRAO:
            menu._ultima_escolha = valor
            return

        if self.abrir_criacao_especie:
            self.abrir_criacao_especie()

        menu.set(getattr(menu, "_ultima_escolha", ESPECIE_PADRAO))

    def atualizar_especies(self, nova_especie=None):
        nome_novo = nova_especie["nome"] if nova_especie else None

        for menu, janela in (
            (self.especie_criacao, self.toplevel),
            (self.especie_edicao, self.toplevel_edicao),
        ):
            atual = menu.get()
            alvo = nome_novo if nome_novo and janela.winfo_viewable() else atual
            self._preencher_menu_especie(menu, alvo)
            menu._ultima_escolha = menu.get()

    def _sistemas_poder(self):
        historia = self._historia_selecionada()
        return historia.get("sistemas_poder", []) if historia else []

    def _nome_sistema(self, id_sistema):
        return next(
            (s["nome"] for s in self._sistemas_poder() if s["id"] == id_sistema),
            "—"
        )

    def _preencher_menu_sistema(self, menu, selecionado=None):
        nomes = [s["nome"] for s in self._sistemas_poder()]
        menu.configure(values=[SISTEMA_PADRAO] + nomes)
        menu.set(selecionado if selecionado in nomes else SISTEMA_PADRAO)
        menu._ultima_escolha = menu.get()

    def _ao_escolher_sistema(self, menu, valor):
        if valor != SISTEMA_PADRAO:
            menu._ultima_escolha = valor
            return

        if self.abrir_criacao_sistema_poder:
            self.abrir_criacao_sistema_poder()

        menu.set(getattr(menu, "_ultima_escolha", SISTEMA_PADRAO))

    def atualizar_sistemas(self, novo_sistema=None):
        nome_novo = novo_sistema["nome"] if novo_sistema else None

        for menu, janela in (
            (self.sistema_criacao, self.toplevel),
            (self.sistema_edicao, self.toplevel_edicao),
        ):
            alvo = nome_novo if nome_novo and janela.winfo_viewable() else menu.get()
            self._preencher_menu_sistema(menu, alvo)

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

        linha_idade_especie = ctk.CTkFrame(cabecalho, fg_color="transparent")
        linha_idade_especie.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        idade_texto = str(personagem.get("idade", "")).strip() or "—"

        ctk.CTkLabel(
            linha_idade_especie,
            text=f"Idade: {idade_texto}",
            font=("Arial", 16)
        ).grid(row=0, column=0, sticky="w", padx=(0, 30))

        ctk.CTkLabel(
            linha_idade_especie,
            text=f"Espécie: {self._nome_especie(personagem.get('especie'))}",
            font=("Arial", 16)
        ).grid(row=0, column=1, sticky="w")

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

            if chave in ["imagens", "galeria", "id", "historia_id", "nome", "idade", "especie", "nome_poder"]:
                continue

            rotulo_chave = chave

            if chave == "sistema_poder":
                rotulo_chave = "sistema de poder"
                valor = self._nome_sistema(valor)
                nome_poder = (personagem.get("nome_poder") or "").strip()
                if nome_poder:
                    valor = f"{valor} {nome_poder}" if valor != "—" else nome_poder

            ctk.CTkLabel(
                frame_info, text=f"{rotulo_chave}:", font=("Arial", 16, "bold")
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

        self.idade_edicao.delete(0, "end")
        self.idade_edicao.insert(0, str(personagem.get("idade", "")))
        self._carregar_especies_edicao(personagem.get("especie"))
        self.especie_edicao._ultima_escolha = self.especie_edicao.get()

        atual_sistema = next(
            (s["nome"] for s in self._sistemas_poder() if s["id"] == personagem.get("sistema_poder")),
            None
        )
        self._preencher_menu_sistema(self.sistema_edicao, atual_sistema)
        self.nome_poder_edicao.delete(0, "end")
        self.nome_poder_edicao.insert(0, personagem.get("nome_poder", ""))

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
        novo_caminho = escolher_arquivo(
            "Selecione uma imagem", ["png", "jpg", "jpeg", "webp"],
            descricao="Imagens", parent=self.toplevel_edicao
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

        caminho = escolher_arquivo(
            "Selecione uma imagem", ["png", "jpg", "jpeg", "webp"],
            descricao="Imagens", parent=self.toplevel_edicao
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
        personagem["idade"] = self.idade_edicao.get().strip()

        especie_escolhida = next(
            (e for e in historia.get("especies", []) if e["nome"] == self.especie_edicao.get()),
            None
        )
        personagem["especie"] = especie_escolhida["id"] if especie_escolhida else ""

        sistema_escolhido = next(
            (s for s in historia.get("sistemas_poder", []) if s["nome"] == self.sistema_edicao.get()),
            None
        )
        personagem["sistema_poder"] = sistema_escolhido["id"] if sistema_escolhido else ""
        personagem["nome_poder"] = self.nome_poder_edicao.get().strip()
        personagem.pop("poderes", None)
        personagem.pop("fraquezas", None)

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
        vincular_toplevel(self.toplevel_edicao, self.janela)
        self.toplevel_edicao.geometry("760x640")
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

        # Idade e espécie lado a lado
        frame_idade_especie = ctk.CTkFrame(corpo, fg_color="transparent")
        frame_idade_especie.pack(fill="x", padx=10, pady=5)

        frame_idade_especie.grid_columnconfigure(0, weight=1)
        frame_idade_especie.grid_columnconfigure(1, weight=1)

        # Idade

        coluna_idade = ctk.CTkFrame(frame_idade_especie, fg_color="transparent")
        coluna_idade.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(coluna_idade, text="Idade:").pack(anchor="w")

        self.idade_edicao = ctk.CTkEntry(
            coluna_idade,
            placeholder_text="Ex.: 25 anos"
        )
        self.idade_edicao.pack(fill="x", pady=5)

        # Especie

        coluna_especie = ctk.CTkFrame(frame_idade_especie, fg_color="transparent")
        coluna_especie.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ctk.CTkLabel(coluna_especie, text="Espécie:").pack(anchor="w")

        self.especie_edicao = ctk.CTkOptionMenu(
            coluna_especie, values=[ESPECIE_PADRAO],
            command=lambda valor: self._ao_escolher_especie(self.especie_edicao, valor)
        )
        self.especie_edicao.set(ESPECIE_PADRAO)
        self.especie_edicao.pack(fill="x", pady=5)

        campos = [
            ("personalidade", "Personalidade:"),
            ("aparencia", "Aparência:"),
            ("historia", "História:"),
            ("relacoes", "Relações:"),
            ("habilidades", "Habilidades:"),
        ]

        self.campos_edicao = {}

        for chave, rotulo in campos:
            if chave == "habilidades":
                ctk.CTkLabel(corpo, text="Sistema de poder:").pack(anchor="w", padx=10, pady=(10, 0))

                frame_sistema = ctk.CTkFrame(corpo, fg_color="transparent")
                frame_sistema.pack(fill="x", padx=10, pady=5)
                frame_sistema.grid_columnconfigure(0, weight=1)
                frame_sistema.grid_columnconfigure(1, weight=1)

                self.sistema_edicao = ctk.CTkOptionMenu(
                    frame_sistema, values=[SISTEMA_PADRAO],
                    command=lambda valor: self._ao_escolher_sistema(self.sistema_edicao, valor)
                )
                self.sistema_edicao.set(SISTEMA_PADRAO)
                self.sistema_edicao.grid(row=0, column=0, sticky="ew", padx=(0, 5))

                self.nome_poder_edicao = ctk.CTkEntry(
                    frame_sistema, placeholder_text="Nome do poder (Ex.: Fusimorfo)"
                )
                self.nome_poder_edicao.grid(row=0, column=1, sticky="ew", padx=(5, 0))
                configurar_entry(self.nome_poder_edicao)

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
        historia = self._historia_selecionada()

        if historia is None:
            print("Selecione a historia primeiro")
            return

        self._preencher_menu_especie(self.especie_criacao)
        self.especie_criacao._ultima_escolha = ESPECIE_PADRAO

        self._preencher_menu_sistema(self.sistema_criacao)
        self.nome_poder_criacao.delete(0, "end")

        self.toplevel.deiconify()
        self.toplevel.lift()
        self.toplevel.focus_force()

    def _escolher_imagem_principal(self):
        caminho = escolher_arquivo(
            "Selecione uma imagem", ["png", "jpg", "jpeg", "webp"],
            descricao="Imagens"
        )

        if not caminho:
            return

        self.caminho_imagem_criacao = caminho

        img_ctk = mostrar_imagem(caminho, 250)
        self.preview_criacao.configure(image=img_ctk, text="")
        self.preview_criacao.image = img_ctk

    def _adicionar_imagem_galeria_criacao(self):
        caminho = escolher_arquivo(
            "Selecione uma imagem", ["png", "jpg", "jpeg", "webp"],
            descricao="Imagens"
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

        nome_novo = self.personame_criacao.get().strip()

        if not nome_novo:
            messagebox.showwarning(
                "Criar personagem", "Digite um nome para o personagem.",
                parent=self.toplevel
            )
            return

        if any(p["nome"] == nome_novo for p in historia["personagens"]):
            messagebox.showwarning(
                "Criar personagem", "Já existe um personagem com esse nome.",
                parent=self.toplevel
            )
            return

        nome_sistema = self.sistema_criacao.get()

        sistema = next(
            (s for s in historia.get("sistemas_poder", []) if s["nome"] == nome_sistema),
            None
        )

        nome_especie = self.especie_criacao.get()

        especie = next(
            (
                e for e in historia.get("especies", [])
                if e["nome"] == nome_especie
            ),None)

        novo = criar_personagem(
            historia,
            nome_novo,
            self.idade_criacao.get().strip(),
            especie,
            self.caminho_imagem_criacao,
            self.personalidade_criacao.get("1.0", "end-1c"),
            self.aparencia_criacao.get("1.0", "end-1c"),
            self.historia_criacao.get("1.0", "end-1c"),
            self.relacoes_criacao.get("1.0", "end-1c"),
            sistema,
            self.habilidades_criacao.get("1.0", "end-1c"),
            self.nome_poder_criacao.get().strip()
        )

        if novo is None:
            return


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
        vincular_toplevel(self.toplevel, self.janela)
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
        self.janela_criacao.grid_rowconfigure(7, weight=1)
        self.janela_criacao.grid_rowconfigure(8, weight=1)
        self.janela_criacao.grid_rowconfigure(9, weight=0)
        self.janela_criacao.grid_rowconfigure(10, weight=0)

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

        # Idade e espécie lado a lado
        frame_idade_especie = ctk.CTkFrame(self.janela_criacao,fg_color="transparent")
        frame_idade_especie.grid(column=1, row=1, columnspan=2,sticky="we", padx=5, pady=5)
        frame_idade_especie.grid_columnconfigure((0, 1), weight=1)

        # Idade
        coluna_idade = ctk.CTkFrame(frame_idade_especie,fg_color="transparent")
        coluna_idade.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkLabel(coluna_idade, text="Idade:").pack(anchor="w")
        self.idade_criacao = ctk.CTkEntry(coluna_idade,placeholder_text="Ex.: 25 anos")
        self.idade_criacao.pack(fill="x", pady=5)

        # Espécie
        coluna_especie = ctk.CTkFrame(frame_idade_especie,fg_color="transparent")
        coluna_especie.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ctk.CTkLabel(coluna_especie, text="Espécie:").pack(anchor="w")

        self.especie_criacao = ctk.CTkOptionMenu(
            coluna_especie, values=[ESPECIE_PADRAO],
            command=lambda valor: self._ao_escolher_especie(self.especie_criacao, valor)
        )
        self.especie_criacao.set(ESPECIE_PADRAO)
        self.especie_criacao.pack(fill="x", pady=5)

        ctk.CTkLabel(self.janela_criacao, text="Personalidade: ").grid(column=1, row=2)
        self.personalidade_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.personalidade_criacao.grid(column=2, row=2, sticky="we")
        configurar_textbox(self.personalidade_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Aparencia: ").grid(column=1, row=3)
        self.aparencia_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.aparencia_criacao.grid(column=2, row=3, sticky="we")
        configurar_textbox(self.aparencia_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Relações").grid(column=1, row=4)
        self.relacoes_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.relacoes_criacao.grid(column=2, row=4, sticky="we")
        configurar_textbox(self.relacoes_criacao)

        ctk.CTkLabel(self.janela_criacao,text="Separe com ';', Ex: Esposa de X; Amiga de X",font=("Helvetica", 11)
                     ).grid(column=2, row=5, sticky="w")

        ctk.CTkLabel(self.janela_criacao, text="Historia do personagem").grid(column=1, row=6)
        self.historia_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.historia_criacao.grid(column=2, row=6, sticky="we")
        configurar_textbox(self.historia_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Sistema de poder:").grid(column=1, row=7)
        frame_sistema_criacao = ctk.CTkFrame(self.janela_criacao, fg_color="transparent")
        frame_sistema_criacao.grid(column=2, row=7, sticky="we")
        frame_sistema_criacao.grid_columnconfigure((0, 1), weight=1)

        self.sistema_criacao = ctk.CTkOptionMenu(
            frame_sistema_criacao, values=[SISTEMA_PADRAO],
            command=lambda valor: self._ao_escolher_sistema(self.sistema_criacao, valor)
        )
        self.sistema_criacao.set(SISTEMA_PADRAO)
        self.sistema_criacao.grid(row=0, column=0, sticky="we", padx=(0, 5))

        self.nome_poder_criacao = ctk.CTkEntry(
            frame_sistema_criacao, placeholder_text="Nome do poder (Ex.: Fusimorfo)"
        )
        self.nome_poder_criacao.grid(row=0, column=1, sticky="we", padx=(5, 0))
        configurar_entry(self.nome_poder_criacao)

        ctk.CTkLabel(self.janela_criacao, text="Habilidades:").grid(column=1, row=8)
        self.habilidades_criacao = ctk.CTkTextbox(self.janela_criacao, height=50)
        self.habilidades_criacao.grid(column=2, row=8, sticky="we")
        configurar_textbox(self.habilidades_criacao)

        ctk.CTkButton(
            self.janela_criacao, text="[Fechar]",
            command=lambda: self.toplevel.withdraw()
        ).grid(column=1, row=10, sticky="se", pady=10, padx=10)

        ctk.CTkButton(
            self.janela_criacao, text="[Salvar Personagem]",
            command=lambda: self._salvar_criacao()
        ).grid(column=2, row=10, sticky="se", pady=10, padx=10)