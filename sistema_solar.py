import copy
import math
import random
import time
import uuid

import customtkinter as ctk

from tkinter import messagebox

import historias
from calendario import dias_do_ano
from mural import JanelaFerramenta
from modelos import novo_sistema_solar, novo_planeta
from undo import HistoricoDesfazer

TAMANHOS = ["Minúsculo", "Pequeno", "Médio", "Grande", "Gigante"]
SEM_ESPECIE = "(nenhuma)"
SEM_CALENDARIO = "(nenhum — informar manualmente)"
ZOOM_SISTEMA_ENTRADA = 120.0     # px por ano-luz ao "mergulhar" em um sistema
RAIO_CLIQUE_SISTEMA = 16
FATOR_MINIMO = 0.05


def _hex_valido(txt):
    if len(txt) != 7 or txt[0] != "#":
        return False
    try:
        int(txt[1:], 16)
        return True
    except ValueError:
        return False


def _num(txt):
    try:
        return float(str(txt).strip().replace(",", "."))
    except ValueError:
        return None


def _lerp(a, b, t):
    return a + (b - a) * t


class SistemaSolarJanela(JanelaFerramenta):
    titulo = "🪐 Sistemas Solares"
    geometria = "1500x850"
    tamanho_minimo = (1100, 650)

    # =====================================================================
    # DADOS
    # =====================================================================

    def sistemas(self):
        return self.lista("sistemas_solares")

    def planetas(self):
        return self.lista("planetas")

    def especies(self):
        return self.historia().setdefault("especies", [])

    def calendarios(self):
        return self.historia().setdefault("calendarios", [])

    def _sistema(self, sid):
        return next((s for s in self.sistemas() if s["id"] == sid), None)

    def _planeta(self, pid):
        return next((p for p in self.planetas() if p["id"] == pid), None) if pid else None

    def _especie(self, eid):
        return next((e for e in self.especies() if e["id"] == eid), None) if eid else None

    def _calendario(self, cid):
        return next((c for c in self.calendarios() if c["id"] == cid), None) if cid else None

    def _orbita_do_planeta(self, planeta):
        for s in self.sistemas():
            for o in s["orbitas"]:
                if o["planeta_id"] == planeta["id"]:
                    return s, o
        return None, None

    def _calendario_da_especie(self, planeta):
        esp = self._especie(planeta.get("especie_id"))
        return self._calendario(esp.get("calendario_id")) if esp else None

    def info_tempo(self, planeta):
        """(dias_por_ano, horas_por_dia, origem). Herda do calendário da espécie, se houver."""
        cal = self._calendario_da_especie(planeta)
        if cal is not None:
            return (dias_do_ano(cal, cal["ano_inicial"]), float(cal.get("horas_dia", 24)),
                    f'calendário "{cal["nome"]}" (herdado da espécie)')
        return float(planeta.get("dias_ano", 365)), float(planeta.get("horas_dia", 24)), "informado manualmente"

    def periodo_dias(self, planeta):
        """Período orbital em dias de 24 h, usado na animação."""
        dias, horas, _ = self.info_tempo(planeta)
        return max(0.01, dias * horas / 24.0)

    def _estado(self):
        return {
            "sistemas": self.sistemas(), "planetas": self.planetas(),
            "calendarios_especies": {e["id"]: e.get("calendario_id", "") for e in self.especies()},
        }

    def _restaurar(self, estado):
        self.sistemas()[:] = estado["sistemas"]
        self.planetas()[:] = estado["planetas"]
        for e in self.especies():
            vinculo = estado["calendarios_especies"].get(e["id"], "")
            if vinculo:
                e["calendario_id"] = vinculo
            else:
                e.pop("calendario_id", None)
        if self.sistema_id and not self._sistema(self.sistema_id):
            self.modo, self.sistema_id = "galaxia", None
        self._validar_selecao()
        historias.atualizar(backup=False)
        self._atualizar_tudo()

    def _fim_acao(self):
        self.historico.registrar(self._estado())
        historias.atualizar(backup=False)
        self._atualizar_tudo()

    def desfazer(self):
        if self.animando:
            return
        e = self.historico.desfazer()
        if e is not None:
            self._restaurar(e)

    def refazer(self):
        if self.animando:
            return
        e = self.historico.refazer()
        if e is not None:
            self._restaurar(e)

    def _validar_selecao(self):
        if self.sel is None:
            return
        tipo, ident = self.sel
        ok = False
        if tipo == "sistema":
            ok = self._sistema(ident) is not None
        elif tipo == "planeta":
            ok = self._planeta(ident) is not None
        elif tipo == "orbita":
            s = self._sistema(self.sistema_id)
            ok = bool(s) and any(o["id"] == ident for o in s["orbitas"])
        if not ok:
            self.sel = None

    # =====================================================================
    # CONSTRUÇÃO DA JANELA
    # =====================================================================

    def construir(self, tl):
        self.modo = "galaxia"
        self.sistema_id = None
        self.sel = None
        self.cam = [0.0, 0.0]
        self.zoom = 40.0                # px por ano-luz (galáxia)
        self.zoom_galaxia = 40.0
        self.zoom_sis = 1.0
        self.fator = 1.0                # escala usada nas transições
        self.t_dias = 0.0
        self.tocando = True
        self.vel = 30.0                 # dias simulados por segundo
        self.animando = False
        self.arrasto = None
        self._pan = None
        self._flutuante = None
        self._ultimo_tick = time.monotonic()
        self.historico = HistoricoDesfazer(limite=60)
        rnd = random.Random(7)
        self.fundo_estrelas = [(rnd.random(), rnd.random(), rnd.choice([1, 1, 1, 2])) for _ in range(140)]

        tl.grid_columnconfigure(1, weight=1)
        tl.grid_rowconfigure(0, weight=1)

        # ---- esquerda: sistemas -------------------------------------------------
        esq = ctk.CTkFrame(tl, width=250)
        esq.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        esq.grid_propagate(False)
        esq.grid_rowconfigure(2, weight=1)
        esq.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(esq, text="🌌 Sistemas solares", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=(8, 0))
        self.lbl_ref = ctk.CTkLabel(esq, text="", text_color="gray65", wraplength=230)
        self.lbl_ref.grid(row=1, column=0, pady=(0, 4))
        self.frame_sistemas = ctk.CTkScrollableFrame(esq)
        self.frame_sistemas.grid(row=2, column=0, sticky="nsew", padx=6)
        self.frame_sistemas.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(esq, text="+ Sistema solar", command=self.novo_sistema).grid(
            row=3, column=0, padx=8, pady=(8, 4), sticky="ew")
        ctk.CTkButton(esq, text="🗑 Remover sistema", fg_color="#8b2e2e", hover_color="#a33a3a",
                      command=self.remover_sistema).grid(row=4, column=0, padx=8, pady=(0, 10), sticky="ew")

        # ---- centro --------------------------------------------------------------
        centro = ctk.CTkFrame(tl, fg_color="transparent")
        centro.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        centro.grid_columnconfigure(0, weight=1)
        centro.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(centro)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        for txt, cmd in (("🌌 Galáxia", self.ver_galaxia), ("+ Órbita", self.adicionar_orbita),
                         ("− Órbita", self.remover_orbita), ("✏️ Editar seleção", self.editar_selecao)):
            ctk.CTkButton(barra, text=txt, width=110, command=cmd).pack(side="left", padx=4, pady=8)
        self.btn_play = ctk.CTkButton(barra, text="⏸", width=40, command=self.alternar_tempo)
        self.btn_play.pack(side="left", padx=(14, 4))
        ctk.CTkLabel(barra, text="Velocidade").pack(side="left", padx=(6, 2))
        self.slider_vel = ctk.CTkSlider(barra, from_=0, to=3.56, number_of_steps=100, width=150,
                                        command=self._mudar_velocidade)
        self.slider_vel.set(math.log10(self.vel))
        self.slider_vel.pack(side="left", padx=4)
        self.lbl_vel = ctk.CTkLabel(barra, text="30 dias/s", width=80)
        self.lbl_vel.pack(side="left")
        ctk.CTkButton(barra, text="↶", width=34, command=self.desfazer).pack(side="left", padx=(12, 2))
        ctk.CTkButton(barra, text="↷", width=34, command=self.refazer).pack(side="left", padx=2)

        self.tela = ctk.CTkCanvas(centro, bg="#05070d", highlightthickness=0)
        self.tela.grid(row=1, column=0, sticky="nsew")
        self.tela.bind("<ButtonPress-1>", self._pressionar)
        self.tela.bind("<B1-Motion>", self._mover)
        self.tela.bind("<ButtonRelease-1>", self._soltar)
        self.tela.bind("<Double-Button-1>", self._duplo_clique)
        self.tela.bind("<MouseWheel>", self._roda)
        self.tela.bind("<Button-4>", lambda e: self._roda(e, 1))
        self.tela.bind("<Button-5>", lambda e: self._roda(e, -1))
        self.tela.bind("<Configure>", lambda e: self._desenhar())

        self.lbl_status = ctk.CTkLabel(centro, anchor="w", text_color="gray70")
        self.lbl_status.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        # ---- direita: armazenamento + informações -----------------------------------
        self.dir = ctk.CTkFrame(tl, width=310)
        self.dir.grid(row=0, column=2, sticky="ns", padx=(5, 10), pady=10)
        self.dir.grid_propagate(False)
        self.dir.grid_rowconfigure(1, weight=1)
        self.dir.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.dir, text="🪐 Armazenamento de planetas",
                     font=("Helvetica", 15, "bold")).grid(row=0, column=0, pady=(8, 2))
        self.frame_planetas = ctk.CTkScrollableFrame(self.dir)
        self.frame_planetas.grid(row=1, column=0, sticky="nsew", padx=6)
        self.frame_planetas.grid_columnconfigure(0, weight=1)
        bot = ctk.CTkFrame(self.dir, fg_color="transparent")
        bot.grid(row=2, column=0, sticky="ew", padx=6, pady=6)
        bot.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(bot, text="+ Planeta", command=lambda: self.editar_planeta(None)).grid(
            row=0, column=0, padx=2, sticky="ew")
        ctk.CTkButton(bot, text="🗑 Remover", fg_color="#8b2e2e", hover_color="#a33a3a",
                      command=self.remover_planeta).grid(row=0, column=1, padx=2, sticky="ew")
        ctk.CTkLabel(self.dir, text="Informações", font=("Helvetica", 14, "bold")).grid(row=3, column=0)
        self.lbl_info = ctk.CTkLabel(self.dir, text="", anchor="nw", justify="left", wraplength=285, height=230)
        self.lbl_info.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

        self._tick()

    def ao_trocar_historia(self, historia):
        self.modo, self.sistema_id, self.sel = "galaxia", None, None
        self.t_dias = 0.0
        self.fator = 1.0
        self.zoom = self.zoom_galaxia
        sis = self.sistemas()
        self.cam = [sum(s["x"] for s in sis) / len(sis), sum(s["y"] for s in sis) / len(sis)] if sis else [0.0, 0.0]
        self.historico.reiniciar(self._estado())
        self._atualizar_tudo()

    def ao_fechar(self):
        self._cancelar_flutuante()

    # =====================================================================
    # PAINÉIS
    # =====================================================================

    def _atualizar_tudo(self):
        self._recarregar_sistemas()
        self._recarregar_planetas()
        self._atualizar_info()
        self._desenhar()

    def _sistema_referencia(self):
        if self.modo == "sistema":
            return self._sistema(self.sistema_id)
        if self.sel and self.sel[0] == "sistema":
            return self._sistema(self.sel[1])
        return None

    def _distancia(self, a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    def _recarregar_sistemas(self):
        for w in self.frame_sistemas.winfo_children():
            w.destroy()
        ref = self._sistema_referencia()
        self.lbl_ref.configure(text=f"Distâncias a partir de {ref['nome']}" if ref else "")
        lista = sorted(self.sistemas(), key=lambda s: (self._distancia(ref, s) if ref else 0, s["nome"].casefold()))
        if not lista:
            ctk.CTkLabel(self.frame_sistemas, text="Nenhum sistema ainda.\nClique em “+ Sistema solar”.",
                         justify="center").grid(row=0, column=0, pady=30)
        for i, s in enumerate(lista):
            linha = ctk.CTkFrame(self.frame_sistemas, fg_color="transparent")
            linha.grid(row=i, column=0, sticky="ew", pady=2)
            linha.grid_columnconfigure(0, weight=1)
            atual = (self.modo == "sistema" and s["id"] == self.sistema_id)
            texto = s["nome"] + (f"\n{self._distancia(ref, s):.1f} anos-luz" if ref and s is not ref else "")
            ctk.CTkButton(linha, text=texto, anchor="w", height=40,
                          fg_color="#1f6aa5" if atual or (self.sel == ("sistema", s["id"])) else "gray30",
                          command=lambda x=s: self._selecionar("sistema", x["id"])
                          ).grid(row=0, column=0, sticky="ew")
            ctk.CTkButton(linha, text="Ir ➜", width=48, height=40,
                          command=lambda x=s: self.ir_para_sistema(x["id"])).grid(row=0, column=1, padx=(3, 0))

    def _recarregar_planetas(self):
        for w in self.frame_planetas.winfo_children():
            w.destroy()
        planetas = self.planetas()
        if not planetas:
            ctk.CTkLabel(self.frame_planetas, text="Nenhum planeta.\nClique em “+ Planeta”.",
                         justify="center").grid(row=0, column=0, pady=30)
        for i, p in enumerate(planetas):
            s, o = self._orbita_do_planeta(p)
            onde = (f"em {s['nome']}" if s else "livre") + (f" · {p.get('luas', 0)} lua(s)" if p.get("luas") else "")
            linha = ctk.CTkFrame(self.frame_planetas, border_width=2,
                                 border_color="#1f6aa5" if self.sel == ("planeta", p["id"]) else "gray25")
            linha.grid(row=i, column=0, sticky="ew", pady=2)
            linha.grid_columnconfigure(1, weight=1)
            bolinha = ctk.CTkLabel(linha, text="●", text_color=p["cor"], font=("Helvetica", 22), width=30)
            bolinha.grid(row=0, column=0, rowspan=2, padx=4)
            nome = ctk.CTkLabel(linha, text=p["nome"], anchor="w", font=("Helvetica", 13, "bold"))
            nome.grid(row=0, column=1, sticky="ew")
            status = ctk.CTkLabel(linha, text=onde, anchor="w", text_color="gray65")
            status.grid(row=1, column=1, sticky="ew")
            for w in (linha, bolinha, nome, status):
                w.bind("<ButtonPress-1>", lambda e, pid=p["id"]: self._iniciar_arrasto_lista(e, pid))
                w.bind("<B1-Motion>", self._mover_arrasto_lista)
                w.bind("<ButtonRelease-1>", self._soltar_arrasto_lista)

    def _selecionar(self, tipo, ident):
        self.sel = (tipo, ident)
        self._atualizar_tudo()

    def _atualizar_info(self):
        self._validar_selecao()
        if self.modo == "galaxia":
            dica = "Arraste os sistemas para posicioná-los · arraste o fundo para mover · roda do mouse = zoom · duplo clique = entrar"
        else:
            dica = "Arraste planetas do armazenamento para as órbitas · arraste um planeta entre órbitas · solte-o no armazenamento para retirá-lo"
        self.lbl_status.configure(text=dica)

        if self.sel is None:
            self.lbl_info.configure(text="Clique em um sistema, planeta ou órbita para ver os detalhes.")
            return
        tipo, ident = self.sel
        if tipo == "sistema":
            s = self._sistema(ident)
            outros = [self._distancia(s, o) for o in self.sistemas() if o is not s]
            txt = (f"SISTEMA {s['nome']}\nEstrela: {s['estrela']['nome']}\n"
                   f"Tamanho da estrela: {s['estrela']['tamanho']:g}× o Sol\n"
                   f"Órbitas: {len(s['orbitas'])} · planetas: {sum(1 for o in s['orbitas'] if o['planeta_id'])}\n"
                   f"Posição: ({s['x']:.1f}, {s['y']:.1f}) anos-luz")
            if outros:
                txt += f"\nSistema mais próximo: {min(outros):.1f} anos-luz"
        elif tipo == "orbita":
            s = self._sistema(self.sistema_id)
            o = next(x for x in s["orbitas"] if x["id"] == ident)
            p = self._planeta(o["planeta_id"])
            txt = f"ÓRBITA\nDistância da estrela: {o['raio']:g} UA\nPlaneta: {p['nome'] if p else '(vazia)'}"
        else:
            p = self._planeta(ident)
            dias, horas, origem = self.info_tempo(p)
            esp = self._especie(p.get("especie_id"))
            s, o = self._orbita_do_planeta(p)
            txt = (f"PLANETA {p['nome']}\nTamanho: {p['tamanho']}\nDiâmetro: {p['diametro_km']:,.0f} km\n"
                   f"Peso: {p['peso'] or '—'}\nLuas: {p.get('luas', 0)}\n"
                   f"Estações: {'Sim' if p['estacoes'] else 'Não'}\n"
                   f"Espécie: {esp['nome'] if esp else '—'}\n"
                   f"Ano: {dias:g} dias · dia: {horas:g} h\n({origem})\n"
                   f"Local: {(s['nome'] + ', órbita ' + format(o['raio'], 'g') + ' UA') if s else 'no armazenamento'}")
        self.lbl_info.configure(text=txt)

    # =====================================================================
    # TEMPO / ANIMAÇÃO
    # =====================================================================

    def _mudar_velocidade(self, v):
        self.vel = 10 ** float(v)
        self.lbl_vel.configure(text=f"{self.vel:.0f} dias/s")

    def alternar_tempo(self):
        self.tocando = not self.tocando
        self.btn_play.configure(text="⏸" if self.tocando else "▶")

    def _tick(self):
        agora = time.monotonic()
        dt = agora - self._ultimo_tick
        self._ultimo_tick = agora
        try:
            if self.tl.winfo_exists():
                if self.tl.winfo_viewable() and self.tocando and self.modo == "sistema" and not self.animando:
                    self.t_dias += dt * self.vel
                    self._desenhar()
                self.tl.after(33, self._tick)
        except Exception:
            pass

    def _animar(self, ms, passo, fim=None):
        self.animando = True
        t0 = time.monotonic()

        def quadro():
            f = min(1.0, (time.monotonic() - t0) * 1000.0 / ms)
            passo(f * f * (3 - 2 * f))
            self._desenhar()
            if f < 1.0:
                self.tela.after(16, quadro)
            else:
                self.animando = False
                if fim:
                    fim()

        quadro()

    def ir_para_sistema(self, sid):
        """Viaja (animado) até o sistema solar: sai do atual, cruza a galáxia e mergulha no destino."""
        alvo = self._sistema(sid)
        if alvo is None or self.animando:
            return
        if self.modo == "sistema" and self.sistema_id == sid:
            return
        self.sel = ("sistema", sid)

        def entrar():
            self.sistema_id = sid
            self.modo = "sistema"
            self.fator = FATOR_MINIMO
            self.sel = None
            self._atualizar_tudo()
            self._animar(550, lambda e: setattr(self, "fator", _lerp(FATOR_MINIMO, 1.0, e)),
                         lambda: (setattr(self, "fator", 1.0), self._atualizar_tudo()))

        def viajar():
            self.modo = "galaxia"
            self.fator = 1.0
            origem, z0 = list(self.cam), self.zoom
            destino = (alvo["x"], alvo["y"])
            dist = math.hypot(destino[0] - origem[0], destino[1] - origem[1])

            def passo(e):
                self.cam = [_lerp(origem[0], destino[0], e), _lerp(origem[1], destino[1], e)]
                recuo = 1 - 0.7 * math.sin(math.pi * e) * min(1.0, dist / 3.0)
                self.zoom = _lerp(z0, ZOOM_SISTEMA_ENTRADA, e) * recuo

            self._animar(600 + min(1400, dist * 110), passo, entrar)

        if self.modo == "sistema":
            atual = self._sistema(self.sistema_id)

            def sair():
                self.modo = "galaxia"
                self.fator = 1.0
                if atual:
                    self.cam = [atual["x"], atual["y"]]
                self.zoom = ZOOM_SISTEMA_ENTRADA
                viajar()

            self._animar(450, lambda e: setattr(self, "fator", _lerp(1.0, FATOR_MINIMO, e)), sair)
        else:
            viajar()

    def ver_galaxia(self):
        if self.animando or self.modo == "galaxia":
            return
        atual = self._sistema(self.sistema_id)

        def sair():
            self.modo = "galaxia"
            self.fator = 1.0
            self.sel = ("sistema", atual["id"]) if atual else None
            if atual:
                self.cam = [atual["x"], atual["y"]]
            self.zoom = ZOOM_SISTEMA_ENTRADA
            self._atualizar_tudo()
            z_fim = self.zoom_galaxia
            self._animar(600, lambda e: setattr(self, "zoom", _lerp(ZOOM_SISTEMA_ENTRADA, z_fim, e)),
                         self._atualizar_tudo)

        self._animar(450, lambda e: setattr(self, "fator", _lerp(1.0, FATOR_MINIMO, e)), sair)

    # =====================================================================
    # DESENHO
    # =====================================================================

    def _tamanho_tela(self):
        w, h = self.tela.winfo_width(), self.tela.winfo_height()
        return (w if w > 10 else 800), (h if h > 10 else 600)

    def _desenhar(self):
        if self.tl is None or not self.tl.winfo_exists():
            return
        c = self.tela
        c.delete("all")
        w, h = self._tamanho_tela()
        for fx, fy, r in self.fundo_estrelas:
            c.create_oval(fx * w, fy * h, fx * w + r, fy * h + r, fill="#5b6478", outline="")
        if self.modo == "galaxia":
            self._desenhar_galaxia(w, h)
        else:
            self._desenhar_sistema(w, h)

    # ---- galáxia -----------------------------------------------------------------

    def _p_tela(self, s):
        w, h = self._tamanho_tela()
        return (w / 2 + (s["x"] - self.cam[0]) * self.zoom, h / 2 + (s["y"] - self.cam[1]) * self.zoom)

    def _desenhar_galaxia(self, w, h):
        c = self.tela
        sistemas = self.sistemas()
        sel = self._sistema(self.sel[1]) if self.sel and self.sel[0] == "sistema" else None

        if sel is not None:
            vizinhos = sorted((s for s in sistemas if s is not sel), key=lambda s: self._distancia(sel, s))[:8]
            x0, y0 = self._p_tela(sel)
            for s in vizinhos:
                x1, y1 = self._p_tela(s)
                c.create_line(x0, y0, x1, y1, fill="#3d6a99", dash=(5, 4))
                c.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 8, fill="#8fb8e0",
                              text=f"{self._distancia(sel, s):.1f} anos-luz", font=("Helvetica", 10))

        for s in sistemas:
            x, y = self._p_tela(s)
            if not (-60 < x < w + 60 and -60 < y < h + 60):
                continue
            cor = s["estrela"]["cor"]
            r = 5 + 3 * math.sqrt(max(0.1, s["estrela"]["tamanho"]))
            c.create_oval(x - r * 2, y - r * 2, x + r * 2, y + r * 2, fill="", outline=cor, width=1, stipple="gray50")
            c.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline="white" if s is sel else "")
            if s is sel:
                c.create_oval(x - r - 8, y - r - 8, x + r + 8, y + r + 8, outline="#ffffff", dash=(3, 3))
            c.create_text(x, y + r + 14, text=s["nome"], fill="#dfe8f5", font=("Helvetica", 11))

        if not sistemas:
            c.create_text(w / 2, h / 2, fill="gray70", justify="center", font=("Helvetica", 16),
                          text="A galáxia está vazia.\nCrie um sistema solar em “+ Sistema solar”.")

        # barra de escala
        alvo_px = 110
        ly = alvo_px / self.zoom
        passo = 10 ** math.floor(math.log10(ly))
        nice = min((m * passo for m in (1, 2, 5, 10) if m * passo <= ly * 1.4), default=passo, key=lambda v: -v)
        px = nice * self.zoom
        c.create_line(20, h - 22, 20 + px, h - 22, fill="#9bb7d4", width=2)
        c.create_text(20 + px / 2, h - 34, fill="#9bb7d4", text=f"{nice:g} ano(s)-luz")

    # ---- sistema ---------------------------------------------------------------------

    def _escala_sistema(self, s, w, h):
        maxr = max([o["raio"] for o in s["orbitas"]] + [1.0])
        return (min(w, h) / 2 * 0.88) / maxr * self.zoom_sis * self.fator

    def _posicao_planeta(self, s, o, p, w, h, escala):
        ang = math.radians(o["angulo0"] + 360.0 * self.t_dias / self.periodo_dias(p))
        return (w / 2 + math.cos(ang) * o["raio"] * escala, h / 2 + math.sin(ang) * o["raio"] * escala)

    @staticmethod
    def _raio_planeta(p, fator):
        r = 5 + 5 * math.log10(max(p["diametro_km"], 100) / 1000 + 1)
        return max(4, min(18, r)) * max(fator, 0.2)

    @staticmethod
    def _raio_estrela(s, fator):
        return (10 + 10 * math.sqrt(max(0.1, s["estrela"]["tamanho"]))) * max(fator, 0.2)

    def _desenhar_sistema(self, w, h):
        c = self.tela
        s = self._sistema(self.sistema_id)
        if s is None:
            return
        cx, cy = w / 2, h / 2
        escala = self._escala_sistema(s, w, h)
        f = self.fator

        c.create_text(16, 14, anchor="nw", fill="#dfe8f5", font=("Helvetica", 15, "bold"),
                      text=f"{s['nome']}  ·  {s['estrela']['nome']}")
        dia_txt = f"Dia {self.t_dias:,.0f}"
        c.create_text(w - 16, 14, anchor="ne", fill="#9bb7d4", text=dia_txt, font=("Helvetica", 12))

        sel_orb = self.sel[1] if self.sel and self.sel[0] == "orbita" else None
        sel_pla = self.sel[1] if self.sel and self.sel[0] == "planeta" else None

        for o in s["orbitas"]:
            r = o["raio"] * escala
            ativa = o["id"] == sel_orb
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#7fb2e5" if ativa else "#2a3a52",
                          width=2 if ativa else 1, dash=() if ativa else (3, 5))
            c.create_text(cx + r * 0.7071 + 4, cy - r * 0.7071 - 4, anchor="sw", fill="#4d6a8c",
                          text=f"{o['raio']:g} UA", font=("Helvetica", 9))

        # estrela (com brilho)
        re = self._raio_estrela(s, f)
        cor = s["estrela"]["cor"]
        for k, stp in ((2.2, "gray12"), (1.6, "gray25"), (1.25, "gray50")):
            c.create_oval(cx - re * k, cy - re * k, cx + re * k, cy + re * k, fill=cor, outline="", stipple=stp)
        c.create_oval(cx - re, cy - re, cx + re, cy + re, fill=cor, outline="white" if self.sel and self.sel[0] == "sistema" else "")

        for o in s["orbitas"]:
            p = self._planeta(o["planeta_id"])
            if p is None:
                continue
            if self.arrasto and self.arrasto.get("origem") == p["id"] and self.arrasto["tipo"] == "canvas":
                continue
            x, y = self._posicao_planeta(s, o, p, w, h, escala)
            rp = self._raio_planeta(p, f)
            c.create_oval(x - rp, y - rp, x + rp, y + rp, fill=p["cor"],
                          outline="white" if p["id"] == sel_pla else "#111111", width=2 if p["id"] == sel_pla else 1)
            luas = int(p.get("luas", 0))
            for k in range(min(luas, 6)):                      # até 6 luas desenhadas
                raio_lua = rp + 7 + 5 * k
                ang_lua = math.radians(self.t_dias * (40.0 / (k + 1)) + k * 70)
                lx, ly = x + math.cos(ang_lua) * raio_lua, y + math.sin(ang_lua) * raio_lua
                rl = max(1.5, 2.5 * max(f, 0.3))
                c.create_oval(lx - rl, ly - rl, lx + rl, ly + rl, fill="#c9ced6", outline="")
            if f > 0.5:
                c.create_text(x, y + rp + 11 + 5 * min(luas, 6), text=p["nome"], fill="#dfe8f5",
                              font=("Helvetica", 10))

        if self.arrasto and self.arrasto["tipo"] == "canvas":
            p = self._planeta(self.arrasto["origem"])
            x, y = self.arrasto["pos"]
            rp = self._raio_planeta(p, 1)
            c.create_oval(x - rp, y - rp, x + rp, y + rp, fill=p["cor"], outline="white", width=2)
            alvo = self._orbita_proxima(s, x, y, w, h)
            if alvo is not None:
                r = alvo["raio"] * escala
                c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#ffd54a", width=3)

    def _orbita_proxima(self, s, x, y, w, h, tolerancia=45):
        escala = self._escala_sistema(s, w, h)
        d = math.hypot(x - w / 2, y - h / 2)
        melhor = None
        menor = tolerancia
        for o in s["orbitas"]:
            diff = abs(d - o["raio"] * escala)
            if diff < menor:
                menor, melhor = diff, o
        return melhor

    # =====================================================================
    # MOUSE NA TELA
    # =====================================================================

    def _acertar_sistema(self, x, y):
        for s in reversed(self.sistemas()):
            sx, sy = self._p_tela(s)
            if math.hypot(x - sx, y - sy) <= RAIO_CLIQUE_SISTEMA:
                return s
        return None

    def _acertar_sistema_interno(self, x, y):
        """Retorna ('planeta', id) | ('estrela', None) | ('orbita', id) | None."""
        s = self._sistema(self.sistema_id)
        w, h = self._tamanho_tela()
        escala = self._escala_sistema(s, w, h)
        for o in s["orbitas"]:
            p = self._planeta(o["planeta_id"])
            if p:
                px, py = self._posicao_planeta(s, o, p, w, h, escala)
                if math.hypot(x - px, y - py) <= self._raio_planeta(p, self.fator) + 4:
                    return ("planeta", p["id"])
        if math.hypot(x - w / 2, y - h / 2) <= self._raio_estrela(s, self.fator) + 4:
            return ("estrela", None)
        o = self._orbita_proxima(s, x, y, w, h, tolerancia=7)
        if o:
            return ("orbita", o["id"])
        return None

    def _pressionar(self, event):
        if self.animando:
            return
        x, y = event.x, event.y
        if self.modo == "galaxia":
            s = self._acertar_sistema(x, y)
            if s:
                sx, sy = self._p_tela(s)
                self.arrasto = {"tipo": "sistema", "id": s["id"], "dx": x - sx, "dy": y - sy, "mexeu": False}
                self.sel = ("sistema", s["id"])
                self._recarregar_sistemas()
                self._atualizar_info()
                self._desenhar()
            else:
                self._pan = (x, y, list(self.cam))
                if self.sel:
                    self.sel = None
                    self._atualizar_tudo()
        else:
            alvo = self._acertar_sistema_interno(x, y)
            if alvo is None:
                self.sel = None
            elif alvo[0] == "estrela":
                self.sel = ("sistema", self.sistema_id)
            else:
                self.sel = alvo
            if alvo and alvo[0] == "planeta":
                self.arrasto = {"tipo": "canvas", "origem": alvo[1], "pos": (x, y), "mexeu": False}
            self._recarregar_planetas()
            self._atualizar_info()
            self._desenhar()

    def _mover(self, event):
        if self.animando:
            return
        if self.modo == "galaxia":
            if self.arrasto and self.arrasto["tipo"] == "sistema":
                s = self._sistema(self.arrasto["id"])
                w, h = self._tamanho_tela()
                s["x"] = self.cam[0] + (event.x - self.arrasto["dx"] - w / 2) / self.zoom
                s["y"] = self.cam[1] + (event.y - self.arrasto["dy"] - h / 2) / self.zoom
                self.arrasto["mexeu"] = True
                self._desenhar()
            elif self._pan:
                x0, y0, cam0 = self._pan
                self.cam = [cam0[0] - (event.x - x0) / self.zoom, cam0[1] - (event.y - y0) / self.zoom]
                self._desenhar()
        elif self.arrasto and self.arrasto["tipo"] == "canvas":
            self.arrasto["pos"] = (event.x, event.y)
            self.arrasto["mexeu"] = True
            self._desenhar()

    def _soltar(self, event):
        if self.modo == "galaxia":
            if self.arrasto and self.arrasto["tipo"] == "sistema":
                mexeu = self.arrasto["mexeu"]
                self.arrasto = None
                if mexeu:
                    self._fim_acao()
            self._pan = None
            return

        if self.arrasto and self.arrasto["tipo"] == "canvas":
            arr = self.arrasto
            self.arrasto = None
            if arr["mexeu"]:
                self._soltar_planeta(arr["origem"], event.x_root, event.y_root, event.x, event.y)
            else:
                self._desenhar()

    def _duplo_clique(self, event):
        if self.modo == "galaxia" and not self.animando:
            s = self._acertar_sistema(event.x, event.y)
            if s:
                self.arrasto = None
                self.ir_para_sistema(s["id"])
        elif self.modo == "sistema":
            alvo = self._acertar_sistema_interno(event.x, event.y)
            if alvo and alvo[0] == "estrela":
                self.editar_sistema(self._sistema(self.sistema_id))
            elif alvo and alvo[0] == "planeta":
                self.editar_planeta(self._planeta(alvo[1]))
            elif alvo and alvo[0] == "orbita":
                self.editar_orbita()

    def _roda(self, event, direcao=None):
        if direcao is None:
            direcao = 1 if event.delta > 0 else -1
        fator = 1.15 if direcao > 0 else 1 / 1.15
        if self.animando:
            return
        if self.modo == "galaxia":
            w, h = self._tamanho_tela()
            antes = ((event.x - w / 2) / self.zoom + self.cam[0], (event.y - h / 2) / self.zoom + self.cam[1])
            self.zoom = max(2.0, min(2000.0, self.zoom * fator))
            self.zoom_galaxia = self.zoom
            self.cam = [antes[0] - (event.x - w / 2) / self.zoom, antes[1] - (event.y - h / 2) / self.zoom]
        else:
            self.zoom_sis = max(0.3, min(6.0, self.zoom_sis * fator))
        self._desenhar()

    # =====================================================================
    # ARRASTAR E SOLTAR (armazenamento -> órbita)
    # =====================================================================

    def _iniciar_arrasto_lista(self, event, pid):
        self.sel = ("planeta", pid)
        self._atualizar_info()
        p = self._planeta(pid)
        self._cancelar_flutuante()
        self._flutuante = ctk.CTkLabel(self.tl, text=f"●  {p['nome']}", text_color="white",
                                       fg_color=p["cor"], corner_radius=8, padx=10, pady=4)
        self._flutuante_id = pid
        self._mover_arrasto_lista(event)

    def _mover_arrasto_lista(self, event):
        if self._flutuante is None:
            return
        x = event.x_root - self.tl.winfo_rootx() + 8
        y = event.y_root - self.tl.winfo_rooty() + 8
        self._flutuante.place(x=x, y=y)
        self._flutuante.lift()

    def _soltar_arrasto_lista(self, event):
        if self._flutuante is None:
            return
        pid = self._flutuante_id
        self._cancelar_flutuante()
        self._soltar_planeta(pid, event.x_root, event.y_root)

    def _cancelar_flutuante(self):
        if self._flutuante is not None:
            try:
                self._flutuante.destroy()
            except Exception:
                pass
        self._flutuante = None

    def _sobre_widget(self, x_root, y_root, alvo):
        w = self.tl.winfo_containing(x_root, y_root)
        while w is not None:
            if w is alvo:
                return True
            w = getattr(w, "master", None)
        return False

    def _soltar_planeta(self, pid, x_root, y_root, x_tela=None, y_tela=None):
        """Regra única de soltar: no armazenamento -> retira; sobre a tela -> órbita mais próxima."""
        p = self._planeta(pid)
        if p is None:
            self._desenhar()
            return

        if self._sobre_widget(x_root, y_root, self.dir):
            if self._orbita_do_planeta(p)[0] is not None:
                self._retirar(p)
                self._fim_acao()
            else:
                self._desenhar()
            return

        if self._sobre_widget(x_root, y_root, self.tela):
            if self.modo != "sistema":
                messagebox.showinfo("Planetas", "Entre em um sistema solar (duplo clique ou “Ir ➜”) "
                                                "para soltar o planeta em uma órbita.", parent=self.tl)
                return
            x = x_tela if x_tela is not None else x_root - self.tela.winfo_rootx()
            y = y_tela if y_tela is not None else y_root - self.tela.winfo_rooty()
            s = self._sistema(self.sistema_id)
            w, h = self._tamanho_tela()
            o = self._orbita_proxima(s, x, y, w, h)
            if o is not None and o["planeta_id"] != p["id"]:
                self._colocar(p, s, o)
                self.sel = ("planeta", p["id"])
                self._fim_acao()
                return
        self._desenhar()

    def _retirar(self, planeta):
        for s in self.sistemas():
            for o in s["orbitas"]:
                if o["planeta_id"] == planeta["id"]:
                    o["planeta_id"] = ""
        planeta["sistema_id"] = planeta["orbita_id"] = ""

    def _colocar(self, planeta, sistema, orbita):
        ocupante = self._planeta(orbita["planeta_id"])
        origem_s, origem_o = self._orbita_do_planeta(planeta)
        self._retirar(planeta)
        if ocupante is not None and ocupante is not planeta:
            if origem_o is not None:                       # troca de lugar
                origem_o["planeta_id"] = ocupante["id"]
                ocupante["sistema_id"], ocupante["orbita_id"] = origem_s["id"], origem_o["id"]
            else:                                          # volta ao armazenamento
                ocupante["sistema_id"] = ocupante["orbita_id"] = ""
        orbita["planeta_id"] = planeta["id"]
        planeta["sistema_id"], planeta["orbita_id"] = sistema["id"], orbita["id"]

    # =====================================================================
    # SISTEMAS
    # =====================================================================

    def _campos_sistema(self, s=None):
        return [
            {"chave": "nome", "rotulo": "Nome do sistema solar:", "tipo": "entry", "valor": s["nome"] if s else ""},
            {"chave": "estrela", "rotulo": "Nome da estrela:", "tipo": "entry", "valor": s["estrela"]["nome"] if s else ""},
            {"chave": "cor", "rotulo": "Cor da estrela (#rrggbb):", "tipo": "entry",
             "valor": s["estrela"]["cor"] if s else "#ffd54a"},
            {"chave": "tamanho", "rotulo": "Tamanho da estrela (1 = tamanho do Sol):", "tipo": "entry",
             "valor": f"{s['estrela']['tamanho']:g}" if s else "1"},
        ]

    def _validar_sistema(self, v, atual=None):
        if not v["nome"]:
            return "Digite o nome do sistema."
        if any(o is not atual and o["nome"].casefold() == v["nome"].casefold() for o in self.sistemas()):
            return "Já existe um sistema com esse nome."
        if not _hex_valido(v["cor"]):
            return "A cor deve estar no formato #rrggbb."
        t = _num(v["tamanho"])
        if t is None or t <= 0:
            return "O tamanho da estrela precisa ser um número maior que zero."
        return None

    def novo_sistema(self):
        def confirmar(v):
            erro = self._validar_sistema(v)
            if erro:
                return erro
            w, h = self._tamanho_tela()
            s = novo_sistema_solar(
                v["nome"], round(self.cam[0] + random.uniform(-3, 3), 2), round(self.cam[1] + random.uniform(-3, 3), 2))
            s["estrela"] = {"nome": v["estrela"] or v["nome"], "cor": v["cor"], "tamanho": _num(v["tamanho"])}
            self.sistemas().append(s)
            self.sel = ("sistema", s["id"])
            self._fim_acao()

        self.pedir_campos("Novo sistema solar", self._campos_sistema(), confirmar, texto_ok="Criar")

    def editar_sistema(self, s):
        if s is None:
            return

        def confirmar(v):
            erro = self._validar_sistema(v, s)
            if erro:
                return erro
            s["nome"] = v["nome"]
            s["estrela"] = {"nome": v["estrela"] or v["nome"], "cor": v["cor"], "tamanho": _num(v["tamanho"])}
            self._fim_acao()

        self.pedir_campos("Editar sistema solar", self._campos_sistema(s), confirmar, texto_ok="Salvar")

    def remover_sistema(self):
        s = self._sistema(self.sistema_id) if self.modo == "sistema" else (
            self._sistema(self.sel[1]) if self.sel and self.sel[0] == "sistema" else None)
        if s is None:
            messagebox.showinfo("Remover", "Selecione um sistema solar na lista ou na galáxia.", parent=self.tl)
            return
        if not messagebox.askyesno("Remover", f'Remover o sistema "{s["nome"]}"? '
                                              "Seus planetas voltam ao armazenamento.", parent=self.tl):
            return
        for o in s["orbitas"]:
            p = self._planeta(o["planeta_id"])
            if p:
                p["sistema_id"] = p["orbita_id"] = ""
        self.sistemas().remove(s)
        if self.sistema_id == s["id"]:
            self.modo, self.sistema_id, self.fator = "galaxia", None, 1.0
        self.sel = None
        self._fim_acao()

    # =====================================================================
    # ÓRBITAS
    # =====================================================================

    def adicionar_orbita(self):
        s = self._sistema(self.sistema_id) if self.modo == "sistema" else None
        if s is None:
            messagebox.showinfo("Órbitas", "Entre em um sistema solar para adicionar órbitas.", parent=self.tl)
            return
        raio = round(max([o["raio"] for o in s["orbitas"]] + [0.0]) + (1.0 if s["orbitas"] else 1.0), 2)
        o = {"id": str(uuid.uuid4()), "raio": raio, "planeta_id": "",
             "angulo0": round(random.uniform(0, 360), 1)}
        s["orbitas"].append(o)
        s["orbitas"].sort(key=lambda x: x["raio"])
        self.sel = ("orbita", o["id"])
        self._fim_acao()

    def _orbita_selecionada(self):
        s = self._sistema(self.sistema_id) if self.modo == "sistema" else None
        if s is None:
            return None, None
        if self.sel and self.sel[0] == "orbita":
            o = next((x for x in s["orbitas"] if x["id"] == self.sel[1]), None)
            return s, o
        return s, None

    def remover_orbita(self):
        s, o = self._orbita_selecionada()
        if s is None:
            messagebox.showinfo("Órbitas", "Entre em um sistema solar para remover órbitas.", parent=self.tl)
            return
        if o is None:
            messagebox.showinfo("Órbitas", "Clique na linha de uma órbita para selecioná-la.", parent=self.tl)
            return
        p = self._planeta(o["planeta_id"])
        if p:
            p["sistema_id"] = p["orbita_id"] = ""
        s["orbitas"].remove(o)
        self.sel = None
        self._fim_acao()

    def editar_orbita(self):
        s, o = self._orbita_selecionada()
        if o is None:
            return

        def confirmar(v):
            r = _num(v["raio"])
            if r is None or r <= 0:
                return "A distância precisa ser um número maior que zero."
            o["raio"] = r
            s["orbitas"].sort(key=lambda x: x["raio"])
            self._fim_acao()

        self.pedir_campos("Editar órbita", [
            {"chave": "raio", "rotulo": "Distância da estrela (UA):", "tipo": "entry", "valor": f"{o['raio']:g}"}],
            confirmar, texto_ok="Salvar")

    def editar_selecao(self):
        if not self.sel:
            return
        tipo, ident = self.sel
        if tipo == "sistema":
            self.editar_sistema(self._sistema(ident))
        elif tipo == "planeta":
            self.editar_planeta(self._planeta(ident))
        elif tipo == "orbita":
            self.editar_orbita()

    # =====================================================================
    # PLANETAS
    # =====================================================================

    def remover_planeta(self):
        p = self._planeta(self.sel[1]) if self.sel and self.sel[0] == "planeta" else None
        if p is None:
            messagebox.showinfo("Remover", "Selecione um planeta no armazenamento.", parent=self.tl)
            return
        if not messagebox.askyesno("Remover", f'Remover o planeta "{p["nome"]}"?', parent=self.tl):
            return
        self._retirar(p)
        self.planetas().remove(p)
        self.sel = None
        self._fim_acao()

    def editar_planeta(self, planeta):
        novo = planeta is None
        base = planeta or novo_planeta("")
        especies = self.especies()
        calendarios = self.calendarios()
        nomes_esp = [SEM_ESPECIE] + [e["nome"] for e in especies]
        nomes_cal = [SEM_CALENDARIO] + [c["nome"] for c in calendarios]
        esp0 = self._especie(base["especie_id"])

        campos = [
            {"chave": "nome", "rotulo": "Nome do planeta:", "tipo": "entry", "valor": base["nome"]},
            {"chave": "cor", "rotulo": "Cor (#rrggbb):", "tipo": "entry", "valor": base["cor"]},
            {"chave": "tamanho", "rotulo": "Tamanho:", "tipo": "menu", "opcoes": TAMANHOS, "valor": base["tamanho"]},
            {"chave": "diametro", "rotulo": "Diâmetro (km):", "tipo": "entry", "valor": f"{base['diametro_km']:g}"},
            {"chave": "peso", "rotulo": "Peso / massa (ex.: 5,97e24 kg):", "tipo": "entry", "valor": base["peso"]},
            {"chave": "luas", "rotulo": "Quantidade de luas:", "tipo": "entry", "valor": str(base.get("luas", 0))},
            {"chave": "estacoes", "rotulo": "Tem estações do ano", "tipo": "check", "valor": base["estacoes"]},
            {"chave": "especie", "rotulo": "Espécie que vive neste planeta:", "tipo": "menu",
             "opcoes": nomes_esp, "valor": esp0["nome"] if esp0 else SEM_ESPECIE},
            {"chave": "vinculo", "rotulo": "Calendário da espécie (se a espécie ainda não tiver um):",
             "tipo": "menu", "opcoes": nomes_cal, "valor": SEM_CALENDARIO},
            {"chave": "dias_ano", "rotulo": "Duração do ano (dias):", "tipo": "entry", "valor": f"{base['dias_ano']:g}"},
            {"chave": "horas_dia", "rotulo": "Duração do dia (horas):", "tipo": "entry", "valor": f"{base['horas_dia']:g}"},
        ]

        def definir(entry, texto, ativo):
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, texto)
            entry.configure(state="normal" if ativo else "disabled")

        def sincronizar(chave=None, valor=None, widgets=None):
            widgets = widgets or ws
            esp = next((e for e in especies if e["nome"] == widgets["especie"].get()), None)
            menu = widgets["vinculo"]
            cal = None
            if esp is None:
                menu.configure(values=[SEM_CALENDARIO], state="disabled")
                menu.set(SEM_CALENDARIO)
            elif self._calendario(esp.get("calendario_id")):
                cal = self._calendario(esp["calendario_id"])
                texto = f'{cal["nome"]} (herdado da espécie)'
                menu.configure(values=[texto], state="disabled")
                menu.set(texto)
            else:
                atual = menu.get()
                menu.configure(values=nomes_cal, state="normal")
                menu.set(atual if atual in nomes_cal else SEM_CALENDARIO)
                cal = next((c for c in calendarios if c["nome"] == menu.get()), None)
            if cal is not None:
                definir(widgets["dias_ano"], f"{dias_do_ano(cal, cal['ano_inicial'])}", False)
                definir(widgets["horas_dia"], f"{cal.get('horas_dia', 24):g}", False)
            else:
                for k in ("dias_ano", "horas_dia"):
                    widgets[k].configure(state="normal")

        def confirmar(v):
            nome = v["nome"]
            if not nome:
                return "Digite o nome do planeta."
            if any(p is not planeta and p["nome"].casefold() == nome.casefold() for p in self.planetas()):
                return "Já existe um planeta com esse nome."
            if not _hex_valido(v["cor"]):
                return "A cor deve estar no formato #rrggbb."
            diam = _num(v["diametro"])
            if diam is None or diam <= 0:
                return "O diâmetro precisa ser um número maior que zero."
            luas = _num(v["luas"] or "0")
            if luas is None or luas < 0 or luas != int(luas) or luas > 500:
                return "A quantidade de luas precisa ser um número inteiro entre 0 e 500."
            dias, horas = _num(v["dias_ano"]), _num(v["horas_dia"])
            if dias is None or dias <= 0 or horas is None or horas <= 0:
                return "A duração do ano e do dia precisam ser números maiores que zero."

            alvo = planeta or novo_planeta(nome)
            esp = next((e for e in especies if e["nome"] == v["especie"]), None)
            if esp is not None and not self._calendario(esp.get("calendario_id")):
                cal = next((c for c in calendarios if c["nome"] == v["vinculo"]), None)
                if cal is not None:
                    esp["calendario_id"] = cal["id"]       # a espécie passa a ter esse calendário

            alvo.update(nome=nome, cor=v["cor"], tamanho=v["tamanho"], diametro_km=diam, peso=v["peso"],
                        estacoes=bool(v["estacoes"]), luas=int(luas), especie_id=esp["id"] if esp else "",
                        dias_ano=dias, horas_dia=horas)
            if novo:
                self.planetas().append(alvo)
            self.sel = ("planeta", alvo["id"])
            self._fim_acao()

        ws = self.pedir_campos("Novo planeta" if novo else "Editar planeta", campos, confirmar,
                               texto_ok="Criar" if novo else "Salvar", ao_mudar=sincronizar, altura=580)
        sincronizar(widgets=ws)
