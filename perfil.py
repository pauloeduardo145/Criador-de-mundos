import customtkinter as ctk

from storage import carregar_perfil, salvar_perfil
from updater import VERSAO_ATUAL

PerfilUsuario = carregar_perfil()

class Perfil:
    
    def __init__(self, frame):

        self.frame = frame
    
    def abrir_perfil(self):

        if hasattr(self, "fa"):
            self.fa.grid()
            return

        self.fa = ctk.CTkFrame(self.frame, width=320, height=400)
        self.fa.grid_propagate(False)
        self.fa.grid(column=2, row=1)

        self.fa.grid_columnconfigure(0, weight=1)
        self.fa.grid_columnconfigure(1, weight=1)

        for i in range(12):
            self.fa.grid_rowconfigure(i, weight=1)
        
        self.mostrar_perfil()

    def mostrar_perfil(self):
        
        ##TOPO

        #icone

        icone = ctk.CTkLabel(self.fa,text="◯",font=("Arial",40))
        icone.grid(column=0,row=0,pady=12,columnspan=2)

        #nome
        Nome = ctk.CTkLabel(self.fa, text=PerfilUsuario["autor"])
        Nome.grid(column=0, row=1, padx=10, pady=12, columnspan=2)

        Descricao = ctk.CTkLabel(self.fa,text=PerfilUsuario["descricao"])
        Descricao.grid(column=0,row=2,padx=10,pady=12,columnspan=2)

        linha = ctk.CTkFrame(self.fa, height=2)
        linha.grid(row=3,column=0,columnspan=2,sticky="ew",padx=15,pady=(5, 10))

        # Estatísticas

        from historias import estatisticas

        stats = estatisticas()

        dados = [
            ("📚 Histórias", stats["historias"]),
            ("👥 Personagens", stats["personagens"]),
            ("✨ Sistemas de Poder", stats["sistemas"]),
            ("📖 Capítulos", stats["capitulos"]),
            ("📝 Observações", stats["observacoes"]),
        ]

        for i, (texto, valor) in enumerate(dados,start=4):
            
            lbl = ctk.CTkLabel(self.fa, text=texto,anchor="w")
            lbl.grid(row=i,column=0, sticky="w", padx=20)

            qtd = ctk.CTkLabel(self.fa,text=valor,font=("Arial", 14, "bold"))
            qtd.grid(row=i, column=1, sticky="e", padx=20)
        
        ## BOTÕES

        editar = ctk.CTkButton(self.fa,text="Editar Perfil",command= self.mostrar_edicao)
        editar.grid(row=10,column=0,columnspan=2,padx=20,pady=(10,5),sticky="ew")

        fechar = ctk.CTkButton(self.fa,text="Fechar Perfil", command= self.fechar_perfil)
        fechar.grid(row=11, column=0, columnspan=2,padx=15,pady=(10,5),sticky="ew")

        ## VERSÃO

        versao = ctk.CTkLabel(self.fa,text=f" Versão: {VERSAO_ATUAL}",anchor="e")
        versao.grid(row=12,column=1)

    def fechar_perfil(self):
        self.fa.grid_remove()

    def mostrar_edicao(self):

        for widget in self.fa.winfo_children():
            widget.destroy()

        self.fa.grid_columnconfigure(0, weight=1)
        self.fa.grid_columnconfigure(1, weight=1)

        for i in range(3):
            self.fa.grid_rowconfigure(i, weight=1)

        icone = ctk.CTkLabel(self.fa, text="◯", font=("Arial", 40))
        icone.grid(row=0, column=0, columnspan=2)

        self.nome = ctk.CTkEntry(self.fa)
        self.nome.insert(0, PerfilUsuario["autor"])
        self.nome.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.nome.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.descricao = ctk.CTkTextbox(self.fa)
        self.descricao.insert("1.0", PerfilUsuario["descricao"])
        self.descricao.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        botao_salvar = ctk.CTkButton(self.fa,text="[Salvar]",command=self.salvar)
        botao_salvar.grid(row=12, column=0, columnspan=2,padx=15,pady=(10,5),sticky="ew")

    def salvar(self):
        global PerfilUsuario

        nome = self.nome.get().strip()
        descricao = self.descricao.get("1.0", "end-1c").strip()

        PerfilUsuario["autor"] = nome
        PerfilUsuario["descricao"] = descricao

        salvar_perfil(PerfilUsuario)

        for widget in self.fa.winfo_children():
            widget.destroy()

        self.mostrar_perfil()