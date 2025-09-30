import tkinter as tk
from db_utils import try_open_with_key, DB_KEY
import tela_main
import src.site

def criar_tela_login():
    login = tk.Tk()
    login.title("Login - Acesso ao Sistema")
    login.resizable(False, False)
    login.geometry("460x520")
    login.configure(bg="#B0E0E6")

    password_var = tk.StringVar()

    tk.Label(login, text="Cadastro de Acessos", font=("Arial", 14, "bold"), bg="#B0E0E6").pack(pady=5)
    # header
    tk.Label(login, text="Digite sua senha/PIN:", bg="#B0E0E6", font=("Arial", 12)).pack(pady=(10,4))

    entry_frame = tk.Frame(login, bg="#B0E0E6")
    entry_frame.pack(pady=(0,6))

    password_entry = tk.Entry(entry_frame, textvariable=password_var, font=("Arial", 16), show="*", justify="center", width=22)
    password_entry.grid(row=0, column=0, padx=(0,6))

    # show/hide toggle
    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        show_var.set(not show_var.get())
        password_entry.config(show="" if show_var.get() else "*")
        show_var.set(not show_var.get())
    tk.Button(entry_frame, text="👁", width=3, command=toggle_show).grid(row=0, column=1)

    status_pass = tk.Label(login, text="",  bg="#B0E0E6", font=("Arial", 11), fg="red")
    status_pass.pack(padx=10, pady=(0,6), fill="x")

    # helper: insert char
    def insert_char(s):
        password_entry.insert(tk.END, s)
        password_entry.focus_set()

    def backspace():
        cur = password_var.get()
        password_var.set(cur[:-1])
        password_entry.focus_set()

    def clear_all():
        password_var.set("")
        password_entry.focus_set()

    def paste_clipboard():
        try:
            txt = login.clipboard_get()
            password_entry.insert(tk.END, txt)
        except Exception:
            status_pass.config(text="Área de transferência vazia.")
        password_entry.focus_set()

    # layouts: 'abc' (lower), 'ABC' (upper), '123', 'sym'
    current_layout = tk.StringVar(value="abc")
    shift_on = tk.BooleanVar(value=False)

    letters_lower = [
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm")
    ]
    letters_upper = [[c.upper() for c in row] for row in letters_lower]
    numbers = list("1234567890")
    symbols = list("!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~")

    # frame teclado
    teclado_frame = tk.Frame(login, bg="#B0E0E6")
    teclado_frame.pack(pady=6)

    # função para desenhar teclado conforme layout
    buttons_refs = []
    def render_layout():
        # limpa frame
        for w in teclado_frame.winfo_children():
            w.destroy()
        buttons_refs.clear()

        layout = current_layout.get()
        if layout in ("abc", "ABC"):
            rows = letters_upper if layout == "ABC" else letters_lower
            # primeira linha
            for r_idx, row in enumerate(rows):
                row_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
                row_frame.pack()
                for ch in row:
                    b = tk.Button(row_frame, text=ch, width=4, height=2, command=lambda c=ch: insert_char(c))
                    b.pack(side="left", padx=2, pady=2)
                    buttons_refs.append(b)
            # linha de espaço e ações
            action_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
            action_frame.pack(pady=(6,0))
            tk.Button(action_frame, text="Shift", width=6, command=toggle_shift).pack(side="left", padx=4)
            tk.Button(action_frame, text="123", width=6, command=lambda: switch_layout("123")).pack(side="left", padx=4)
            tk.Button(action_frame, text="Sym", width=6, command=lambda: switch_layout("sym")).pack(side="left", padx=4)
            tk.Button(action_frame, text="Espaço", width=14, command=lambda: insert_char(" ")).pack(side="left", padx=4)
            tk.Button(action_frame, text="←", width=6, command=backspace).pack(side="left", padx=4)

        elif layout == "123":
            row_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
            row_frame.pack()
            for n in numbers[:5]:
                b = tk.Button(row_frame, text=n, width=4, height=2, command=lambda c=n: insert_char(c))
                b.pack(side="left", padx=2, pady=2)
            row_frame2 = tk.Frame(teclado_frame, bg="#B0E0E6")
            row_frame2.pack()
            for n in numbers[5:]:
                b = tk.Button(row_frame2, text=n, width=4, height=2, command=lambda c=n: insert_char(c))
                b.pack(side="left", padx=2, pady=2)

            action_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
            action_frame.pack(pady=(6,0))
            tk.Button(action_frame, text="abc", width=6, command=lambda: switch_layout("abc")).pack(side="left", padx=4)
            tk.Button(action_frame, text="Sym", width=6, command=lambda: switch_layout("sym")).pack(side="left", padx=4)
            tk.Button(action_frame, text="Espaço", width=14, command=lambda: insert_char(" ")).pack(side="left", padx=4)
            tk.Button(action_frame, text="←", width=6, command=backspace).pack(side="left", padx=4)

        elif layout == "sym":
            # mostra símbolos em várias linhas
            per_row = 8
            for i in range(0, len(symbols), per_row):
                row_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
                row_frame.pack()
                for sym in symbols[i:i+per_row]:
                    b = tk.Button(row_frame, text=sym, width=4, height=2, command=lambda c=sym: insert_char(c))
                    b.pack(side="left", padx=2, pady=2)
            action_frame = tk.Frame(teclado_frame, bg="#B0E0E6")
            action_frame.pack(pady=(6,0))
            tk.Button(action_frame, text="abc", width=6, command=lambda: switch_layout("abc")).pack(side="left", padx=4)
            tk.Button(action_frame, text="123", width=6, command=lambda: switch_layout("123")).pack(side="left", padx=4)
            tk.Button(action_frame, text="Espaço", width=14, command=lambda: insert_char(" ")).pack(side="left", padx=4)
            tk.Button(action_frame, text="←", width=6, command=backspace).pack(side="left", padx=4)

    def switch_layout(new):
        # ajustar o valor do layout; respeita shift para alternar ABC/abc
        if new == "abc":
            current_layout.set("ABC" if shift_on.get() else "abc")
        else:
            current_layout.set(new)
        render_layout()

    def toggle_shift():
        # alterna maiúsculas/minúsculas quando em layout ABC/abc
        shift_on.set(not shift_on.get())
        if current_layout.get() in ("abc", "ABC"):
            current_layout.set("ABC" if shift_on.get() else "abc")
        render_layout()

    # rodar primeira vez
    render_layout()

    # controles extras (cole, limpar, confirmar)
    controle_frame = tk.Frame(login, bg="#B0E0E6")
    controle_frame.pack(pady=8)

    tk.Button(controle_frame, text="Colar", width=8, command=paste_clipboard).pack(side="left", padx=6)
    tk.Button(controle_frame, text="Limpar", width=8, command=clear_all).pack(side="left", padx=6)
    tk.Button(controle_frame, text="←", width=6, command=backspace).pack(side="left", padx=6)

    def verificar_senha():
        entered = password_var.get()
        if not entered:
            status_pass.config(text="Digite a senha/PIN.")
            return
        ok = try_open_with_key(entered)
        if ok:
            import db_utils
            db_utils.DB_KEY = entered
            login.destroy()
            tela_main.start_main_app()
        else:
            status_pass.config(text="Senha incorreta")
            password_var.set("")

     # botão OK
    tk.Button(login, text="OK", font=("Arial", 12, "bold"), width=18, height=2, command=verificar_senha).pack(pady=(6,12))

    src.site.endereco(login, 20, 8)

    # foco na entry
    password_entry.focus_set()
    login.mainloop()
