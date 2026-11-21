import customtkinter as ctk

from calendario import CalendarioJanela
from dicionario import DicionarioJanela
from desenho import DesenhoJanela
from sistema_solar import SistemaSolarJanela


class Mural:
    """
    MURAL: ao clicar em "Mural" o conteúdo é limpo e aparecem os botões das
    ferramentas. Cada ferramenta abre no seu próprio Toplevel ÚNICO
    (criado uma vez e depois só mostrado/escondido):

      📅 Calendários        — dias, semanas, meses e anos personalizados
      📖 Dicionários        — alfabetos/fontes desenhados letra a letra
      🎨 Desenhar           — tela de desenho com camadas e exportação
      🪐 Sistemas solares   — planetas, órbitas e galáxia

    Para acrescentar uma ferramenta nova basta incluir uma linha em
    `self.ferramentas` (ícone, título, chave na história, janela).
    Ctrl+Z / Ctrl+Y funcionam dentro de cada janela.
    """

    def __init__(self, janela, frame_conteudo, mostrar_no_conteudo=None,
                 obter_historia_selecionada=None, navegar=None):

        self.janela = janela
        self.frame_conteudo = frame_conteudo
        self.obter_historia_selecionada = obter_historia_selecionada
        self.navegar = navegar

        obter = lambda: self.obter_historia_selecionada() if self.obter_historia_selecionada else None

        self.calendarios = CalendarioJanela(janela, obter)
        self.dicionarios = DicionarioJanela(janela, obter)
        self.desenhos = DesenhoJanela(janela, obter)
        self.sistemas_solares = SistemaSolarJanela(janela, obter)

        # (ícone, título, texto da contagem, janela)
        self.ferramentas = [
            ("📅", "Calendários", lambda h: f'{len(h.get("calendarios", []))}', self.calendarios),
            ("📖", "Dicionários", lambda h: f'{len(h.get("dicionarios", []))}', self.dicionarios),
            ("🎨", "Desenhar", lambda h: f'{len(h.get("desenhos", []))}', self.desenhos),
            ("🪐", "Sistemas solares",
             lambda h: f'{len(h.get("sistemas_solares", []))} sistemas · {len(h.get("planetas", []))} planetas',
             self.sistemas_solares),
        ]

    def limpar_frame_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        # Força o canvas a recalcular a área rolável com base no conteúdo atual
        self.frame_conteudo.update_idletasks()
        self.frame_conteudo._parent_canvas.configure(
            scrollregion=self.frame_conteudo._parent_canvas.bbox("all")
        )
        self.frame_conteudo._parent_canvas.yview_moveto(0)

    def mostrar_mural(self, event=None):
        historia = self.obter_historia_selecionada() if self.obter_historia_selecionada else None

        self.limpar_frame_conteudo()

        if historia is None:
            ctk.CTkLabel(
                self.frame_conteudo,
                text="📖 Nenhuma história selecionada.\nCrie ou selecione uma história para continuar.",
                font=("Helvetica", 18), justify="center"
            ).pack(expand=True)
            return

        ctk.CTkLabel(self.frame_conteudo, text="🖼️ Mural",
                     font=("Helvetica", 22, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(self.frame_conteudo, anchor="w",
                     text="Escolha uma ferramenta. Cada uma abre em sua própria janela.").pack(
            anchor="w", padx=20, pady=(0, 10))

        grade = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        grade.pack(fill="x", padx=20, pady=10)
        colunas = 2
        for c in range(colunas):
            grade.grid_columnconfigure(c, weight=1, uniform="mural")

        for i, (icone, titulo, contagem, ferramenta) in enumerate(self.ferramentas):
            ctk.CTkButton(
                grade, text=f"{icone}  {titulo}\n({contagem(historia)})",
                height=90, font=("Helvetica", 16, "bold"),
                command=ferramenta.abrir
            ).grid(row=i // colunas, column=i % colunas, padx=8, pady=8, sticky="ew")

        self.frame_conteudo.update_idletasks()
        self.frame_conteudo._parent_canvas.configure(
            scrollregion=self.frame_conteudo._parent_canvas.bbox("all"))
