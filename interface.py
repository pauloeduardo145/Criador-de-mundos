import customtkinter as ctk

ctk.set_appearance_mode("dark")

#JANELAS

janela = ctk.CTk()
janela.title("Criador de Mundos")
janela.geometry("1000x1000")
janela.attributes('-fullscreen', True)
janela.bind('<Escape>', lambda e: janela.attributes('-fullscreen', False))
janela.grid_columnconfigure(1, weight=1)
janela.grid_rowconfigure(1,weight=1)

#MENU

frame_menu = ctk.CTkFrame(janela, width= 200,height=350)
frame_menu.grid_propagate(False)
frame_menu.grid_columnconfigure(0,weight=1)
frame_menu.grid_rowconfigure(0,weight=1)
frame_menu.grid(column=0,row=0, padx=20,pady=10)

menu = ctk.CTkLabel(frame_menu,text='HISTÓRIAS')
menu.grid(column=0,row=0,sticky="n",padx=10,pady=10)

#INFORMAÇÕES

frame_inf = ctk.CTkFrame(janela,width=200,height=350)
frame_inf.grid_propagate(False)
frame_inf.grid_columnconfigure(0,weight=1)
frame_inf.grid_rowconfigure(0,weight=1)
frame_inf.grid(column=0,row=1,padx=20,pady=10)

inicio = ctk.CTkLabel(frame_inf,text='INFORMAÇÕES')
inicio.grid(column=0,row=0,sticky="n",padx=10,pady=10)

#CONTEUDO

frame_conteudo = ctk.CTkFrame(janela)
frame_conteudo.grid_propagate(False)
frame_conteudo.grid_columnconfigure(0,weight=1)
frame_conteudo.grid_rowconfigure(0,weight=1)
frame_conteudo.grid(column=1, row=0, columnspan=5, rowspan=5, sticky="nsew",padx=20,pady=10)

conteudo = ctk.CTkLabel(frame_conteudo,text='CONTEUDO')
conteudo.grid(column=0,row=0,sticky="n",padx=10,pady=10)

janela.mainloop()