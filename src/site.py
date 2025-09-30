import webbrowser
import tkinter as tk

def endereco(area, top, botton):
    link = tk.Label(area, text="Desenvolvido por MHPS", bg="#B0E0E6", fg="blue", cursor="hand2")
    link.pack(pady=(top,botton))
    link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.mhps.com.br"))
