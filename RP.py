import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from datetime import datetime, timedelta
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
import csv
import os
from PIL import Image, ImageTk

# Função para converter string de hora para timedelta
def tempo_str_para_timedelta(t):
    h, m = map(int, t.split(":"))
    return timedelta(hours=h, minutes=m)

# Função para calcular hora extra
def calcular_hora_extra(regime, entrada1, saida1, entrada2, saida2):
    t1 = tempo_str_para_timedelta(entrada1)
    t2 = tempo_str_para_timedelta(saida1)
    t3 = tempo_str_para_timedelta(entrada2)
    t4 = tempo_str_para_timedelta(saida2)

    total = (t2 - t1) + (t4 - t3)

    if regime == "Reduzido":
        carga = timedelta(hours=6, minutes=30)
    else:
        carga = timedelta(hours=8)

    diff = total - carga

    if diff.total_seconds() == 0:
        return "0:00"

    sinal = "+" if diff.total_seconds() > 0 else "-"
    return f"{sinal}{str(abs(diff))[:-3]}"

# Função para criar seletores de hora com seleção automática e navegação com Enter
def criar_seletor_horario(parent, tooltip_text):
    hora_var = tk.StringVar(value="00")
    minuto_var = tk.StringVar(value="00")

    frame = ttk.Frame(parent)

    def validate_input(text):
        return text.isdigit() and len(text) <= 2 or text == ""

    vcmd = (frame.register(validate_input), '%P')

    spn_hora = ttk.Spinbox(frame, from_=0, to=23, width=3, textvariable=hora_var,
                           wrap=True, format="%02.0f", justify="center",
                           validate="key", validatecommand=vcmd)
    spn_hora.pack(side=tk.LEFT)

    ttk.Label(frame, text=":").pack(side=tk.LEFT)

    spn_minuto = ttk.Spinbox(frame, from_=0, to=59, width=4, textvariable=minuto_var,
                             wrap=True, format="%02.0f", justify="center",
                             validate="key", validatecommand=vcmd)
    spn_minuto.pack(side=tk.LEFT)

    ToolTip(spn_hora, tooltip_text)
    ToolTip(spn_minuto, tooltip_text)

    def select_all(event):
        event.widget.selection_range(0, tk.END)
        return 'break'

    spn_hora.bind("<FocusIn>", select_all)
    spn_minuto.bind("<FocusIn>", select_all)

    def focus_next(event):
        event.widget.tk_focusNext().focus()
        return "break"

    spn_hora.bind("<Return>", focus_next)
    spn_minuto.bind("<Return>", focus_next)

    def get_horario():
        return f"{hora_var.get()}:{minuto_var.get()}"

    return frame, get_horario, hora_var, minuto_var, spn_hora, spn_minuto

DATA_FILE = "registros.csv"

def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

def salvar_dados_csv(dados):
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(dados)

