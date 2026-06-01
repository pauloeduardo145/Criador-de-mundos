import customtkinter as ctk
from widgets import mostrar_frame,criar_historia, ocultar_frame

ctk.set_appearance_mode("dark")

#JANELAS

janela = ctk.CTk()
janela.title("Criador de Mundos")
janela.geometry("1000x1000")
janela.attributes('-fullscreen', True)
janela.bind('<Escape>', lambda e: janela.attributes('-fullscreen', False))
janela.grid_columnconfigure(1, weight=1)
janela.grid_rowconfigure(1,weight=1)

#HISTORIAS

frame_historia = ctk.CTkFrame(janela, width= 200,height=350)
frame_historia.grid_propagate(False)
frame_historia.grid_columnconfigure(0,weight=1)
frame_historia.grid_rowconfigure(0,weight=1)
frame_historia.grid(column=0,row=1, padx=20,pady=10)

menu = ctk.CTkLabel(frame_historia,text='HISTÓRIAS')
menu.grid(column=0,row=0,sticky="n",padx=10,pady=10)

button_base = ctk.CTkButton(frame_historia, text="Criar historias",command=lambda:mostrar_frame(frame_nomeh))
button_base.grid(column=0,row=1,sticky="n",padx=10,pady=10)

#INFORMAÇÕES

frame_inf = ctk.CTkFrame(janela,width=200,height=350)
frame_inf.grid_propagate(False)
frame_inf.grid_columnconfigure(0,weight=1)
frame_inf.grid_rowconfigure(0,weight=1)
frame_inf.grid(column=0,row=2,padx=20,pady=10)

inicio = ctk.CTkLabel(frame_inf,text='INFORMAÇÕES')
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=10)

#CONTEUDO

frame_conteudo = ctk.CTkFrame(janela)
frame_conteudo.grid_propagate(False)
frame_conteudo.grid_columnconfigure(0,weight=1)
frame_conteudo.grid_rowconfigure(0,weight=1)
frame_conteudo.grid(column=1, row=0, columnspan=5, rowspan=5, sticky="nsew",padx=10,pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0,sticky="n",padx=10,pady=10)

#CAIXA

caixa_frame = ctk.CTkFrame(janela,width= 200,height=50)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,padx=10,pady=10)

botaofake = ctk.CTkLabel(caixa_frame,text="butoon",font=("Helvetica", 10))
botaofake.grid(column=0,row=0,sticky="n",padx=10,pady=10)

confi = ctk.CTkLabel(caixa_frame,text="config",font=("Helvetica", 10))
confi.grid(column=1,row=0,sticky="n",padx=10,pady=10)

#CRIAR INTERFACE

frame_nomeh = ctk.CTkFrame(janela,fg_color="black",width=200, height=150)
frame_nomeh.grid_propagate(False)
frame_nomeh.grid_columnconfigure(0, weight=1)

frame_nomeh.place(relx=0.5, rely=0.5, anchor="center")
frame_nomeh.place_forget()

botaofake = ctk.CTkLabel(frame_nomeh,text="Criar historia")
botaofake.grid(column=0,row=1,padx=10,pady=10)

nome = ctk.CTkEntry(frame_nomeh)
nome.grid(column=0,row=2)#columnspan=2)

criar_h = ctk.CTkButton(frame_nomeh,text="Criar", command=lambda:(criar_historia(nome),ocultar_frame(frame_nomeh)) )
criar_h.grid(column=0,row=3,padx=10,pady=10,sticky="s")

janela.mainloop()