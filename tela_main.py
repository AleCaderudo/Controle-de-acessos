# tela_main.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from db_utils import get_conn, DB_FILENAME
import src.site

# variáveis globais internas
registro_editando = None
janela = None
formulario_cat = None
formulario_ref = None
formulario_user = None
formulario_passw = None
tree = None
status_label = None
botao_cadastrar = None
botao_cancelar = None
botoes = {}

def criar_menu_contexto(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Copiar", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Colar", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Recortar", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_separator()

    def selecionar_tudo():
        try:
            widget.select_range(0, tk.END)
        except Exception:
            # widget pode não suportar select_range
            pass

    menu.add_command(label="Selecionar tudo", command=selecionar_tudo)

    def mostrar_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    widget.bind("<Button-3>", mostrar_menu)  # botão direito

def limpar_formulario():
    try:
        if formulario_cat:
            formulario_cat.current(0)
    except Exception:
        pass
    try:
        if formulario_ref:
            formulario_ref.delete(0, tk.END)
        if formulario_user:
            formulario_user.delete(0, tk.END)
        if formulario_passw:
            formulario_passw.delete(0, tk.END)
    except Exception:
        pass

def grava_db():
    global registro_editando, botao_cadastrar, botao_cancelar
    if not os.path.exists(DB_FILENAME):
        messagebox.showerror("Erro", f"Banco '{DB_FILENAME}' não encontrado.")
        return

    try:
        conn = get_conn()
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível conectar ao DB: {e}")
        return

    cursor = conn.cursor()

    categoria = formulario_cat.get()
    refer = formulario_ref.get()
    usuario = formulario_user.get()
    senhas = formulario_passw.get()

    if registro_editando:  # Modo edição
        cursor.execute(
            "UPDATE Dados SET categoria=?, ref=?, user=?, passw=? WHERE id=?",
            (categoria, refer, usuario, senhas, registro_editando)
        )
        conn.commit()
        status_label.config(text=f"✏️ Registro ID {registro_editando} atualizado.")
        registro_editando = None
        botao_cadastrar.config(text="Cadastrar", command=grava_db)
        botao_cancelar.pack_forget()
    else:  # Novo cadastro
        cursor.execute(
            "INSERT INTO Dados (categoria, ref, user, passw) VALUES (?, ?, ?, ?)",
            (categoria, refer, usuario, senhas)
        )
        conn.commit()
        status_label.config(text=f"✅ Salvo: [{categoria}] {refer} | {usuario} | {senhas}")

    conn.close()
    limpar_formulario()
    exibe("Todos")

def exibe(categoria=None):
    # limpa tree
    for i in tree.get_children():
        tree.delete(i)

    if not os.path.exists(DB_FILENAME):
        status_label.config(text=f"❗ Banco '{DB_FILENAME}' não encontrado.")
        return

    try:
        conn = get_conn()
    except Exception as e:
        status_label.config(text=f"Erro ao abrir DB: {e}")
        return

    cursor = conn.cursor()
    if categoria and categoria != "Todos":
        cursor.execute("SELECT * FROM Dados WHERE categoria=? ORDER BY id", (categoria,))
    else:
        cursor.execute("SELECT * FROM Dados ORDER BY categoria, id")
    linhas = cursor.fetchall()
    conn.close()

    for r in linhas:
        # r esperado: (id, categoria, ref, user, passw)
        tree.insert("", tk.END, iid=r[0], values=(r[1], r[2], r[3], r[4]))

    status_label.config(text=f"✅ {len(linhas)} registros exibidos.")

    # destacar botão ativo
    for nome, botao in botoes.items():
        try:
            if nome == categoria:
                botao.config(bg="#87CEFA")
            else:
                botao.config(bg="SystemButtonFace")
        except Exception:
            pass

def excluir_registro():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um registro para excluir.")
        return

    item = selecionado[0]
    registro_id = int(item)

    valores = tree.item(item, "values")
    referencia = valores[1] if valores else f"ID {registro_id}"

    if not messagebox.askyesno("Confirmar", f"Excluir registro: {referencia}?"):
        return

    try:
        conn = get_conn()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao DB: {e}")
        return

    cursor = conn.cursor()
    cursor.execute("DELETE FROM Dados WHERE id=?", (registro_id,))
    conn.commit()
    conn.close()

    tree.delete(item)
    status_label.config(text=f"🗑️ Registro '{referencia}' excluído.")

def on_tree_click(event):
    global registro_editando, botao_cadastrar, botao_cancelar
    item_id = tree.identify_row(event.y)
    if not item_id:
        return
    col = tree.identify_column(event.x)
    try:
        col_index = int(col.replace("#", "")) - 1
    except Exception:
        col_index = None
    values = tree.item(item_id, "values")
    if not values:
        return

    # Copiar só se for Ref, Usuário ou Senha (col_index 1/2/3)
    if col_index in (1, 2, 3):
        valor = values[col_index]
        janela.clipboard_clear()
        janela.clipboard_append(str(valor))
        janela.update()
        status_label.config(text=f"'{valor}' copiado para a área de transferência.")

    # Sempre entra em modo edição
    registro_editando = int(item_id)
    try:
        formulario_cat.set(values[0])
    except Exception:
        pass
    formulario_ref.delete(0, tk.END)
    formulario_ref.insert(0, values[1])
    formulario_user.delete(0, tk.END)
    formulario_user.insert(0, values[2])
    formulario_passw.delete(0, tk.END)
    formulario_passw.insert(0, values[3])

    botao_cadastrar.config(text="Editar", command=grava_db)
    botao_cancelar.pack(padx=8)

def cancelar_edicao():
    global registro_editando
    registro_editando = None
    limpar_formulario()
    botao_cadastrar.config(text="Cadastrar", command=grava_db)
    botao_cancelar.pack_forget()
    status_label.config(text="Edição cancelada.")

# --- Construção da janela principal ---
def start_main_app():
    global janela, formulario_cat, formulario_ref, formulario_user, formulario_passw
    global tree, status_label, botao_cadastrar, botao_cancelar, botoes

    janela = tk.Tk()
    janela.title("Cadastro de Acessos 1.0 mhps.com.br")
    janela.geometry("900x600")
    janela.configure(bg="#B0E0E6")

    tk.Label(janela, text="Cadastro de Acessos", font=("Arial", 14, "bold"), bg="#B0E0E6").pack(pady=5)

    frame_form = tk.Frame(janela, bg="#B0E0E6")
    frame_form.pack(pady=3)

    # Categoria (Combobox)
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left")
    tk.Label(frame_unico, text="Categoria", font=("Arial", 12), bg="#B0E0E6").pack(padx=2)
    categorias = ["Site", "E-mail", "Programas", "Outros"]
    formulario_cat = ttk.Combobox(frame_unico, values=categorias, state="readonly", width=12)
    formulario_cat.pack(side="left", padx=2)
    formulario_cat.current(0)

    # Referência
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left")
    tk.Label(frame_unico, text="Referência", font=("Arial", 12), bg="#B0E0E6").pack(padx=2)
    formulario_ref = tk.Entry(frame_unico,  width=40)
    formulario_ref.pack(side="left", padx=2)
    criar_menu_contexto(formulario_ref)

    # Usuário
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left", padx=12)
    tk.Label(frame_unico, text="Usuário", font=("Arial", 12), bg="#B0E0E6").pack(padx=2)
    formulario_user = tk.Entry(frame_unico,  width=30)
    formulario_user.pack(side="left", padx=2)
    criar_menu_contexto(formulario_user)

    # Senha
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left")
    tk.Label(frame_unico, text="Senha", font=("Arial", 12), bg="#B0E0E6").pack(padx=2)
    formulario_passw = tk.Entry(frame_unico)
    formulario_passw.pack(side="left", padx=2)
    criar_menu_contexto(formulario_passw)

    # Botão cadastrar
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left")
    tk.Label(frame_unico, text="", bg="#B0E0E6").pack(padx=2)
    botao_cadastrar = tk.Button(frame_unico, text="Cadastrar", command=grava_db)
    botao_cadastrar.pack(padx=8)

    # Botão cancelar cadastro (invisível até edição)
    frame_unico = tk.Frame(frame_form, bg="#B0E0E6")
    frame_unico.pack(side="left")
    tk.Label(frame_unico, text="", bg="#B0E0E6").pack(padx=2)
    botao_cancelar = tk.Button(frame_unico, text="Cancelar edição", command=cancelar_edicao, fg="red")
    botao_cancelar.pack(padx=8)
    botao_cancelar.pack_forget()

    # Botões de filtro
    frame_buttons = tk.Frame(janela, bg="#B0E0E6")
    frame_buttons.pack(pady=8)

    botoes = {}
    categorias_botoes = {
        "Todos": "Todos",
        "Sites": "Site",
        "E-mails": "E-mail",
        "Programas": "Programas",
        "Outros": "Outros"
    }

    for texto, categoria in categorias_botoes.items():
        b = tk.Button(frame_buttons, text=texto, command=lambda c=categoria: exibe(c))
        b.pack(side="left", padx=8)
        botoes[categoria] = b

    tk.Button(frame_buttons, text="🗑️ Excluir selecionado", fg="red", command=excluir_registro).pack(side="left", padx=8)

    # Status
    status_label = tk.Label(janela, text="", bg="#B0E0E6", font=("Arial", 10), anchor="w", justify="left")
    status_label.pack(padx=10, pady=(0,10))

    # Treeview
    frame_tree = tk.Frame(janela)
    frame_tree.pack(padx=10, pady=10, fill="both", expand=True)

    cols = ("Categoria", "Ref", "Usuário", "Senha")
    tree = ttk.Treeview(frame_tree, columns=cols, show="headings", selectmode="browse")
    for c in cols:
        tree.heading(c, text=c)
        if c == "Categoria":
            tree.column(c, width=80, anchor="center")
        elif c == "Ref":
            tree.column(c, width=260, anchor="center")
        elif c == "Usuário":
            tree.column(c, width=160, anchor="center")
        else:
            tree.column(c, width=160, anchor="center")

    vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame_tree.grid_rowconfigure(0, weight=1)
    frame_tree.grid_columnconfigure(0, weight=1)

    tree.bind("<ButtonRelease-1>", on_tree_click)

    # carrega dados iniciais
    exibe("Todos")

    src.site.endereco(janela, 5, 5)

    janela.mainloop()