def mostrar_erro_centralizado(mensagem, titulo="Erro"):
    # Cria uma janela filha modal
    erro_win = tk.Toplevel(app)
    erro_win.title(titulo)
    erro_win.resizable(False, False)

    # Bloqueia a interface principal
    erro_win.transient(app)
    erro_win.grab_set()

    # Mensagem no centro da janela
    lbl = ttk.Label(erro_win, text=mensagem, anchor="center", justify="center", padding=15)
    lbl.pack()

    # Botão para fechar a janela
    btn = ttk.Button(erro_win, text="OK", command=erro_win.destroy)
    btn.pack(pady=10)

    # Calcula posição central da janela erro_win em relação ao app
    app.update_idletasks()
    largura = erro_win.winfo_reqwidth()
    altura = erro_win.winfo_reqheight()

    pos_x = app.winfo_x() + (app.winfo_width() // 2) - (largura // 2)
    pos_y = app.winfo_y() + (app.winfo_height() // 2) - (altura // 2)

    erro_win.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    erro_win.wait_window()  # Espera o usuário fechar a janela

app = ttk.Window(themename="cosmo")
app.title("Registro de Ponto")
app.geometry('920x415')
app.resizable(False, False)

# Definir estilo Danger para destacar erros
style = ttk.Style()
style.configure("Danger.TEntry", foreground="red", bordercolor="red", borderwidth=2)
style.configure("Danger.TSpinbox", foreground="red", bordercolor="red", borderwidth=2)

def mostrar_erro(mensagem, campo=None):
    # Destaca o campo em vermelho, se fornecido
    if campo:
        estilo_original = campo.cget("style")
        campo.configure(style="Danger.TEntry" if isinstance(campo, ttk.Entry) else "Danger.TSpinbox")

    # Janela modal centralizada
    mostrar_erro_centralizado(mensagem, "Erro!")

    # Remove destaque
    if campo:
        campo.configure(style=estilo_original)
    # Após fechar, foca no campo
    if campo:
        campo.focus_set()

def carregar_imagem(caminho, tamanho=(30, 30)):
    imagem = Image.open(caminho)
    imagem = imagem.resize(tamanho, Image.LANCZOS)
    return ImageTk.PhotoImage(imagem)

def ajustar_campos_por_regime(event=None):
    regime = regime_var.get()
    if regime == "PT":
        entrada_fn_hora.set("12")
        saida_almoco_hora.set("16")
        entrada_almoco_hora.set("17")
        saida_final_hora.set("21")
    elif regime == "PM":
        entrada_fn_hora.set("08")
        saida_almoco_hora.set("12")
        entrada_almoco_hora.set("13")
        saida_final_hora.set("19")
    elif regime == "Folga":
        entrada_fn_hora.set("00")
        saida_almoco_hora.set("00")
        entrada_almoco_hora.set("00")
        saida_final_hora.set("00")
        salvar()

img_addponto = carregar_imagem("assets/img_addponto.png")
img_editponto = carregar_imagem("assets/img_editponto.png")
img_delponto = carregar_imagem("assets/img_delponto.png")

regime_var = tk.StringVar()
datas_utilizadas = set()

# Frame lateral à direita
frame_lateral = ttk.Frame(app, padding=10)
frame_lateral.place(x=750, y=1, width=165, height=450)

ttk.Label(frame_lateral, text="Data:").pack(anchor="w")
data_entry = ttk.DateEntry(frame_lateral, width=14)
data_entry.pack(pady=(0, 5))

ttk.Separator(frame_lateral, orient="horizontal").pack(fill="x", pady=5)

ttk.Label(frame_lateral, text="Regime:").pack(anchor="w")
regime_combo = ttk.Combobox(frame_lateral, textvariable=regime_var,
                             values=["PM", "PT", "Reduzido", "Folga"],
                             state="readonly", width=16)
regime_combo.pack(pady=(0, 5))
regime_combo.bind("<<ComboboxSelected>>", ajustar_campos_por_regime)

ttk.Separator(frame_lateral, orient="horizontal").pack(fill="x", pady=5)

entrada_widget, entrada_fn, entrada_fn_hora, entrada_fn_minuto, spn_entrada_hora, spn_entrada_minuto = criar_seletor_horario(frame_lateral, "Horário de entrada")
saida_almoco_widget, saida_almoco_fn, saida_almoco_hora, saida_almoco_minuto, spn_saida_almoco_hora, spn_saida_almoco_minuto = criar_seletor_horario(frame_lateral, "Saída para o almoço")
entrada_almoco_widget, entrada_almoco_fn, entrada_almoco_hora, entrada_almoco_minuto, spn_entrada_almoco_hora, spn_entrada_almoco_minuto = criar_seletor_horario(frame_lateral, "Retorno do almoço")
saida_final_widget, saida_final_fn, saida_final_hora, saida_final_minuto, spn_saida_final_hora, spn_saida_final_minuto = criar_seletor_horario(frame_lateral, "Saída final")

for texto, widget in [
    ("Entrada:", entrada_widget),
    ("Intervalo:", saida_almoco_widget),
    ("Retorno:", entrada_almoco_widget),
    ("Saída:", saida_final_widget),
]:
    ttk.Label(frame_lateral, text=texto).pack(anchor="w")
    widget.pack(pady=(0, 5), padx=(10,0), fill="x")

# Ajuste da Treeview para caber ao lado esquerdo
total_width = 720
columns = ("Data", "Regime", "Entrada", "Intervalo", "Retorno", "Saída", "Hora Extra")
num_cols = len(columns)
col_width = total_width // num_cols  # largura uniforme para cada coluna

tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=col_width, anchor="center", stretch=False)  # stretch False = sem redimensionar

tree.place(x=10, y=18, width=total_width, height=340)

ttk.Separator(frame_lateral, orient="horizontal").pack(fill="x", pady=5)

# Botões
btn_frame = ttk.Frame(app)
btn_frame.place(x=10, y=390, width=900, height=50, anchor="w")

salvar_lbl = ttk.Label(btn_frame, image=img_addponto, cursor="hand2")
salvar_lbl.place(x=780, y=20, anchor="center")
salvar_lbl.bind("<Button-1>", lambda e: salvar())
ToolTip(salvar_lbl, "Salvar registro")

editar_lbl = ttk.Label(btn_frame, image=img_editponto, cursor="hand2")
editar_lbl.place(x=825, y=20, anchor="center")
editar_lbl.bind("<Button-1>", lambda e: editar())
ToolTip(editar_lbl, "Editar registro selecionado")

excluir_lbl = ttk.Label(btn_frame, image=img_delponto, cursor="hand2")
excluir_lbl.place(x=870, y=20, anchor="center")
excluir_lbl.bind("<Button-1>", lambda e: excluir())
ToolTip(excluir_lbl, "Excluir registro selecionado")

saldo_label = ttk.Label(btn_frame, text="")
saldo_label.place(x=610, y=10, height=30)

def impedir_redimensionamento(event):
    # Sempre resetar para os tamanhos originais fixos
    for col in columns:
        tree.column(col, width=col_width, stretch=False)

# Bindar clique no cabeçalho
tree.heading("#0", command=lambda: None)  # Para prevenir seleção da coluna índice 0
for col in columns:
    tree.heading(col, command=lambda c=col: None)  # Desativa o clique que poderia redimensionar

# Captura evento de clique no cabeçalho
tree.bind("<ButtonRelease-1>", impedir_redimensionamento)

def salvar():
    d = data_entry.entry.get()
    if d in datas_utilizadas:
        mostrar_erro(f"A data {d} está cadastrada!", data_entry.entry)
        return

    r = regime_var.get()
    if not r:
        mostrar_erro("Por favor, selecione o regime de trabalho.", regime_combo)
        return

    ent1 = entrada_fn()
    sai1 = saida_almoco_fn()
    ent2 = entrada_almoco_fn()
    sai2 = saida_final_fn()

    t_ent1 = tempo_str_para_timedelta(ent1)
    t_sai1 = tempo_str_para_timedelta(sai1)
    t_ent2 = tempo_str_para_timedelta(ent2)
    t_sai2 = tempo_str_para_timedelta(sai2)
    hora_extra_str = "0:00"

    if r != "Folga":
        if t_ent1 == t_sai1:
            mostrar_erro("Os horários Entrada e Intervalo não podem ser iguais.", spn_entrada_hora)
            return
        if t_sai1 <= t_ent1:
            mostrar_erro("O horário de Retorno deve ser maior que o de Intervalo.", spn_saida_almoco_hora)
            return
        if t_ent2 <= t_sai1 or t_ent2 <= t_ent1:
            mostrar_erro("O horário de Retorno deve ser maior que Entrada e Intervalo.", spn_entrada_almoco_hora)
            return
        if (t_ent2 - t_sai1) < timedelta(minutes=30):
            mostrar_erro("Intervalo deve ser superior a 30 minutos.", spn_entrada_almoco_hora)
            return
        if t_sai2 <= max(t_ent1, t_sai1, t_ent2):
            mostrar_erro("Saída deve ser o superior aos demais horários.", spn_saida_final_hora)
            return

        hora_extra_str = calcular_hora_extra(r, ent1, sai1, ent2, sai2)

    tag = "positivo" if hora_extra_str.startswith("+") else "negativo"
    tree.insert("", tk.END, values=(d, r, ent1, sai1, ent2, sai2, hora_extra_str), tags=(tag,))
    datas_utilizadas.add(d)

    dados = [tree.item(child)['values'] for child in tree.get_children()]
    dados.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))

    for i in tree.get_children():
        tree.delete(i)
    for linha in dados:
        tag = "positivo" if linha[6].startswith("+") else "negativo"
        tree.insert("", tk.END, values=linha, tags=(tag,))

    salvar_dados_csv(dados)
    excluir_lbl.config(state="disabled")
    editar_lbl.config(state="disabled")
    atualizar_saldo_total()

