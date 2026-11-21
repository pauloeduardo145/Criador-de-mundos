import customtkinter as ctk

from mural import JanelaRascunho
from modelos import novo_calendario
from entry_textbox import configurar_entry

ANO_MAX_CALCULO = 100000   # limite do cálculo do dia da semana (evita laço enorme)


# ---------------------------------------------------------------------------
# CÁLCULOS (funções puras, sem interface)
# ---------------------------------------------------------------------------

def dias_do_mes(cal, ano, i):
    """Dias do mês i no ano dado, considerando regras e anos especiais."""
    especial = next((a for a in cal.get("anos_especiais", []) if a["ano"] == ano), None)
    if especial is not None and i < len(especial["dias"]):
        return max(1, int(especial["dias"][i]))

    dias = int(cal["meses"][i]["dias"])
    for r in cal.get("regras", []):
        cada = int(r["cada"])
        # O N-ésimo ano contado a partir do ano inicial recebe os dias extras.
        if cada > 0 and r["mes"] == i and (ano - cal["ano_inicial"] + 1) % cada == 0:
            dias += int(r["extra"])
    return max(1, dias)


def dias_do_ano(cal, ano):
    """O ano é o total de dias dos seus meses."""
    return sum(dias_do_mes(cal, ano, i) for i in range(len(cal["meses"])))


def deslocamento_do_ano(cal, ano):
    """Quantos dias se passaram do início do ano inicial até o início de `ano`."""
    return sum(dias_do_ano(cal, a) for a in range(cal["ano_inicial"], ano))


def dia_da_semana_do_mes(cal, ano, i):
    """Índice (em dias_semana) do primeiro dia do mês i."""
    n = max(1, len(cal["dias_semana"]))
    antes = sum(dias_do_mes(cal, ano, k) for k in range(i))
    return (deslocamento_do_ano(cal, ano) + antes) % n


def _int(texto):
    try:
        return int(str(texto).strip())
    except ValueError:
        return None


def _float(texto):
    try:
        return float(str(texto).strip().replace(",", "."))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# JANELA
# ---------------------------------------------------------------------------

