def selecionar_tudo_entry(event):
    event.widget.select_range(0, "end")
    event.widget.icursor("end")
    return "break"

def selecionar_tudo_textbox(event):
    event.widget.tag_add("sel", "1.0", "end-1c")
    event.widget.mark_set("insert", "1.0")
    event.widget.see("insert")
    return "break"

def configurar_entry(entry):
    entry.bind("<Control-a>", selecionar_tudo_entry)
    entry.bind("<Control-A>", selecionar_tudo_entry)

def configurar_textbox(textbox):
    textbox.bind("<Control-a>", selecionar_tudo_textbox)
    textbox.bind("<Control-A>", selecionar_tudo_textbox)