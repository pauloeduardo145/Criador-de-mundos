import math
import customtkinter as ctk

from tkinter import messagebox

from mural import JanelaRascunho
from modelos import novo_dicionario, nova_letra
from entry_textbox import configurar_entry

TIPOS_LETRA = ["Vogal", "Consoante", "Símbolo", "Número", "Pontuação", "Outro"]
TAM_EDITOR = 340           # lado do quadro de desenho, em pixels
PASSO_MINIMO = 6           # distância mínima (em unidades 0..1000) entre pontos de um traço


def desenhar_tracos(canvas, tracos, x0, y0, tam, espessura, cor="#f2f2f2"):
    """Desenha os traços (coordenadas 0..1000) num quadrado de lado `tam`."""
    k = tam / 1000.0
    largura = max(1.0, espessura * k)
    for traco in tracos:
        if not traco:
            continue
        if len(traco) == 1:
            x, y = x0 + traco[0][0] * k, y0 + traco[0][1] * k
            r = largura / 2
            canvas.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline=cor)
            continue
        pontos = []
        for px, py in traco:
            pontos += [x0 + px * k, y0 + py * k]
        canvas.create_line(*pontos, fill=cor, width=largura, capstyle="round",
                           joinstyle="round", smooth=len(traco) > 2)


# ---------------------------------------------------------------------------
# API DE "FONTE" (funções puras, sem interface)
#
# O dicionário funciona como uma fonte: cada letra tem um glifo (traços num
# quadrado 0..1000) e um texto latino que ela representa ("equivale").
# Estas funções existem para a futura função que escreve texto com a fonte.
# ---------------------------------------------------------------------------

def mapa_fonte(dicionario):
    """[(texto_latino_em_minusculas, letra)], maiores primeiro (ex.: 'th' antes de 't')."""
    return sorted(
        ((l["equivale"].casefold(), l) for l in dicionario.get("letras", []) if l.get("equivale")),
        key=lambda par: -len(par[0]))


def tokenizar(dicionario, texto):
    """
    Converte um texto em uma lista de itens da fonte:
        ("glifo", letra) | ("espaco", None) | ("quebra", None) | ("desconhecido", caractere)
    """
    mapa = mapa_fonte(dicionario)
    baixo = texto.casefold()
    itens, i = [], 0
    while i < len(texto):
        ch = texto[i]
        if ch == "\n":
            itens.append(("quebra", None)); i += 1
        elif ch == " ":
            itens.append(("espaco", None)); i += 1
        else:
            achou = next(((eq, l) for eq, l in mapa if baixo.startswith(eq, i)), None)
            if achou:
                itens.append(("glifo", achou[1])); i += len(achou[0])
            else:
                itens.append(("desconhecido", ch)); i += 1
    return itens