class CalendarioJanela(JanelaRascunho):
    titulo = "📅 Calendários"
    geometria = "1300x780"
    tamanho_minimo = (1000, 600)
    chave = "calendarios"
    rotulo_item = "calendário"
    icone = "📅"

    # ---- novo ----------------------------------------------------------------

    def campos_novo(self):
        return [
            {"chave": "nome", "rotulo": "Nome do calendário:", "tipo": "entry",
             "placeholder": "Ex: Calendário Élfico"},
            {"chave": "ano_inicial", "rotulo": "Ano inicial:", "tipo": "entry", "valor": "1"},
        ]

    def criar_item(self, valores):
        ano = _int(valores.get("ano_inicial", "1"))
        if ano is None:
            return "O ano inicial precisa ser um número inteiro."
        return novo_calendario(valores["nome"], self.historia(), ano)

    # ---- área principal --------------------------------------------------------

    def construir_area(self, frame):
        frame.grid_columnconfigure(0, weight=1, uniform="cal")
        frame.grid_columnconfigure(1, weight=1, uniform="cal")

        self.editor = ctk.CTkScrollableFrame(frame, label_text="Editor")
        self.editor.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.editor.grid_columnconfigure(0, weight=1)

        self.painel_prev = ctk.CTkFrame(frame)
        self.painel_prev.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.painel_prev.grid_columnconfigure(0, weight=1)
        self.painel_prev.grid_rowconfigure(2, weight=1)

        self.ano_prev = None
        self.mes_prev = 0
        self._montar_preview_base()

    # ---- edição ---------------------------------------------------------------------

    def ao_carregar_rascunho(self):
        self.ano_prev = None
        self._montar_editor()
        self._atualizar_preview()

    def _entrada(self, pai, valor, largura=None, **grid):
        e = ctk.CTkEntry(pai, width=largura or 140)
        e.insert(0, str(valor))
        configurar_entry(e)
        e.bind("<KeyRelease>", self._ao_digitar)
        e.bind("<FocusOut>", self._ao_terminar_campo)
        e.bind("<Return>", self._ao_terminar_campo)
        e.grid(**grid)
        return e

    def _ao_digitar(self, event=None):
        self._ler_widgets()
        self._atualizar_preview()
        self._atualizar_estado()

    def _ao_terminar_campo(self, event=None):
        self._ler_widgets()
        self.checkpoint()

    def _titulo_secao(self, texto, linha):
        ctk.CTkLabel(self.editor, text=texto, font=("Helvetica", 16, "bold"),
                     anchor="w").grid(row=linha, column=0, sticky="ew", padx=6, pady=(14, 4))

    def _montar_editor(self):
        rolagem = self.editor._parent_canvas.yview()[0]

        for w in self.editor.winfo_children():
            w.destroy()

        self.e_semana, self.e_meses, self.e_regras, self.e_especiais = [], [], [], []
        c = self.rascunho
        if c is None:
            ctk.CTkLabel(self.editor, text="Crie ou selecione um calendário\npara editar.",
                         justify="center").grid(row=0, column=0, pady=60)
            return

        linha = 0

        # Básico
        geral = ctk.CTkFrame(self.editor, fg_color="transparent")
        geral.grid(row=linha, column=0, sticky="ew"); linha += 1
        for col, (rotulo, attr, valor) in enumerate([
            ("Nome", "e_nome", c["nome"]),
            ("Ano inicial", "e_ano_inicial", c["ano_inicial"]),
            ("Horas por dia", "e_horas", c.get("horas_dia", 24)),
        ]):
            ctk.CTkLabel(geral, text=rotulo, anchor="w").grid(row=0, column=col, sticky="w", padx=4)
            setattr(self, attr, self._entrada(geral, valor, 150 if col == 0 else 90,
                                              row=1, column=col, padx=4, pady=(0, 4)))

        self.lbl_resumo = ctk.CTkLabel(self.editor, text="", anchor="w", justify="left")
        self.lbl_resumo.grid(row=linha, column=0, sticky="ew", padx=6, pady=4); linha += 1

        # Dias da semana
        self._titulo_secao("Dias da semana", linha); linha += 1
        bloco = ctk.CTkFrame(self.editor, fg_color="transparent")
        bloco.grid(row=linha, column=0, sticky="ew"); linha += 1
        for i, nome in enumerate(c["dias_semana"]):
            ctk.CTkLabel(bloco, text=f"{i + 1}.", width=26).grid(row=i, column=0)
            self.e_semana.append(self._entrada(bloco, nome, 180, row=i, column=1, padx=4, pady=2))
            ctk.CTkButton(bloco, text="✖", width=30, fg_color="#8b2e2e", hover_color="#a33a3a",
                          command=lambda k=i: self._remover_dia_semana(k)).grid(row=i, column=2, padx=4)
        ctk.CTkButton(self.editor, text="+ Dia da semana", width=140,
                      command=self._adicionar_dia_semana).grid(row=linha, column=0, sticky="w", padx=6, pady=4)
        linha += 1

        # Meses
        self._titulo_secao("Meses (nome e quantidade de dias)", linha); linha += 1
        bloco = ctk.CTkFrame(self.editor, fg_color="transparent")
        bloco.grid(row=linha, column=0, sticky="ew"); linha += 1
        for i, mes in enumerate(c["meses"]):
            ctk.CTkLabel(bloco, text=f"{i + 1}.", width=26).grid(row=i, column=0)
            en = self._entrada(bloco, mes["nome"], 180, row=i, column=1, padx=4, pady=2)
            ed = self._entrada(bloco, mes["dias"], 60, row=i, column=2, padx=4, pady=2)
            ctk.CTkLabel(bloco, text="dias").grid(row=i, column=3)
            ctk.CTkButton(bloco, text="✖", width=30, fg_color="#8b2e2e", hover_color="#a33a3a",
                          command=lambda k=i: self._remover_mes(k)).grid(row=i, column=4, padx=4)
            self.e_meses.append((en, ed))
        ctk.CTkButton(self.editor, text="+ Mês", width=140,
                      command=self._adicionar_mes).grid(row=linha, column=0, sticky="w", padx=6, pady=4)
        linha += 1

        # Anos variáveis
        self._titulo_secao("Anos com duração variável", linha); linha += 1
        ctk.CTkLabel(self.editor, anchor="w", justify="left", wraplength=420,
                     text="Regra: a cada N anos (contando do ano inicial) um mês ganha dias extras. "
                          "Ano especial: define os dias de cada mês de um ano específico "
                          "e tem prioridade sobre as regras."
                     ).grid(row=linha, column=0, sticky="ew", padx=6); linha += 1

        opcoes_mes = [f"{i + 1}. {m['nome']}" for i, m in enumerate(c["meses"])]
        bloco = ctk.CTkFrame(self.editor, fg_color="transparent")
        bloco.grid(row=linha, column=0, sticky="ew"); linha += 1
        for i, r in enumerate(c["regras"]):
            ctk.CTkLabel(bloco, text="A cada").grid(row=i, column=0, padx=2)
            ec = self._entrada(bloco, r["cada"], 50, row=i, column=1, padx=2, pady=2)
            ctk.CTkLabel(bloco, text="anos, mês").grid(row=i, column=2, padx=2)
            menu = ctk.CTkOptionMenu(bloco, values=opcoes_mes, width=140,
                                     command=lambda v, k=i: self._ao_mudar_mes_regra(k))
            menu.set(opcoes_mes[r["mes"]] if r["mes"] < len(opcoes_mes) else opcoes_mes[0])
            menu.grid(row=i, column=3, padx=2)
            ctk.CTkLabel(bloco, text="+").grid(row=i, column=4)
            ee = self._entrada(bloco, r["extra"], 50, row=i, column=5, padx=2)
            ctk.CTkLabel(bloco, text="dias").grid(row=i, column=6)
            ctk.CTkButton(bloco, text="✖", width=30, fg_color="#8b2e2e", hover_color="#a33a3a",
                          command=lambda k=i: self._remover_regra(k)).grid(row=i, column=7, padx=4)
            self.e_regras.append((ec, menu, ee))
        ctk.CTkButton(self.editor, text="+ Regra de ano variável", width=180,
                      command=self._adicionar_regra).grid(row=linha, column=0, sticky="w", padx=6, pady=4)
        linha += 1

        bloco = ctk.CTkFrame(self.editor, fg_color="transparent")
        bloco.grid(row=linha, column=0, sticky="ew"); linha += 1
        for i, a in enumerate(c["anos_especiais"]):
            ctk.CTkLabel(bloco, text="Ano").grid(row=i, column=0, padx=2)
            ea = self._entrada(bloco, a["ano"], 70, row=i, column=1, padx=2, pady=2)
            ed = self._entrada(bloco, ", ".join(str(d) for d in a["dias"]), 240,
                               row=i, column=2, padx=2)
            ctk.CTkButton(bloco, text="✖", width=30, fg_color="#8b2e2e", hover_color="#a33a3a",
                          command=lambda k=i: self._remover_ano_especial(k)).grid(row=i, column=3, padx=4)
            self.e_especiais.append((ea, ed))
        ctk.CTkLabel(self.editor, anchor="w", text="(dias de cada mês separados por vírgula)"
                     ).grid(row=linha, column=0, sticky="w", padx=6); linha += 1
        ctk.CTkButton(self.editor, text="+ Ano especial", width=140,
                      command=self._adicionar_ano_especial).grid(row=linha, column=0, sticky="w", padx=6, pady=4)

        self.editor.update_idletasks()
        self.editor._parent_canvas.yview_moveto(rolagem)

    # ---- leitura dos campos para o rascunho -----------------------------------------------

    def _marcar(self, entry, ok):
        normal = ctk.ThemeManager.theme["CTkEntry"]["border_color"]
        entry.configure(border_color=normal if ok else "#ff4d4d")

    def _ler_widgets(self):
        c = self.rascunho
        if c is None or not hasattr(self, "e_nome") or not self.e_nome.winfo_exists():
            return

        c["nome"] = self.e_nome.get().strip() or c["nome"]

        v = _int(self.e_ano_inicial.get())
        self._marcar(self.e_ano_inicial, v is not None)
        if v is not None:
            c["ano_inicial"] = v

        v = _float(self.e_horas.get())
        self._marcar(self.e_horas, v is not None and v > 0)
        if v is not None and v > 0:
            c["horas_dia"] = int(v) if v == int(v) else v

        c["dias_semana"] = [e.get().strip() for e in self.e_semana]

        for mes, (en, ed) in zip(c["meses"], self.e_meses):
            mes["nome"] = en.get().strip()
            v = _int(ed.get())
            ok = v is not None and 1 <= v <= 1000
            self._marcar(ed, ok)
            if ok:
                mes["dias"] = v

        for r, (ec, menu, ee) in zip(c["regras"], self.e_regras):
            v = _int(ec.get()); ok = v is not None and v >= 1
            self._marcar(ec, ok)
            if ok:
                r["cada"] = v
            v = _int(ee.get()); ok = v is not None
            self._marcar(ee, ok)
            if ok:
                r["extra"] = v
            r["mes"] = max(0, int(menu.get().split(".")[0]) - 1)

        for a, (ea, ed) in zip(c["anos_especiais"], self.e_especiais):
            v = _int(ea.get()); self._marcar(ea, v is not None)
            if v is not None:
                a["ano"] = v
            dias = [_int(p) for p in ed.get().split(",") if p.strip()]
            ok = bool(dias) and all(d is not None and 1 <= d <= 1000 for d in dias)
            self._marcar(ed, ok)
            if ok:
                a["dias"] = dias

    # ---- ações estruturais ---------------------------------------------------------------------

    def _estrutural(self, funcao):
        self._ler_widgets()
        funcao(self.rascunho)
        self.checkpoint()
        self._montar_editor()
        self._atualizar_preview()

    def _adicionar_dia_semana(self):
        self._estrutural(lambda c: c["dias_semana"].append(f"Dia {len(c['dias_semana']) + 1}"))

    def _remover_dia_semana(self, i):
        if len(self.rascunho["dias_semana"]) <= 1:
            return
        self._estrutural(lambda c: c["dias_semana"].pop(i))

    def _adicionar_mes(self):
        self._estrutural(lambda c: c["meses"].append(
            {"nome": f"Mês {len(c['meses']) + 1}", "dias": 30}))

    def _remover_mes(self, i):
        if len(self.rascunho["meses"]) <= 1:
            return

        def remover(c):
            c["meses"].pop(i)
            c["regras"] = [r for r in c["regras"] if r["mes"] != i]
            for r in c["regras"]:
                if r["mes"] > i:
                    r["mes"] -= 1
            for a in c["anos_especiais"]:
                if i < len(a["dias"]):
                    a["dias"].pop(i)
        self._estrutural(remover)

    def _adicionar_regra(self):
        self._estrutural(lambda c: c["regras"].append({"cada": 4, "mes": 0, "extra": 1}))

    def _ao_mudar_mes_regra(self, k):
        self._ler_widgets()
        self.checkpoint()
        self._atualizar_preview()

    def _remover_regra(self, i):
        self._estrutural(lambda c: c["regras"].pop(i))

    def _adicionar_ano_especial(self):
        def adicionar(c):
            usados = {a["ano"] for a in c["anos_especiais"]}
            ano = c["ano_inicial"]
            while ano in usados:
                ano += 1
            c["anos_especiais"].append({"ano": ano, "dias": [m["dias"] for m in c["meses"]]})
        self._estrutural(adicionar)

    def _remover_ano_especial(self, i):
        self._estrutural(lambda c: c["anos_especiais"].pop(i))

    def validar(self, c):
        self._ler_widgets()
        if not c["nome"].strip():
            return "O calendário precisa de um nome."
        if not c["dias_semana"] or any(not d for d in c["dias_semana"]):
            return "Todos os dias da semana precisam de um nome."
        if not c["meses"] or any(not m["nome"] for m in c["meses"]):
            return "Todos os meses precisam de um nome."
        nomes = [m["nome"].casefold() for m in c["meses"]]
        if len(set(nomes)) != len(nomes):
            return "Há meses com nomes repetidos."
        anos = [a["ano"] for a in c["anos_especiais"]]
        if len(set(anos)) != len(anos):
            return "Há anos especiais repetidos."
        return None

    # ---- visualização (sempre do rascunho, antes de salvar) --------------------------------------

    def _montar_preview_base(self):
        p = self.painel_prev
        ctk.CTkLabel(p, text="👁 Visualização (antes de salvar)",
                     font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=(10, 4))

        nav = ctk.CTkFrame(p, fg_color="transparent")
        nav.grid(row=1, column=0, sticky="ew", padx=10)
        nav.grid_columnconfigure(4, weight=1)
        ctk.CTkButton(nav, text="◀", width=30, command=lambda: self._mover_mes(-1)).grid(row=0, column=0)
        self.lbl_mes = ctk.CTkLabel(nav, text="", font=("Helvetica", 15, "bold"), width=190)
        self.lbl_mes.grid(row=0, column=1, padx=4)
        ctk.CTkButton(nav, text="▶", width=30, command=lambda: self._mover_mes(1)).grid(row=0, column=2)
        ctk.CTkLabel(nav, text="Ano:").grid(row=0, column=3, padx=(14, 2), sticky="e")
        self.e_ano_prev = ctk.CTkEntry(nav, width=80)
        self.e_ano_prev.grid(row=0, column=4, sticky="w")
        configurar_entry(self.e_ano_prev)
        self.e_ano_prev.bind("<Return>", self._ir_para_ano)
        self.e_ano_prev.bind("<FocusOut>", self._ir_para_ano)

        self.grade = ctk.CTkFrame(p, fg_color="transparent")
        self.grade.grid(row=2, column=0, sticky="nsew", padx=10, pady=8)

        self.lbl_info = ctk.CTkLabel(p, text="", justify="left", anchor="w", wraplength=480)
        self.lbl_info.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))

    def _ir_para_ano(self, event=None):
        v = _int(self.e_ano_prev.get())
        if v is not None:
            self.ano_prev = v
        self._atualizar_preview()

    def _mover_mes(self, delta):
        c = self.rascunho
        if c is None:
            return
        self.mes_prev += delta
        n = len(c["meses"])
        while self.mes_prev < 0:
            self.mes_prev += n
            self.ano_prev -= 1
        while self.mes_prev >= n:
            self.mes_prev -= n
            self.ano_prev += 1
        self._atualizar_preview()

    def _atualizar_preview(self):
        for w in self.grade.winfo_children():
            w.destroy()

        c = self.rascunho
        if c is None:
            self.lbl_mes.configure(text="—")
            self.lbl_info.configure(text="")
            return

        # Dados do rascunho ainda incompletos (ex.: nome vazio) não quebram a visualização.
        meses = c["meses"]
        semana = [d or "?" for d in c["dias_semana"]] or ["?"]
        if not meses:
            return

        if self.ano_prev is None:
            self.ano_prev = c["ano_inicial"]
        self.ano_prev = max(c["ano_inicial"], min(self.ano_prev, c["ano_inicial"] + ANO_MAX_CALCULO))
        self.mes_prev = max(0, min(self.mes_prev, len(meses) - 1))

        ano, i = self.ano_prev, self.mes_prev
        self.e_ano_prev.delete(0, "end")
        self.e_ano_prev.insert(0, str(ano))
        self.lbl_mes.configure(text=f"{meses[i]['nome'] or '?'} · {ano}")

        n = len(semana)
        for col, nome in enumerate(semana):
            self.grade.grid_columnconfigure(col, weight=1, uniform="dia")
            ctk.CTkLabel(self.grade, text=nome[:3], font=("Helvetica", 12, "bold"),
                         text_color="#9bb7d4").grid(row=0, column=col, pady=(0, 4))

        inicio = dia_da_semana_do_mes(c, ano, i)
        total = dias_do_mes(c, ano, i)
        for d in range(total):
            pos = inicio + d
            ctk.CTkLabel(
                self.grade, text=str(d + 1), height=30, corner_radius=6,
                fg_color=("#2b3a4a" if (pos % n) == 0 else "#2a2a2a")
            ).grid(row=1 + pos // n, column=pos % n, padx=1, pady=1, sticky="ew")

        base = sum(m["dias"] for m in meses)
        dias_ano = dias_do_ano(c, ano)
        extra = dias_ano - base
        texto = (f"Ano {ano}: {dias_ano} dias em {len(meses)} meses"
                 + (f" ({extra:+d} em relação ao ano comum de {base})" if extra else "")
                 + f"\nMês {meses[i]['nome'] or '?'}: {total} dias · semana de {n} dias · "
                   f"{c.get('horas_dia', 24)} horas por dia"
                 + f"\n1º dia do ano cai em: {semana[deslocamento_do_ano(c, ano) % n]}")
        self.lbl_info.configure(text=texto)

        if hasattr(self, "lbl_resumo") and self.lbl_resumo.winfo_exists():
            self.lbl_resumo.configure(
                text=f"Ano comum: {base} dias · {len(meses)} meses · semana de {n} dias")
