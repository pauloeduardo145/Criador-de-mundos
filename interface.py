import customtkinter as ctk
from widgets import mostrar_frame,criar_historia, ocultar_frame,criar_label
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
frame_historia.grid_rowconfigure(2,weight=2)
frame_historia.grid_rowconfigure(4,weight=1)
frame_historia.grid(column=0,row=1, padx=20,pady=5)


menu = ctk.CTkLabel(frame_historia,text='HISTÓRIAS')
menu.grid(column=0,row=0,sticky="n",padx=10,pady=10)

criah = ctk.CTkButton(frame_historia, text="[Criar historias]",command=lambda:mostrar_frame(frame_nomeh))
criah.grid(column=0,row=4,sticky="s",padx=10,pady=5)

#LABEL DO HISTORIA

frame_lista = ctk.CTkScrollableFrame(frame_historia)
frame_lista.grid_columnconfigure(0,weight=1)
frame_lista.grid_rowconfigure(0,weight=0)
frame_lista.grid(column=0,row=2,sticky="n",padx=10,pady=5)
frame_lista._scrollbar.configure(height=0)

#INFORMAÇÕES

frame_inf = ctk.CTkFrame(janela,width=200,height=350)
frame_inf.grid_propagate(False)
frame_inf.grid_columnconfigure(0,weight=1)
frame_inf.grid_rowconfigure(0,weight=1)
frame_inf.grid(column=0,row=2,padx=20,pady=10)

inicio = ctk.CTkLabel(frame_inf,text='INFORMAÇÕES')
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=10)

lista = ctk.CTkFrame(frame_inf,width=200,height=300)
lista.grid_propagate(False)
lista.grid_columnconfigure(0,weight=1)
lista.grid_rowconfigure(0,weight=0)
lista.grid_rowconfigure(0,weight=0)
lista.grid_rowconfigure(2,weight=1)
lista.grid_rowconfigure(3,weight=1)
lista.grid_rowconfigure(4,weight=1)
lista.grid_rowconfigure(5,weight=1)
lista.grid_rowconfigure(6,weight=1)
lista.grid(column=0,row=2,sticky="n",padx=10,pady=5)

#LABELS DO INFORMAÇÕES
nome_historia = ctk.CTkLabel(lista,text='Nome:')
nome_historia.grid(column=0,row=0,sticky="w",padx=10,pady=10)

arcos = ctk.CTkLabel(lista,text='Arcos:')
arcos.grid(column=0,row=2,sticky="w",padx=10,pady=10)

cap = ctk.CTkLabel(lista,text='Capitulos:')
cap.grid(column=0,row=3,sticky="w",padx=10,pady=10)

pers = ctk.CTkLabel(lista,text='Personagens:')
pers.grid(column=0,row=4,sticky="w",padx=10,pady=10)

ue = ctk.CTkLabel(lista,text='Ultima Edição:')
ue.grid(column=0,row=5,sticky="w",padx=10,pady=10)

sp = ctk.CTkLabel(lista,text='Sistema(as) de Poder(es):')
sp.grid(column=0,row=6,sticky="w",padx=10,pady=10)

#RECEBER INFORMAÇÕES DA HISTORIA SELECIONADA 




#CONTEUDO

frame_conteudo = ctk.CTkFrame(janela)
frame_conteudo.grid_propagate(False)
frame_conteudo.grid_columnconfigure(0,weight=1)
frame_conteudo.grid_rowconfigure(0,weight=1)
frame_conteudo.grid(column=1, row=0, columnspan=5, rowspan=5, sticky="nsew",padx=5,pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0,sticky="n",padx=10,pady=10)

#CAIXA

caixa_frame = ctk.CTkFrame(janela,width= 200,height=50)
caixa_frame.grid_propagate(False)
caixa_frame.grid(column=0,row=0,padx=10,pady=10)

botaofake = ctk.CTkButton(caixa_frame,text="butoon",fg_color="black",width=4,font=("Helvetica", 10))
botaofake.grid(column=0,row=0,sticky="n",padx=5,pady=10)

label_config = ctk.CTkButton(caixa_frame,text="config",fg_color="black",width=4,font=("Helvetica", 10))
label_config.grid(column=1,row=0,sticky="n",padx=5,pady=10)

#CRIAR INTERFACE

frame_nomeh = ctk.CTkFrame(janela,fg_color="black",width=200, height=150)
frame_nomeh.grid_propagate(False)
frame_nomeh.grid_columnconfigure(0, weight=1)

frame_nomeh.place(relx=0.5, rely=0.5, anchor="center")
frame_nomeh.place_forget()

botaofake = ctk.CTkLabel(frame_nomeh,text="Criar historia")
botaofake.grid(column=0,row=1,padx=10,pady=10)

nome = ctk.CTkEntry(frame_nomeh)
nome.grid(column=0,row=2)
nome.focus()


criar_h = ctk.CTkButton(frame_nomeh,text="Criar", command=lambda:(criar_historia(nome.get()),criar_label(nome.get(),frame_lista),ocultar_frame(frame_nomeh)))
criar_h.grid(column=0,row=3,padx=10,pady=10,sticky="s")

janela.mainloop()