class DicionarioJanela(JanelaRascunho):
    titulo = "📖 Dicionários"
    geometria = "1300x780"
    tamanho_minimo = (1000, 620)
    chave = "dicionarios"
    rotulo_item = "dicionário"
    icone = "📖"

    # ---- novo ----------------------------------------------------------------

    def campos_novo(self):
        return [
            {"chave": "nome", "rotulo": "Nome do dicionário:", "tipo": "entry",
             "placeholder": "Ex: Escrita Antiga"},
            {"chave": "descricao", "rotulo": "Descrição (opcional):", "tipo": "texto", "altura": 70},
        ]

    def criar_item(self, valores):
        return novo_dicionario(valores["nome"], self.historia(), valores.get("descricao", ""))

    # ---- área principal --------------------------------------------------------

    def construir_area(self, frame):
        self.letra_id = None
        self.ferramenta = ctk.StringVar(value="Pincel")
        self._traco_atual = None
        self._apagou = False

        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(frame, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        topo.grid_columnconfigure(1, weight=1)
        topo.grid_columnconfigure(3, weight=2)
        ctk.CTkLabel(topo, text="Nome:").grid(row=0, column=0, padx=(0, 4))
        self.e_nome = ctk.CTkEntry(topo)
        self.e_nome.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(topo, text="Descrição:").grid(row=0, column=2, padx=(10, 4))
        self.e_desc = ctk.CTkEntry(topo)
        self.e_desc.grid(row=0, column=3, sticky="ew")
        for e in (self.e_nome, self.e_desc):
            configurar_entry(e)
            e.bind("<KeyRelease>", self._ler_topo)
            e.bind("<FocusOut>", lambda ev: self.checkpoint())
            e.bind("<Return>", lambda ev: self.checkpoint())

        corpo = ctk.CTkFrame(frame, fg_color="transparent")
        corpo.grid(row=1, column=0, sticky="nsew")
        corpo.grid_columnconfigure(1, weight=1)
        corpo.grid_rowconfigure(0, weight=1)

        # Letras
        painel = ctk.CTkFrame(corpo, width=290)
        painel.grid(row=0, column=0, sticky="ns", padx=(0, 6))
        painel.grid_propagate(False)
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_columnconfigure(0, weight=1)
        self.lbl_letras = ctk.CTkLabel(painel, text="Letras", font=("Helvetica", 15, "bold"))
        self.lbl_letras.grid(row=0, column=0, pady=6)
        self.grade_letras = ctk.CTkScrollableFrame(painel)
        self.grade_letras.grid(row=1, column=0, sticky="nsew", padx=4)
        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="ew", padx=4, pady=6)
        botoes.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(botoes, text="+ Letra", command=self.adicionar_letra).grid(
            row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(botoes, text="− Remover", fg_color="#8b2e2e", hover_color="#a33a3a",
                      command=self.remover_letra).grid(row=0, column=1, padx=2, sticky="ew")

        # Abas
        self.abas = ctk.CTkTabview(corpo, command=self._ao_mudar_aba)
        self.abas.grid(row=0, column=1, sticky="nsew")
        self.aba_desenho = self.abas.add("✏️ Desenhar letra")
        self.aba_visual = self.abas.add("👁 Visualizar dicionário")
        self._montar_aba_desenho(self.aba_desenho)
        self._montar_aba_visual(self.aba_visual)

    # ---- rascunho -----------------------------------------------------------------------------------

    def ao_carregar_rascunho(self):
        d = self.rascunho
        for e, valor in ((self.e_nome, d["nome"] if d else ""),
                         (self.e_desc, d.get("descricao", "") if d else "")):
            e.configure(state="normal")
            e.delete(0, "end")
            e.insert(0, valor)
            if d is None:
                e.configure(state="disabled")

        if d is None or not any(l["id"] == self.letra_id for l in d["letras"]):
            self.letra_id = d["letras"][0]["id"] if d and d["letras"] else None

        self._montar_letras()
        self._carregar_letra()
        self._atualizar_visual()

    def _ler_topo(self, event=None):
        if self.rascunho is None:
            return
        self.rascunho["nome"] = self.e_nome.get().strip() or self.rascunho["nome"]
        self.rascunho["descricao"] = self.e_desc.get().strip()
        self._atualizar_estado()

    def checkpoint(self):
        super().checkpoint()
        self._montar_letras()
        self._atualizar_visual()

    def validar(self, d):
        if not d["nome"].strip():
            return "O dicionário precisa de um nome."
        if any(not l["nome"].strip() for l in d["letras"]):
            return "Todas as letras precisam de um nome."
        return None

    def _letra(self):
        if self.rascunho is None:
            return None
        return next((l for l in self.rascunho["letras"] if l["id"] == self.letra_id), None)

    # ---- painel de letras --------------------------------------------------------------------------------

    def _montar_letras(self):
        for w in self.grade_letras.winfo_children():
            w.destroy()

        d = self.rascunho
        letras = d["letras"] if d else []
        self.lbl_letras.configure(text=f"Letras ({len(letras)})")
        colunas = 3
        for c in range(colunas):
            self.grade_letras.grid_columnconfigure(c, weight=1)

        for i, letra in enumerate(letras):
            ativo = letra["id"] == self.letra_id
            card = ctk.CTkFrame(self.grade_letras, border_width=2,
                                border_color="#1f6aa5" if ativo else "gray25")
            card.grid(row=i // colunas, column=i % colunas, padx=3, pady=3, sticky="nsew")
            cv = ctk.CTkCanvas(card, width=64, height=64, bg="#1b1b1b", highlightthickness=0)
            cv.pack(padx=4, pady=(4, 0))
            desenhar_tracos(cv, letra["tracos"], 4, 4, 56, letra.get("espessura", 8))
            ctk.CTkLabel(card, text=letra["nome"] or "?", font=("Helvetica", 12)).pack(pady=(0, 3))
            for w in (card, cv, *card.winfo_children()):
                w.bind("<Button-1>", lambda e, lid=letra["id"]: self.selecionar_letra(lid))

    def selecionar_letra(self, letra_id):
        self.letra_id = letra_id
        self._montar_letras()
        self._carregar_letra()

    def adicionar_letra(self):
        if self.rascunho is None:
            return

        def confirmar(v):
            nome = v["nome"]
            if not nome:
                return "Digite o nome da letra."
            if any(l["nome"] == nome for l in self.rascunho["letras"]):
                return "Já existe uma letra com esse nome."
            letra = nova_letra(nome)
            self.rascunho["letras"].append(letra)
            self.letra_id = letra["id"]
            self.checkpoint()
            self._carregar_letra()

        self.pedir_campos("Nova letra", [
            {"chave": "nome", "rotulo": "Nome da letra (ex.: A, Ka, Th):", "tipo": "entry"}
        ], confirmar, texto_ok="Adicionar")

    def remover_letra(self):
        letra = self._letra()
        if letra is None:
            return
        if not messagebox.askyesno("Remover", f'Remover a letra "{letra["nome"]}"?', parent=self.tl):
            return
        letras = self.rascunho["letras"]
        i = letras.index(letra)
        letras.remove(letra)
        self.letra_id = letras[min(i, len(letras) - 1)]["id"] if letras else None
        self.checkpoint()
        self._carregar_letra()

    # ---- aba: desenhar -------------------------------------------------------------------------------------

    def _montar_aba_desenho(self, aba):
        aba.grid_columnconfigure(1, weight=1)
        aba.grid_rowconfigure(0, weight=1)

        # Atributos
        attrs = ctk.CTkFrame(aba, width=260)
        attrs.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        attrs.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(attrs, text="Atributos da letra",
                     font=("Helvetica", 15, "bold")).grid(row=0, column=0, pady=8)

        self.attr = {}
        linha = 1
        for chave, rotulo in (("nome", "Nome"), ("equivale", "Equivale a (texto latino)"),
                              ("pronuncia", "Pronúncia"), ("notas", "Notas"),
                              ("avanco", "Largura do glifo (1000 = quadrado)")):
            ctk.CTkLabel(attrs, text=rotulo, anchor="w").grid(row=linha, column=0, sticky="w", padx=10)
            e = ctk.CTkEntry(attrs)
            e.grid(row=linha + 1, column=0, sticky="ew", padx=10, pady=(0, 6))
            configurar_entry(e)
            e.bind("<KeyRelease>", self._ler_atributos)
            e.bind("<FocusOut>", lambda ev: self.checkpoint())
            e.bind("<Return>", lambda ev: self.checkpoint())
            self.attr[chave] = e
            linha += 2

        ctk.CTkLabel(attrs, text="Tipo", anchor="w").grid(row=linha, column=0, sticky="w", padx=10)
        self.menu_tipo = ctk.CTkOptionMenu(attrs, values=TIPOS_LETRA, command=self._ao_mudar_tipo)
        self.menu_tipo.grid(row=linha + 1, column=0, sticky="ew", padx=10, pady=(0, 6))
        linha += 2

        ctk.CTkLabel(attrs, text="Espessura do traço", anchor="w").grid(
            row=linha, column=0, sticky="w", padx=10)
        self.slider_espessura = ctk.CTkSlider(attrs, from_=2, to=40, number_of_steps=38,
                                              command=self._ao_mudar_espessura)
        self.slider_espessura.grid(row=linha + 1, column=0, sticky="ew", padx=10, pady=(0, 6))
        self.slider_espessura.bind("<ButtonRelease-1>", lambda e: self.checkpoint())

        # Quadro
        centro = ctk.CTkFrame(aba, fg_color="transparent")
        centro.grid(row=0, column=1, sticky="nsew")
        centro.grid_columnconfigure(0, weight=1)

        ferramentas = ctk.CTkFrame(centro, fg_color="transparent")
        ferramentas.grid(row=0, column=0, pady=(4, 6))
        ctk.CTkSegmentedButton(ferramentas, values=["Pincel", "Borracha"],
                               variable=self.ferramenta).pack(side="left", padx=4)
        ctk.CTkButton(ferramentas, text="Limpar letra", width=100, fg_color="gray30",
                      hover_color="gray40", command=self.limpar_letra).pack(side="left", padx=4)

        self.quadro = ctk.CTkCanvas(centro, width=TAM_EDITOR, height=TAM_EDITOR,
                                    bg="#1b1b1b", highlightthickness=1,
                                    highlightbackground="#555555", cursor="crosshair")
        self.quadro.grid(row=1, column=0, pady=4)
        self.quadro.bind("<ButtonPress-1>", self._quadro_pressionar)
        self.quadro.bind("<B1-Motion>", self._quadro_mover)
        self.quadro.bind("<ButtonRelease-1>", self._quadro_soltar)

        ctk.CTkLabel(centro, text="Desenhe com o mouse · Ctrl+Z desfaz o último traço",
                     text_color="gray60").grid(row=2, column=0)

    def _carregar_letra(self):
        letra = self._letra()
        estado = "normal" if letra else "disabled"
        for chave, e in self.attr.items():
            e.configure(state="normal")
            e.delete(0, "end")
            if letra:
                e.insert(0, letra.get(chave, 1000 if chave == "avanco" else ""))
            e.configure(state=estado)
        self.menu_tipo.configure(state=estado)
        self.slider_espessura.configure(state=estado)
        if letra:
            self.menu_tipo.set(letra.get("tipo", "Consoante"))
            self.slider_espessura.set(letra.get("espessura", 8))
        self._redesenhar_quadro()

    def _ler_atributos(self, event=None):
        letra = self._letra()
        if letra is None:
            return
        for chave, e in self.attr.items():
            texto = e.get().strip()
            if chave == "avanco":
                try:
                    letra[chave] = max(100, min(3000, int(texto)))
                except ValueError:
                    pass
            else:
                letra[chave] = texto
        self._atualizar_estado()

    def _ao_mudar_tipo(self, valor):
        letra = self._letra()
        if letra:
            letra["tipo"] = valor
            self.checkpoint()

    def _ao_mudar_espessura(self, valor):
        letra = self._letra()
        if letra:
            letra["espessura"] = int(valor)
            self._redesenhar_quadro()
            self._atualizar_estado()

    def _redesenhar_quadro(self):
        c = self.quadro
        c.delete("all")
        # guias (linha de base e meio)
        for f in (0.2, 0.5, 0.8):
            y = TAM_EDITOR * f
            c.create_line(0, y, TAM_EDITOR, y, fill="#2c3b4a", dash=(4, 4))
        c.create_line(TAM_EDITOR / 2, 0, TAM_EDITOR / 2, TAM_EDITOR, fill="#2c3b4a", dash=(4, 4))
        letra = self._letra()
        if letra:
            desenhar_tracos(c, letra["tracos"], 0, 0, TAM_EDITOR, letra.get("espessura", 8))
        else:
            c.create_text(TAM_EDITOR / 2, TAM_EDITOR / 2, fill="gray60", justify="center",
                          text="Adicione ou selecione\numa letra para desenhar")

    def _para_glifo(self, event):
        k = 1000.0 / TAM_EDITOR
        return [max(0, min(1000, round(event.x * k, 1))), max(0, min(1000, round(event.y * k, 1)))]

    def _quadro_pressionar(self, event):
        letra = self._letra()
        if letra is None:
            return
        self._apagou = False
        if self.ferramenta.get() == "Borracha":
            self._apagar_em(event)
        else:
            self._traco_atual = [self._para_glifo(event)]
            letra["tracos"].append(self._traco_atual)
            self._redesenhar_quadro()

    def _quadro_mover(self, event):
        letra = self._letra()
        if letra is None:
            return
        if self.ferramenta.get() == "Borracha":
            self._apagar_em(event)
            return
        if self._traco_atual is None:
            return
        p = self._para_glifo(event)
        ultimo = self._traco_atual[-1]
        if math.hypot(p[0] - ultimo[0], p[1] - ultimo[1]) >= PASSO_MINIMO:
            self._traco_atual.append(p)
            self._redesenhar_quadro()

    def _quadro_soltar(self, event):
        if self._letra() is None:
            return
        if self.ferramenta.get() == "Borracha":
            if self._apagou:
                self.checkpoint()
        elif self._traco_atual is not None:
            self._traco_atual = None
            self.checkpoint()          # fim da ação = um traço

    def _apagar_em(self, event):
        letra = self._letra()
        p = self._para_glifo(event)
        raio = 45
        antes = len(letra["tracos"])
        letra["tracos"] = [
            t for t in letra["tracos"]
            if not any(math.hypot(x - p[0], y - p[1]) <= raio for x, y in t)
        ]
        if len(letra["tracos"]) != antes:
            self._apagou = True
            self._redesenhar_quadro()

    def limpar_letra(self):
        letra = self._letra()
        if letra and letra["tracos"]:
            letra["tracos"] = []
            self.checkpoint()
            self._redesenhar_quadro()

    def desfazer(self):
        super().desfazer()

    # ---- aba: visualizar ----------------------------------------------------------------------------------------

    def _montar_aba_visual(self, aba):
        aba.grid_columnconfigure(0, weight=1)
        aba.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(aba, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(barra, text="Texto de teste:").grid(row=0, column=0, padx=(0, 6))
        self.e_teste = ctk.CTkEntry(barra, placeholder_text="Escreva algo para ver na escrita do dicionário")
        self.e_teste.grid(row=0, column=1, sticky="ew")
        configurar_entry(self.e_teste)
        self.e_teste.bind("<KeyRelease>", lambda e: self._atualizar_visual())

        self.rolagem_visual = ctk.CTkScrollableFrame(aba)
        self.rolagem_visual.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.rolagem_visual.grid_columnconfigure(0, weight=1)

    def _ao_mudar_aba(self):
        self._atualizar_visual()

    def _atualizar_visual(self):
        if not hasattr(self, "rolagem_visual") or not self.rolagem_visual.winfo_exists():
            return
        if self.abas.get() != "👁 Visualizar dicionário":
            return

        for w in self.rolagem_visual.winfo_children():
            w.destroy()

        d = self.rascunho
        if d is None:
            return

        letras = d["letras"]
        ctk.CTkLabel(self.rolagem_visual, text=d["nome"], font=("Helvetica", 22, "bold"),
                     anchor="w").grid(row=0, column=0, sticky="ew", padx=6)
        if d.get("descricao"):
            ctk.CTkLabel(self.rolagem_visual, text=d["descricao"], anchor="w", justify="left",
                         wraplength=700).grid(row=1, column=0, sticky="ew", padx=6)

        # Texto de teste escrito com as letras desenhadas
        texto = self.e_teste.get() or " ".join(l["equivale"] for l in letras if l["equivale"])
        larg = max(420, self.rolagem_visual.winfo_width() - 40)
        cv = ctk.CTkCanvas(self.rolagem_visual, width=larg, bg="#1b1b1b", highlightthickness=0)
        cv.grid(row=2, column=0, padx=6, pady=10, sticky="ew")
        altura = self._escrever(cv, texto, letras, larg)
        cv.configure(height=altura)

        ctk.CTkLabel(self.rolagem_visual, text=f"Todas as letras ({len(letras)})",
                     font=("Helvetica", 16, "bold"), anchor="w").grid(
            row=3, column=0, sticky="ew", padx=6, pady=(8, 2))

        grade = ctk.CTkFrame(self.rolagem_visual, fg_color="transparent")
        grade.grid(row=4, column=0, sticky="ew")
        colunas = max(1, larg // 150)
        for c in range(colunas):
            grade.grid_columnconfigure(c, weight=1, uniform="l")
        for i, l in enumerate(letras):
            card = ctk.CTkFrame(grade)
            card.grid(row=i // colunas, column=i % colunas, padx=4, pady=4, sticky="nsew")
            g = ctk.CTkCanvas(card, width=96, height=96, bg="#1b1b1b", highlightthickness=0)
            g.pack(padx=8, pady=(8, 2))
            desenhar_tracos(g, l["tracos"], 6, 6, 84, l.get("espessura", 8))
            ctk.CTkLabel(card, text=f'{l["nome"]}  →  {l["equivale"] or "—"}',
                         font=("Helvetica", 13, "bold")).pack()
            detalhe = l.get("tipo", "")
            if l.get("pronuncia"):
                detalhe += f' · /{l["pronuncia"]}/'
            ctk.CTkLabel(card, text=detalhe, text_color="gray70").pack()
            if l.get("notas"):
                ctk.CTkLabel(card, text=l["notas"], wraplength=130, text_color="gray60").pack(pady=(0, 4))
        if not letras:
            ctk.CTkLabel(grade, text="Nenhuma letra ainda.").grid(row=0, column=0, pady=20)

    def _escrever(self, cv, texto, letras, largura, tam=56):
        """Escreve `texto` com a fonte do dicionário. Devolve a altura usada."""
        x, y = 8, 8
        for tipo, valor in tokenizar({"letras": letras}, texto):
            if tipo == "quebra":
                x, y = 8, y + tam + 8
                continue
            if tipo == "espaco":
                x += tam * 0.5
                continue
            avanco = tam * (valor.get("avanco", 1000) / 1000 if tipo == "glifo" else 0.6) * 0.95
            if x + avanco > largura - 8:
                x, y = 8, y + tam + 8
            if tipo == "glifo":
                desenhar_tracos(cv, valor["tracos"], x, y, tam, valor.get("espessura", 8))
            else:
                cv.create_text(x + avanco / 2, y + tam / 2, text=valor, fill="gray60",
                               font=("Helvetica", int(tam * 0.5)))
            x += avanco
        return y + tam + 8