def excluir():
    selecionado = tree.selection()
    if not selecionado:
        mostrar_erro("Selecione um registro para excluir.")
        return
    for item in selecionado:
        data_removida = tree.item(item)['values'][0]
        datas_utilizadas.discard(data_removida)
        tree.delete(item)

    dados = [tree.item(child)['values'] for child in tree.get_children()]
    salvar_dados_csv(dados)
    excluir_lbl.config(state="disabled")
    editar_lbl.config(state="disabled")
    atualizar_saldo_total()

def editar():
    selecionado = tree.selection()
    if not selecionado:
        mostrar_erro("Selecione um registro para editar.")
        return
    item = selecionado[0]
    valores = tree.item(item)['values']

    datas_utilizadas.discard(valores[0])

    data_entry.entry.delete(0, tk.END)
    data_entry.entry.insert(0, valores[0])

    regime_var.set(valores[1])
    entrada_fn_hora.set(valores[2].split(":")[0])
    saida_almoco_hora.set(valores[3].split(":")[0])
    entrada_almoco_hora.set(valores[4].split(":")[0])
    saida_final_hora.set(valores[5].split(":")[0])
    editar_lbl.config(state="disabled")
    tree.delete(item)
    atualizar_saldo_total()

def atualizar_saldo_total():
    total = timedelta()
    for item in tree.get_children():
        hora_extra_str = tree.item(item)['values'][-1]
        sinal = hora_extra_str[0]
        tempo_str = hora_extra_str[1:] if sinal in "+-" else hora_extra_str
        horas, minutos = map(int, tempo_str.split(":"))
        delta = timedelta(hours=horas, minutes=minutos)
        if sinal == "-":
            total -= delta
        else:
            total += delta

    horas, resto = divmod(abs(total).seconds, 3600)
    minutos = resto // 60
    sinal_total = "-" if total.total_seconds() < 0 else ""
    resultado_str = f"{sinal_total}{horas}:{minutos:02}"
    saldo_label.config(text=f"Saldo de Horas: {resultado_str}")
    if total.total_seconds() > 0:
        saldo_label.config(foreground="green")
    elif total.total_seconds() < 0:
        saldo_label.config(foreground="red")
    else:
        saldo_label.config(foreground="black")

for linha in carregar_dados():
    tag = "positivo" if linha[6].startswith("+") else "negativo"
    tree.insert("", tk.END, values=linha, tags=(tag,))
    datas_utilizadas.add(linha[0])
atualizar_saldo_total()

# Atalhos de teclado
def atalho_salvar(event=None):
    salvar()

def atalho_excluir(event=None):
    if not tree.selection():
        Messagebox.show_error("Selecione um registro para excluir.", "Erro!")
        return
    excluir()

def atalho_editar(event=None):
    if not tree.selection():
        Messagebox.show_error("Selecione um registro para editar.","Erro!")
        return
    editar()

app.bind("<Control-s>", atalho_salvar)
app.bind("<Control-S>", atalho_salvar)

app.bind("<Control-d>", atalho_excluir)
app.bind("<Control-D>", atalho_excluir)

app.bind("<Control-e>", atalho_editar)
app.bind("<Control-E>", atalho_editar)

app.mainloop()
