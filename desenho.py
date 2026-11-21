import io
import os
import shutil
import uuid

import customtkinter as ctk

from tkinter import messagebox, filedialog, colorchooser
from PIL import Image, ImageDraw, ImageTk

import historias
from storage import PASTA_DESENHOS
from mural import JanelaFerramenta
from modelos import novo_desenho
from undo import HistoricoDesfazer

FERRAMENTAS = ["✏️ Pincel", "🧽 Borracha", "🪣 Balde", "╱ Linha",
               "▭ Retângulo", "◯ Elipse", "💧 Conta-gotas"]
FORMATOS = ["png", "jpeg", "jpg", "webp"]
TRANSPARENTE = (0, 0, 0, 0)


def _xadrez(tamanho, quadrado=10):
    """Fundo quadriculado que indica transparência."""
    img = Image.new("RGBA", tamanho, (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, tamanho[1], quadrado):
        for x in range(0, tamanho[0], quadrado):
            if ((x // quadrado) + (y // quadrado)) % 2:
                d.rectangle([x, y, x + quadrado - 1, y + quadrado - 1], fill=(204, 204, 204, 255))
    return img


def _copiar_estado(e):
    return {"meta": list(e["meta"]), "imgs": [i.copy() for i in e["imgs"]], "ativa": e["ativa"]}


class DesenhoJanela(JanelaFerramenta):
    titulo = "🎨 Desenhar"
    geometria = "1350x800"
    tamanho_minimo = (1000, 600)

    # ---- construção -----------------------------------------------------------------

    def construir(self, tl):
        self.doc = None
        self.camadas = []
        self.ativa = 0
        self.cor = (0, 0, 0, 255)
        self.historico = HistoricoDesfazer(
            limite=30, copiar=_copiar_estado, igual=lambda a, b: False)

        self._ultimo = None
        self._inicio = None
        self._forma_item = None
        self._desenho = None
        self._agendado = False
        self._xadrez = None
        self._tk_img = None
        self._item_img = None
        self._sujas = set()
        self._acao_em_curso = False

        tl.grid_columnconfigure(1, weight=1)
        tl.grid_rowconfigure(0, weight=1)

        # -- lista de desenhos
        lateral = ctk.CTkFrame(tl, width=210)
        lateral.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        lateral.grid_propagate(False)
        lateral.grid_rowconfigure(1, weight=1)
        lateral.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(lateral, text="🎨 Desenhos", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=8)
        self.frame_lista = ctk.CTkScrollableFrame(lateral)
        self.frame_lista.grid(row=1, column=0, sticky="nsew", padx=6)
        self.frame_lista.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(lateral, text="+ Novo desenho", command=self.novo).grid(
            row=2, column=0, padx=8, pady=(8, 4), sticky="ew")
        ctk.CTkButton(lateral, text="🗑 Remover desenho", fg_color="#8b2e2e",
                      hover_color="#a33a3a", command=self.remover).grid(
            row=3, column=0, padx=8, pady=(0, 10), sticky="ew")

        # -- centro: ferramentas + tela
        centro = ctk.CTkFrame(tl, fg_color="transparent")
        centro.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        centro.grid_columnconfigure(0, weight=1)
        centro.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(centro)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.ferramenta = ctk.StringVar(value=FERRAMENTAS[0])
        ctk.CTkSegmentedButton(barra, values=FERRAMENTAS, variable=self.ferramenta).grid(
            row=0, column=0, columnspan=8, padx=8, pady=(8, 4), sticky="w")

        opcoes = ctk.CTkFrame(barra, fg_color="transparent")
        opcoes.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.btn_cor = ctk.CTkButton(opcoes, text="Cor", width=70, fg_color="#000000",
                                     hover=False, command=self.escolher_cor)
        self.btn_cor.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(opcoes, text="Tamanho").pack(side="left")
        self.slider_tam = ctk.CTkSlider(opcoes, from_=1, to=80, number_of_steps=79, width=150,
                                        command=lambda v: self.lbl_tam.configure(text=str(int(v))))
        self.slider_tam.set(8)
        self.slider_tam.pack(side="left", padx=6)
        self.lbl_tam = ctk.CTkLabel(opcoes, text="8", width=26)
        self.lbl_tam.pack(side="left")
        self.var_preencher = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opcoes, text="Preencher formas", variable=self.var_preencher).pack(
            side="left", padx=14)
        ctk.CTkLabel(opcoes, text="Tolerância do balde").pack(side="left")
        self.slider_tol = ctk.CTkSlider(opcoes, from_=0, to=100, number_of_steps=100, width=110)
        self.slider_tol.set(30)
        self.slider_tol.pack(side="left", padx=6)

        palco = ctk.CTkFrame(centro)
        palco.grid(row=1, column=0, sticky="nsew")
        palco.grid_columnconfigure(0, weight=1)
        palco.grid_rowconfigure(0, weight=1)
        self.tela = ctk.CTkCanvas(palco, bg="#3a3a3a", highlightthickness=0, cursor="crosshair")
        self.tela.grid(row=0, column=0, sticky="nsew")
        sb_v = ctk.CTkScrollbar(palco, orientation="vertical", command=self.tela.yview)
        sb_h = ctk.CTkScrollbar(palco, orientation="horizontal", command=self.tela.xview)
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        self.tela.configure(xscrollcommand=sb_h.set, yscrollcommand=sb_v.set)
        self.tela.bind("<ButtonPress-1>", self._pressionar)
        self.tela.bind("<B1-Motion>", self._mover)
        self.tela.bind("<ButtonRelease-1>", self._soltar)

        self.lbl_status = ctk.CTkLabel(centro, text="Crie ou selecione um desenho.", anchor="w")
        self.lbl_status.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        # -- camadas
        lat2 = ctk.CTkFrame(tl, width=230)
        lat2.grid(row=0, column=2, sticky="ns", padx=(5, 10), pady=10)
        lat2.grid_propagate(False)
        lat2.grid_rowconfigure(1, weight=1)
        lat2.grid_columnconfigure(0, weight=1)
        acoes = ctk.CTkFrame(lat2, fg_color="transparent")
        acoes.grid(row=0, column=0, sticky="ew", padx=6, pady=(8, 2))
        acoes.grid_columnconfigure(2, weight=1)
        ctk.CTkButton(acoes, text="↶", width=34, command=self.desfazer).grid(row=0, column=0, padx=(0, 2))
        ctk.CTkButton(acoes, text="↷", width=34, command=self.refazer).grid(row=0, column=1, padx=2)
        ctk.CTkButton(acoes, text="📤 Exportar…", command=self.exportar).grid(
            row=0, column=2, padx=(6, 0), sticky="ew")
        ctk.CTkLabel(lat2, text="Camadas", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=(52, 4))
        self.frame_camadas = ctk.CTkScrollableFrame(lat2)
        self.frame_camadas.grid(row=1, column=0, sticky="nsew", padx=6)
        self.frame_camadas.grid_columnconfigure(0, weight=1)
        bot = ctk.CTkFrame(lat2, fg_color="transparent")
        bot.grid(row=2, column=0, sticky="ew", padx=6, pady=8)
        bot.grid_columnconfigure((0, 1), weight=1)
        for i, (txt, cmd) in enumerate([
                ("+ Camada", self.adicionar_camada), ("− Camada", self.remover_camada),
                ("▲ Subir", lambda: self.mover_camada(1)), ("▼ Descer", lambda: self.mover_camada(-1)),
                ("Renomear", self.renomear_camada), ("Duplicar", self.duplicar_camada)]):
            ctk.CTkButton(bot, text=txt, command=cmd, height=28).grid(
                row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")

        self.recarregar_lista()
        self._montar_camadas()

    # ---- história / lista -----------------------------------------------------------------

    def ao_trocar_historia(self, historia):
        self.doc = None
        self.camadas = []
        self.recarregar_lista()
        self._montar_camadas()
        self._limpar_tela()

    def recarregar_lista(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()
        for i, d in enumerate(self.lista("desenhos")):
            ctk.CTkButton(
                self.frame_lista, text=d["nome"], anchor="w",
                fg_color="#1f6aa5" if d is self.doc else "gray30",
                command=lambda x=d: self.abrir_desenho(x)
            ).grid(row=i, column=0, sticky="ew", pady=2)

    def _pasta(self, doc=None):
        return os.path.join(PASTA_DESENHOS, (doc or self.doc)["id"])

    def _arquivo(self, camada_id, doc=None):
        return os.path.join(self._pasta(doc), f"{camada_id}.png")

    # ---- criar / abrir / remover -----------------------------------------------------------

    def novo(self):
        def confirmar(v):
            nome = v["nome"]
            if not nome:
                return "Digite o nome do desenho."
            if any(d["nome"].casefold() == nome.casefold() for d in self.lista("desenhos")):
                return "Já existe um desenho com esse nome."
            try:
                larg, alt = int(v["largura"]), int(v["altura"])
            except ValueError:
                return "Largura e altura precisam ser números inteiros."
            if not (16 <= larg <= 4000 and 16 <= alt <= 4000):
                return "Largura e altura devem estar entre 16 e 4000 pixels."

            doc = novo_desenho(nome, larg, alt)
            fundo = {"id": str(uuid.uuid4()), "nome": "Fundo", "visivel": True}
            c1 = {"id": str(uuid.uuid4()), "nome": "Camada 1", "visivel": True}
            doc["camadas"] = [fundo, c1]
            doc["ativa"] = 1
            os.makedirs(self._pasta(doc), exist_ok=True)
            Image.new("RGBA", (larg, alt), (255, 255, 255, 255)).save(self._arquivo(fundo["id"], doc))
            Image.new("RGBA", (larg, alt), TRANSPARENTE).save(self._arquivo(c1["id"], doc))
            self.lista("desenhos").append(doc)
            historias.atualizar(backup=False)
            self.abrir_desenho(doc)

        self.pedir_campos("Novo desenho", [
            {"chave": "nome", "rotulo": "Nome:", "tipo": "entry"},
            {"chave": "largura", "rotulo": "Largura (px):", "tipo": "entry", "valor": "800"},
            {"chave": "altura", "rotulo": "Altura (px):", "tipo": "entry", "valor": "600"},
        ], confirmar, texto_ok="Criar")

    def abrir_desenho(self, doc):
        self.doc = doc
        self.camadas = []
        for meta in doc["camadas"]:
            caminho = self._arquivo(meta["id"])
            if os.path.exists(caminho):
                img = Image.open(caminho).convert("RGBA")
                if img.size != (doc["largura"], doc["altura"]):
                    img = img.resize((doc["largura"], doc["altura"]))
            else:
                img = Image.new("RGBA", (doc["largura"], doc["altura"]), TRANSPARENTE)
            self.camadas.append({**meta, "img": img})
        self.ativa = min(doc.get("ativa", len(self.camadas) - 1), len(self.camadas) - 1)
        self._xadrez = _xadrez((doc["largura"], doc["altura"]))
        self._sujas = set()

        self.historico.reiniciar(self._estado())
        self.recarregar_lista()
        self._montar_camadas()
        self._preparar_tela()
        self._atualizar_tela()
        self._status()

    def remover(self):
        if self.doc is None:
            return
        if not messagebox.askyesno("Remover", f'Remover o desenho "{self.doc["nome"]}"?', parent=self.tl):
            return
        shutil.rmtree(self._pasta(), ignore_errors=True)
        self.lista("desenhos").remove(self.doc)
        historias.atualizar(backup=False)
        self.doc = None
        self.camadas = []
        self.recarregar_lista()
        self._montar_camadas()
        self._limpar_tela()

    # ---- estado, desfazer e salvamento automático --------------------------------------------------

    def _estado(self):
        return {"meta": [(c["id"], c["nome"], c["visivel"]) for c in self.camadas],
                "imgs": [c["img"] for c in self.camadas], "ativa": self.ativa}

    def _restaurar(self, estado):
        self.camadas = [{"id": m[0], "nome": m[1], "visivel": m[2], "img": img}
                        for m, img in zip(estado["meta"], estado["imgs"])]
        self.ativa = estado["ativa"]
        self._sujas = {c["id"] for c in self.camadas}
        self._salvar()
        self._montar_camadas()
        self._atualizar_tela()

    def desfazer(self):
        if self.doc is None:
            return
        estado = self.historico.desfazer()
        if estado is not None:
            self._restaurar(estado)
            self._status("Desfeito")

    def refazer(self):
        if self.doc is None:
            return
        estado = self.historico.refazer()
        if estado is not None:
            self._restaurar(estado)
            self._status("Refeito")

    def _fim_acao(self, camada_alterada=True):
        """Fim de uma ação: registra para desfazer e SALVA automaticamente."""
        if self.doc is None:
            return
        if camada_alterada and self.camadas:
            self._sujas.add(self.camadas[self.ativa]["id"])
        self.historico.registrar(self._estado())
        self._salvar()

    def _salvar(self):
        doc = self.doc
        if doc is None:
            return
        os.makedirs(self._pasta(), exist_ok=True)
        for c in self.camadas:
            if c["id"] in self._sujas or not os.path.exists(self._arquivo(c["id"])):
                c["img"].save(self._arquivo(c["id"]))
        ids = {c["id"] for c in self.camadas}
        for nome in os.listdir(self._pasta()):               # camadas apagadas
            if nome.endswith(".png") and nome[:-4] not in ids:
                os.remove(os.path.join(self._pasta(), nome))
        self._sujas.clear()
        doc["camadas"] = [{"id": c["id"], "nome": c["nome"], "visivel": c["visivel"]}
                          for c in self.camadas]
        doc["ativa"] = self.ativa
        historias.atualizar(backup=False)
        self._status("Salvo automaticamente")

    def _status(self, extra=""):
        if self.doc is None:
            self.lbl_status.configure(text="Crie ou selecione um desenho.")
            return
        c = self.camadas[self.ativa]["nome"] if self.camadas else "—"
        self.lbl_status.configure(
            text=f'{self.doc["nome"]} · {self.doc["largura"]}×{self.doc["altura"]} px · '
                 f'camada ativa: {c}' + (f"  ·  {extra}" if extra else ""))

    # ---- tela ---------------------------------------------------------------------------------------

    def _limpar_tela(self):
        self.tela.delete("all")
        self._item_img = None
        self._status()

    def _preparar_tela(self):
        self.tela.delete("all")
        self.tela.configure(scrollregion=(0, 0, self.doc["largura"], self.doc["altura"]))
        self._item_img = self.tela.create_image(0, 0, anchor="nw")

    def _compor(self, fundo_xadrez=True):
        base = (self._xadrez or _xadrez((self.doc["largura"], self.doc["altura"]))).copy() \
            if fundo_xadrez else Image.new("RGBA", (self.doc["largura"], self.doc["altura"]), TRANSPARENTE)
        for c in self.camadas:
            if c["visivel"]:
                base = Image.alpha_composite(base, c["img"])
        return base

    def _atualizar_tela(self):
        if self.doc is None or self._item_img is None:
            return
        self._tk_img = ImageTk.PhotoImage(self._compor())
        self.tela.itemconfigure(self._item_img, image=self._tk_img)

    def _agendar_tela(self):
        if not self._agendado:
            self._agendado = True
            self.tela.after(16, self._executar_agendado)

    def _executar_agendado(self):
        self._agendado = False
        self._atualizar_tela()

    # ---- cor ----------------------------------------------------------------------------------------

    def escolher_cor(self):
        inicial = "#%02x%02x%02x" % self.cor[:3]
        escolhida = colorchooser.askcolor(color=inicial, parent=self.tl, title="Escolher cor")
        if escolhida and escolhida[0]:
            self._definir_cor(tuple(int(v) for v in escolhida[0]) + (255,))

    def _definir_cor(self, rgba):
        self.cor = rgba
        hexa = "#%02x%02x%02x" % rgba[:3]
        claro = sum(rgba[:3]) > 380
        self.btn_cor.configure(fg_color=hexa, text_color="#000000" if claro else "#ffffff")

    # ---- mouse ----------------------------------------------------------------------------------------

    def _ponto(self, event):
        return int(self.tela.canvasx(event.x)), int(self.tela.canvasy(event.y))

    def _tamanho(self):
        return max(1, int(self.slider_tam.get()))

    def _dentro(self, p):
        return 0 <= p[0] < self.doc["largura"] and 0 <= p[1] < self.doc["altura"]

    @staticmethod
    def _carimbo(draw, a, b, cor, t):
        r = t / 2
        draw.line([a, b], fill=cor, width=t)
        draw.ellipse([b[0] - r, b[1] - r, b[0] + r, b[1] + r], fill=cor)

    def _pressionar(self, event):
        if self.doc is None or not self.camadas:
            return
        p = self._ponto(event)
        f = self.ferramenta.get()
        camada = self.camadas[self.ativa]
        self._acao_em_curso = True

        if f in (FERRAMENTAS[0], FERRAMENTAS[1]):
            cor = self.cor if f == FERRAMENTAS[0] else TRANSPARENTE
            self._desenho = ImageDraw.Draw(camada["img"])
            self._carimbo(self._desenho, p, p, cor, self._tamanho())
            self._ultimo = p
            self._agendar_tela()
        elif f == FERRAMENTAS[2]:                                   # balde
            if self._dentro(p):
                ImageDraw.floodfill(camada["img"], p, self.cor, thresh=int(self.slider_tol.get()))
                self._atualizar_tela()
            self._acao_em_curso = False
            self._fim_acao()
        elif f == FERRAMENTAS[6]:                                   # conta-gotas
            if self._dentro(p):
                r, g, b, a = self._compor(fundo_xadrez=False).getpixel(p)
                if a:
                    self._definir_cor((r, g, b, 255))
            self._acao_em_curso = False
        else:                                                       # formas
            self._inicio = p

    def _mover(self, event):
        if not self._acao_em_curso:
            return
        p = self._ponto(event)
        f = self.ferramenta.get()
        if f in (FERRAMENTAS[0], FERRAMENTAS[1]) and self._desenho is not None:
            cor = self.cor if f == FERRAMENTAS[0] else TRANSPARENTE
            self._carimbo(self._desenho, self._ultimo, p, cor, self._tamanho())
            self._ultimo = p
            self._agendar_tela()
        elif self._inicio is not None:
            if self._forma_item is not None:
                self.tela.delete(self._forma_item)
            x0, y0 = self._inicio
            cor = "#%02x%02x%02x" % self.cor[:3]
            kw = dict(outline=cor, width=self._tamanho(), fill=cor if self.var_preencher.get() else "")
            if f == FERRAMENTAS[3]:
                self._forma_item = self.tela.create_line(x0, y0, p[0], p[1], fill=cor,
                                                         width=self._tamanho(), capstyle="round")
            elif f == FERRAMENTAS[4]:
                self._forma_item = self.tela.create_rectangle(x0, y0, p[0], p[1], **kw)
            else:
                self._forma_item = self.tela.create_oval(x0, y0, p[0], p[1], **kw)

    def _soltar(self, event):
        if not self._acao_em_curso:
            return
        self._acao_em_curso = False
        f = self.ferramenta.get()
        p = self._ponto(event)

        if f in (FERRAMENTAS[0], FERRAMENTAS[1]):
            self._desenho = None
            self._ultimo = None
            self._atualizar_tela()
            self._fim_acao()
        elif self._inicio is not None:
            if self._forma_item is not None:
                self.tela.delete(self._forma_item)
                self._forma_item = None
            camada = self.camadas[self.ativa]
            d = ImageDraw.Draw(camada["img"])
            x0, y0 = self._inicio
            t = self._tamanho()
            preenchido = self.var_preencher.get()
            if f == FERRAMENTAS[3]:
                self._carimbo(d, (x0, y0), p, self.cor, t)
                d.ellipse([x0 - t / 2, y0 - t / 2, x0 + t / 2, y0 + t / 2], fill=self.cor)
            else:
                caixa = [min(x0, p[0]), min(y0, p[1]), max(x0, p[0]), max(y0, p[1])]
                desenhar = d.rectangle if f == FERRAMENTAS[4] else d.ellipse
                desenhar(caixa, outline=self.cor, width=t, fill=self.cor if preenchido else None)
            self._inicio = None
            self._atualizar_tela()
            self._fim_acao()

    # ---- camadas -----------------------------------------------------------------------------------------

    def _montar_camadas(self):
        for w in self.frame_camadas.winfo_children():
            w.destroy()
        # topo da lista = camada mais acima
        for pos, idx in enumerate(reversed(range(len(self.camadas)))):
            c = self.camadas[idx]
            linha = ctk.CTkFrame(self.frame_camadas, fg_color="transparent")
            linha.grid(row=pos, column=0, sticky="ew", pady=1)
            linha.grid_columnconfigure(1, weight=1)
            var = ctk.BooleanVar(value=c["visivel"])
            ctk.CTkCheckBox(linha, text="", width=24, variable=var,
                            command=lambda i=idx, v=var: self._alternar_visivel(i, v.get())
                            ).grid(row=0, column=0)
            ctk.CTkButton(linha, text=c["nome"], anchor="w", height=28,
                          fg_color="#1f6aa5" if idx == self.ativa else "gray30",
                          command=lambda i=idx: self._selecionar_camada(i)
                          ).grid(row=0, column=1, sticky="ew")

    def _selecionar_camada(self, i):
        self.ativa = i
        self._montar_camadas()
        self._status()

    def _alternar_visivel(self, i, valor):
        self.camadas[i]["visivel"] = bool(valor)
        self._atualizar_tela()
        self._fim_acao(camada_alterada=False)

    def _nova_id(self):
        return str(uuid.uuid4())

    def adicionar_camada(self):
        if self.doc is None:
            return
        img = Image.new("RGBA", (self.doc["largura"], self.doc["altura"]), TRANSPARENTE)
        nome = f"Camada {len(self.camadas)}"
        self.camadas.insert(self.ativa + 1, {"id": self._nova_id(), "nome": nome,
                                             "visivel": True, "img": img})
        self.ativa += 1
        self._sujas.add(self.camadas[self.ativa]["id"])
        self._montar_camadas()
        self._fim_acao(camada_alterada=False)

    def remover_camada(self):
        if self.doc is None or len(self.camadas) <= 1:
            return
        self.camadas.pop(self.ativa)
        self.ativa = max(0, min(self.ativa, len(self.camadas) - 1))
        self._montar_camadas()
        self._atualizar_tela()
        self._fim_acao(camada_alterada=False)

    def mover_camada(self, delta):
        i, j = self.ativa, self.ativa + delta
        if self.doc is None or not (0 <= j < len(self.camadas)):
            return
        self.camadas[i], self.camadas[j] = self.camadas[j], self.camadas[i]
        self.ativa = j
        self._montar_camadas()
        self._atualizar_tela()
        self._fim_acao(camada_alterada=False)

    def duplicar_camada(self):
        if self.doc is None:
            return
        c = self.camadas[self.ativa]
        nova = {"id": self._nova_id(), "nome": c["nome"] + " cópia", "visivel": True,
                "img": c["img"].copy()}
        self.camadas.insert(self.ativa + 1, nova)
        self.ativa += 1
        self._sujas.add(nova["id"])
        self._montar_camadas()
        self._atualizar_tela()
        self._fim_acao(camada_alterada=False)

    def renomear_camada(self):
        if self.doc is None:
            return

        def confirmar(v):
            if not v["nome"]:
                return "Digite um nome."
            self.camadas[self.ativa]["nome"] = v["nome"]
            self._montar_camadas()
            self._fim_acao(camada_alterada=False)

        self.pedir_campos("Renomear camada", [
            {"chave": "nome", "rotulo": "Nome:", "tipo": "entry",
             "valor": self.camadas[self.ativa]["nome"]}], confirmar, texto_ok="Renomear")

    # ---- exportar (com visualização) ---------------------------------------------------------------------

    def _codificar(self, imagem, formato, qualidade):
        buf = io.BytesIO()
        if formato == "png":
            imagem.save(buf, "PNG")
        elif formato in ("jpeg", "jpg"):
            fundo = Image.new("RGB", imagem.size, (255, 255, 255))
            fundo.paste(imagem, mask=imagem.getchannel("A"))
            fundo.save(buf, "JPEG", quality=qualidade)
        else:
            imagem.save(buf, "WEBP", quality=qualidade)
        return buf.getvalue()

    def exportar(self):
        if self.doc is None:
            messagebox.showinfo("Exportar", "Abra um desenho primeiro.", parent=self.tl)
            return

        self.fechar_overlay()
        plana = self._compor(fundo_xadrez=False)

        ov = ctk.CTkFrame(self.tl, corner_radius=12, border_width=2)
        ov.place(relx=0.5, rely=0.5, anchor="center")
        ov.lift()
        self.overlay = ov

        ctk.CTkLabel(ov, text="Exportar desenho", font=("Helvetica", 20, "bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        moldura = ctk.CTkLabel(ov, text="", width=440, height=330)
        moldura.grid(row=1, column=0, columnspan=2, padx=20, pady=6)
        info = ctk.CTkLabel(ov, text="", anchor="w")
        info.grid(row=2, column=0, columnspan=2, padx=20, sticky="ew")

        ctk.CTkLabel(ov, text="Formato").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        ctk.CTkLabel(ov, text="Qualidade (jpeg/jpg/webp)").grid(
            row=3, column=1, padx=20, pady=(10, 0), sticky="w")
        menu = ctk.CTkOptionMenu(ov, values=FORMATOS)
        menu.grid(row=4, column=0, padx=20, sticky="ew")
        slider = ctk.CTkSlider(ov, from_=1, to=100, number_of_steps=99)
        slider.set(90)
        slider.grid(row=4, column=1, padx=20, sticky="ew")

        estado = {"dados": b"", "img": None}

        def atualizar(*_):
            formato = menu.get()
            slider.configure(state="disabled" if formato == "png" else "normal")
            dados = self._codificar(plana, formato, int(slider.get()))
            estado["dados"] = dados
            resultado = Image.open(io.BytesIO(dados)).convert("RGBA")
            vista = resultado.copy()
            vista.thumbnail((440, 330))
            fundo = _xadrez(vista.size, 8)
            fundo = Image.alpha_composite(fundo, vista)
            estado["img"] = ctk.CTkImage(light_image=fundo, dark_image=fundo, size=fundo.size)
            moldura.configure(image=estado["img"])
            info.configure(text=f"{formato.upper()} · {plana.width}×{plana.height} px · "
                                f"{len(dados) / 1024:.1f} KB")

        menu.configure(command=atualizar)
        slider.configure(command=atualizar)

        def exportar_agora():
            formato = menu.get()
            caminho = filedialog.asksaveasfilename(
                parent=self.tl, title="Exportar", initialfile=self.doc["nome"],
                defaultextension=f".{formato}",
                filetypes=[(formato.upper(), f"*.{formato}")])
            if not caminho:
                return
            if not caminho.lower().endswith(f".{formato}"):
                caminho += f".{formato}"
            with open(caminho, "wb") as f:
                f.write(estado["dados"])
            self.fechar_overlay()
            messagebox.showinfo("Exportar", f"Desenho exportado:\n{caminho}", parent=self.tl)

        botoes = ctk.CTkFrame(ov, fg_color="transparent")
        botoes.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=15)
        botoes.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(botoes, text="Cancelar", fg_color="gray30", hover_color="gray40",
                      command=self.fechar_overlay).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(botoes, text="Exportar…", command=exportar_agora).grid(
            row=0, column=1, padx=(5, 0), sticky="ew")

        atualizar()
