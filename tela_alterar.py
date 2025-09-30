import tkinter as tk
import sqlcipher3.dbapi2 as sqlite
from db_utils import DB_FILENAME, try_open_with_key
import tela_main
import src.site

def tela_forcar_alteracao():
    win = tk.Tk()
    win.title("Cadastro de acessos 1.0 - mhps.com.br")
    win.geometry("400x300")
    win.configure(bg="#B0E0E6")

    tk.Label(win, text="Cadastro de Acessos", font=("Arial", 14, "bold"), bg="#B0E0E6").pack(pady=5)
    tk.Label(win, text="⚠️ A senha padrão '1234' está ativa.",
             font=("Arial", 12, "bold"), bg="#B0E0E6", fg="red").pack(pady=10)
    tk.Label(win, text="Por segurança, crie uma nova senha:", bg="#B0E0E6").pack()
    tk.Label(win, text="(Aceita letras, números e símbolos)", bg="#B0E0E6").pack()

    var1 = tk.StringVar()
    var2 = tk.StringVar()
    e1 = tk.Entry(win, textvariable=var1, show="*", width=25)
    e2 = tk.Entry(win, textvariable=var2, show="*", width=25)
    e1.pack(pady=5)
    e2.pack(pady=5)

    status = tk.Label(win, text="", bg="#B0E0E6", fg="red")
    status.pack()

    def confirmar():
        s1, s2 = var1.get(), var2.get()
        if not s1:
            status.config(text="Digite a nova senha.")
            return
        if s1 != s2:
            status.config(text="As senhas não conferem.")
            return
        if len(s1) < 4:
            status.config(text="Senha muito curta (mínimo 4 caracteres).")
            return
        try:
            conn = sqlite.connect(DB_FILENAME)
            cur = conn.cursor()
            cur.execute("PRAGMA key = '1234';")
            cur.execute("SELECT count(*) FROM sqlite_master;")
            cur.execute("PRAGMA rekey = %s;" % repr(s1))
            conn.commit()
            conn.close()

            if try_open_with_key(s1):
                import db_utils
                db_utils.DB_KEY = s1
                win.destroy()
                tela_main.start_main_app()
            else:
                status.config(text="Erro ao validar a nova senha.")
        except Exception as e:
            # aqui só mostra se a janela ainda existe
            if status.winfo_exists():
                status.config(text=f"Erro: {e}")

    tk.Button(win, text="Confirmar", command=confirmar).pack(pady=10)

    src.site.endereco(win, 5, 8)
    win.mainloop()

