import copy
import customtkinter as ctk

from tkinter import messagebox

import historias
from undo import HistoricoDesfazer
from entry_textbox import configurar_entry, configurar_textbox


class JanelaFerramenta:
    """
    Base das ferramentas do Mural. Cada ferramenta tem UM ÚNICO Toplevel:
    ele é criado na primeira vez e depois só é escondido/mostrado
    (withdraw/deiconify), como as outras janelas do programa.

    Ctrl+Z desfaz e Ctrl+Y (ou Ctrl+Shift+Z) refaz — as subclasses
    implementam `desfazer()` e `refazer()`.
    """

    titulo = "Ferramenta"
    geometria = "1100x700"
    tamanho_minimo = (800, 500)

    def __init__(self, janela, obter_historia):
        self.janela = janela
        self.obter_historia = obter_historia
        self.tl = None
        self.overlay = None
        self._historia_id = None

    # ---- ciclo de vida ------------------------------------------------

    def abrir(self):
        historia = self.obter_historia()
        if historia is None:
            messagebox.showinfo("Mural", "Selecione uma história primeiro.")
            return

        if self.tl is None or not self.tl.winfo_exists():
            self.tl = ctk.CTkToplevel(self.janela)
            self.tl.geometry(self.geometria)
            self.tl.minsize(*self.tamanho_minimo)
            self.tl.protocol("WM_DELETE_WINDOW", self.fechar)
            self.tl.bind("<Control-z>", self._atalho_desfazer)
            self.tl.bind("<Control-Z>", self._atalho_refazer)
            self.tl.bind("<Control-y>", self._atalho_refazer)
            self.tl.bind("<Escape>", lambda e: self.fechar_overlay())
            self._historia_id = None
            self.construir(self.tl)

        if self._historia_id != historia["id"]:
            self._historia_id = historia["id"]
            self.ao_trocar_historia(historia)

        self.tl.title(f"{self.titulo} — {historia['nome']}")
        self.tl.deiconify()
        self.tl.lift()
        self.tl.focus_force()

    def fechar(self):
        if not self.pode_fechar():
            return
        self.fechar_overlay()
        self.ao_fechar()
        self.tl.withdraw()

    # ---- ganchos para as subclasses -------------------------------------

    def construir(self, tl):
        raise NotImplementedError

    def ao_trocar_historia(self, historia):
        pass

    def pode_fechar(self):
        return True

    def ao_fechar(self):
        pass

    def desfazer(self):
        pass

    def refazer(self):
        pass

    def _atalho_desfazer(self, event=None):
        # Se um campo de texto tem o foco, o Tk já trata Ctrl+Z de forma
        # própria (textboxes) — aqui desfazemos as ações da ferramenta.
        self.desfazer()
        return "break"

    def _atalho_refazer(self, event=None):
        self.refazer()
        return "break"

    # ---- dados da história -----------------------------------------------

    def historia(self):
        return self.obter_historia()

    def lista(self, chave):
        return self.historia().setdefault(chave, [])

    # ---- formulário inline (sem criar outro Toplevel) ----------------------

    def fechar_overlay(self):
        if self.overlay is not None and self.overlay.winfo_exists():
            self.overlay.destroy()
        self.overlay = None

    def pedir_campos(self, titulo, campos, ao_confirmar, texto_ok="OK",
                     altura=None, ao_mudar=None, largura=460):
        """
        Mostra um formulário por cima da janela da ferramenta.

        campos: lista de dicts {"chave", "rotulo", "tipo": entry|menu|check|texto,
                                "valor", "opcoes", "placeholder"}
        ao_confirmar(valores) -> None se deu certo (fecha) ou texto de erro.
        ao_mudar(chave, valor, widgets) é chamado quando um menu/check muda.
        Devolve o dict de widgets (chave -> widget).
        """
        self.fechar_overlay()

        ov = ctk.CTkFrame(self.tl, corner_radius=12, border_width=2)
        ov.place(relx=0.5, rely=0.5, anchor="center")
        ov.lift()
        self.overlay = ov
        ov.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ov, text=titulo, font=("Helvetica", 20, "bold"),
                     anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))

        if altura is None:
            altura = min(70 * len(campos) + 20, 480)

        corpo = ctk.CTkScrollableFrame(ov, width=largura, height=altura,
                                       fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew", padx=10)
        corpo.grid_columnconfigure(0, weight=1)

        widgets = {}
        tipos = {}
        linha = 0
        for campo in campos:
            chave = campo["chave"]
            tipo = campo.get("tipo", "entry")
            valor = campo.get("valor", "")
            tipos[chave] = tipo

            if tipo == "check":
                var = ctk.BooleanVar(value=bool(valor))
                w = ctk.CTkCheckBox(
                    corpo, text=campo["rotulo"], variable=var,
                    command=lambda c=chave: ao_mudar and ao_mudar(c, widgets[c].get() in (1, True), widgets))
                w.var = var
                w.grid(row=linha, column=0, sticky="w", padx=8, pady=(8, 8))
                linha += 1
                widgets[chave] = w
                continue

            ctk.CTkLabel(corpo, text=campo["rotulo"], anchor="w",
                         justify="left").grid(row=linha, column=0, sticky="w", padx=8)
            linha += 1

            if tipo == "menu":
                opcoes = list(campo["opcoes"]) or [""]
                w = ctk.CTkOptionMenu(
                    corpo, values=opcoes,
                    command=lambda v, c=chave: ao_mudar and ao_mudar(c, v, widgets))
                w.set(valor if valor in opcoes else opcoes[0])
            elif tipo == "texto":
                w = ctk.CTkTextbox(corpo, height=campo.get("altura", 80))
                w.insert("1.0", str(valor))
                configurar_textbox(w)
            else:
                w = ctk.CTkEntry(corpo, placeholder_text=campo.get("placeholder", ""))
                if valor != "":
                    w.insert(0, str(valor))
                configurar_entry(w)

            w.grid(row=linha, column=0, sticky="ew", padx=8, pady=(2, 8))
            linha += 1
            widgets[chave] = w

        def ler():
            valores = {}
            for chave, w in widgets.items():
                if tipos[chave] == "texto":
                    valores[chave] = w.get("1.0", "end-1c").strip()
                elif tipos[chave] == "check":
                    valores[chave] = bool(w.var.get())
                else:
                    valores[chave] = w.get().strip()
            return valores

        erro = ctk.CTkLabel(ov, text="", text_color="#ff6b6b", anchor="w",
                            justify="left", wraplength=largura - 20)
        erro.grid(row=2, column=0, sticky="ew", padx=20)

        def confirmar(event=None):
            resultado = ao_confirmar(ler())
            if resultado:
                erro.configure(text=resultado)
            else:
                self.fechar_overlay()

        botoes = ctk.CTkFrame(ov, fg_color="transparent")
        botoes.grid(row=3, column=0, sticky="ew", padx=20, pady=(5, 15))
        botoes.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(botoes, text="Cancelar", fg_color="gray30", hover_color="gray40",
                      command=self.fechar_overlay).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(botoes, text=texto_ok, command=confirmar).grid(
            row=0, column=1, padx=(5, 0), sticky="ew")

        for chave, w in widgets.items():
            if tipos[chave] == "entry":
                w.bind("<Return>", confirmar)

        primeiro = next((w for c, w in widgets.items() if tipos[c] == "entry"), None)
        if primeiro is not None:
            ov.after(80, primeiro.focus)

        return widgets


class JanelaRascunho(JanelaFerramenta):
    """
    Ferramenta com lista de itens à esquerda e um editor à direita que
    trabalha num RASCUNHO: nada vai para o disco até clicar em "Salvar", e
    a visualização mostra sempre o rascunho (antes de salvar).

    Subclasses definem:
        chave            -> chave da lista na história ("calendarios", ...)
        rotulo_item      -> "calendário", "dicionário"
        campos_novo()    -> campos pedidos ao criar
        criar_item(valores) -> dict do novo item (ou texto de erro)
        construir_area(frame) -> monta o editor/visualização
        ao_carregar_rascunho() -> desenha o editor a partir de self.rascunho
        validar(rascunho) -> texto de erro ou None
    """

    chave = None
    rotulo_item = "item"
    icone = ""

    def construir(self, tl):
        tl.grid_columnconfigure(1, weight=1)
        tl.grid_rowconfigure(0, weight=1)

        self.rascunho = None
        self.original = None
        self.salvo = None
        self.historico = HistoricoDesfazer()

        lateral = ctk.CTkFrame(tl, width=220)
        lateral.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        lateral.grid_propagate(False)
        lateral.grid_rowconfigure(1, weight=1)
        lateral.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(lateral, text=f"{self.icone} {self.titulo.split(' ', 1)[-1]}",
                     font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=8)

        self.frame_lista = ctk.CTkScrollableFrame(lateral)
        self.frame_lista.grid(row=1, column=0, sticky="nsew", padx=6)
        self.frame_lista.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(lateral, text=f"+ Novo {self.rotulo_item}",
                      command=self.novo).grid(row=2, column=0, padx=8, pady=(8, 4), sticky="ew")
        ctk.CTkButton(lateral, text="🗑 Excluir", fg_color="#8b2e2e", hover_color="#a33a3a",
                      command=self.excluir).grid(row=3, column=0, padx=8, pady=(0, 10), sticky="ew")

        self.area = ctk.CTkFrame(tl, fg_color="transparent")
        self.area.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.area.grid_columnconfigure(0, weight=1)
        self.area.grid_rowconfigure(1, weight=1)

        # Barra de estado + salvar
        barra = ctk.CTkFrame(self.area)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        barra.grid_columnconfigure(0, weight=1)
        self.lbl_estado = ctk.CTkLabel(barra, text="Nenhum item selecionado", anchor="w")
        self.lbl_estado.grid(row=0, column=0, sticky="ew", padx=10, pady=6)
        ctk.CTkButton(barra, text="↶", width=34, command=self.desfazer).grid(row=0, column=1, padx=2)
        ctk.CTkButton(barra, text="↷", width=34, command=self.refazer).grid(row=0, column=2, padx=2)
        ctk.CTkButton(barra, text="Descartar alterações", fg_color="gray30", hover_color="gray40",
                      command=self.descartar).grid(row=0, column=3, padx=4, pady=6)
        self.btn_salvar = ctk.CTkButton(barra, text="💾 Salvar", command=self.salvar)
        self.btn_salvar.grid(row=0, column=4, padx=(4, 8), pady=6)

        self.conteudo = ctk.CTkFrame(self.area, fg_color="transparent")
        self.conteudo.grid(row=1, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)
        self.construir_area(self.conteudo)

        self.recarregar_lista()
        self._atualizar_estado()

    # ---- ganchos -----------------------------------------------------------

    def campos_novo(self):
        return [{"chave": "nome", "rotulo": "Nome:", "tipo": "entry"}]

    def criar_item(self, valores):
        raise NotImplementedError

    def construir_area(self, frame):
        raise NotImplementedError

    def ao_carregar_rascunho(self):
        pass

    def validar(self, rascunho):
        return None

    # ---- lista ---------------------------------------------------------------

    def ao_trocar_historia(self, historia):
        self.rascunho = self.original = self.salvo = None
        self.historico.reiniciar({})
        self.recarregar_lista()
        self.ao_carregar_rascunho()
        self._atualizar_estado()

    def recarregar_lista(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()
        for i, item in enumerate(self.lista(self.chave)):
            ativo = self.original is item
            ctk.CTkButton(
                self.frame_lista, text=item["nome"], anchor="w",
                fg_color=("#1f6aa5" if ativo else "gray30"),
                command=lambda it=item: self.selecionar(it)
            ).grid(row=i, column=0, sticky="ew", pady=2)

    # ---- rascunho ---------------------------------------------------------------

    @property
    def alterado(self):
        return self.rascunho is not None and self.rascunho != self.salvo

    def _atualizar_estado(self):
        if self.rascunho is None:
            self.lbl_estado.configure(text="Nenhum item selecionado — escolha um ou crie um novo.")
            self.btn_salvar.configure(state="disabled")
            return
        marca = "  ● alterações não salvas" if self.alterado else "  ✔ salvo"
        novo = "  (novo)" if self.original is None else ""
        self.lbl_estado.configure(text=f"{self.rascunho['nome']}{novo}{marca}")
        self.btn_salvar.configure(state="normal")

    def _confirmar_descartar(self):
        if not self.alterado:
            return True
        r = messagebox.askyesnocancel(
            "Alterações não salvas",
            f'Salvar as alterações em "{self.rascunho["nome"]}" antes de continuar?',
            parent=self.tl)
        if r is None:
            return False
        if r:
            return self.salvar()
        return True

    def pode_fechar(self):
        return self.rascunho is None or self._confirmar_descartar()

    def carregar(self, rascunho, original):
        self.rascunho = rascunho
        self.original = original
        self.salvo = copy.deepcopy(original) if original is not None else None
        self.historico.reiniciar(rascunho)
        self.recarregar_lista()
        self.ao_carregar_rascunho()
        self._atualizar_estado()

    def selecionar(self, item):
        if item is self.original and self.rascunho is not None:
            return
        if not self._confirmar_descartar():
            return
        self.carregar(copy.deepcopy(item), item)

    def checkpoint(self):
        """Chamar depois de cada ação do usuário no rascunho."""
        if self.rascunho is None:
            return
        self.historico.registrar(self.rascunho)
        self._atualizar_estado()

    def desfazer(self):
        if self.rascunho is None:
            return
        estado = self.historico.desfazer()
        if estado is not None:
            self.rascunho = estado
            self.ao_carregar_rascunho()
            self._atualizar_estado()

    def refazer(self):
        if self.rascunho is None:
            return
        estado = self.historico.refazer()
        if estado is not None:
            self.rascunho = estado
            self.ao_carregar_rascunho()
            self._atualizar_estado()

    def descartar(self):
        if self.rascunho is None or not self.alterado:
            return
        if self.original is None:
            self.rascunho = self.salvo = None
            self.historico.reiniciar({})
            self.ao_carregar_rascunho()
            self._atualizar_estado()
        else:
            self.carregar(copy.deepcopy(self.original), self.original)

    # ---- criar / salvar / excluir -------------------------------------------------

    def novo(self):
        if not self._confirmar_descartar():
            return

        def confirmar(valores):
            nome = valores.get("nome", "")
            if not nome:
                return "Digite um nome."
            if any(i["nome"].casefold() == nome.casefold() for i in self.lista(self.chave)):
                return f"Já existe um {self.rotulo_item} com esse nome."
            item = self.criar_item(valores)
            if isinstance(item, str):
                return item
            self.carregar(item, None)       # só vai para a lista ao salvar

        self.pedir_campos(f"Novo {self.rotulo_item}", self.campos_novo(), confirmar,
                          texto_ok="Criar")

    def salvar(self):
        if self.rascunho is None:
            return False

        erro = self.validar(self.rascunho)
        if erro:
            messagebox.showwarning("Não foi possível salvar", erro, parent=self.tl)
            return False

        nome = self.rascunho["nome"]
        for i in self.lista(self.chave):
            if i is not self.original and i["nome"].casefold() == nome.casefold():
                messagebox.showwarning(
                    "Não foi possível salvar",
                    f"Já existe um {self.rotulo_item} chamado \"{nome}\".", parent=self.tl)
                return False

        dados = copy.deepcopy(self.rascunho)
        if self.original is None:
            self.lista(self.chave).append(dados)
            self.original = dados
        else:
            self.original.clear()
            self.original.update(dados)

        self.salvo = copy.deepcopy(self.original)
        historias.atualizar()
        self.recarregar_lista()
        self._atualizar_estado()
        return True

    def excluir(self):
        if self.rascunho is None:
            return
        nome = self.rascunho["nome"]
        if not messagebox.askyesno(
                "Excluir", f'Deseja realmente excluir o {self.rotulo_item} "{nome}"?',
                parent=self.tl):
            return
        if self.original is not None:
            self.lista(self.chave).remove(self.original)
            historias.atualizar()
        self.rascunho = self.original = self.salvo = None
        self.historico.reiniciar({})
        self.recarregar_lista()
        self.ao_carregar_rascunho()
        self._atualizar_estado()
