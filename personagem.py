import customtkinter as ctk
from widgets import mostrar_imagem
from entry_textbox import configurar_entry, configurar_textbox
from tkinter import filedialog, messagebox
import os
import shutil
import storage
import uuid
import historias


class Personagem:
    def __init__(self, frame_conteudo, obter_historia_selecionada=None):
        self.frame_conteudo = frame_conteudo
        
        self.obter_historia_selecionada = obter_historia_selecionada

        self.personagem_selecionado = None
        self.caminho_imagem = None


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
            return True
        return self.obter_historia_selecionada() is not None

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

        print(personagem["nome"])

    def edicao_personagem(self, *args):
        if self.personagem_selecionado is None:
            print("Nenhum personagem selecionado")
            return

        if "galeria" not in self.personagem_selecionado:
            self.personagem_selecionado["galeria"] = []

        if not self._historia_selecionada():
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