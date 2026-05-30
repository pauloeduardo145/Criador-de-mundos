import customtkinter as ctk

ctk.set_appearance_mode("dark")

#JANELAS

janela = ctk.CTk()
janela.title("Criador de Mundos")
janela.geometry("1000x1000")
janela.attributes('-fullscreen', True)
janela.bind('<Escape>', lambda e: janela.attributes('-fullscreen', False))
janela.grid_columnconfigure(1, weight=1)

#INICIO

frame_inicio = ctk.CTkFrame(janela, width=300, height=500)
frame_inicio.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

inicio = ctk.CTkLabel(janela,text="INICIO")
inicio.grid(row=1, column=0, padx=100,pady=90)

menu = ctk.CTkLabel(janela,text='MENU')
menu.grid(row=1, column=1, padx=100,pady=90)


janela.mainloop()