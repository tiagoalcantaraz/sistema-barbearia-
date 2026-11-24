import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = "troque-esta-chave"
DB = "barbearia.db"
SERVICOS = {"Corte": 40, "Barba": 30, "Corte + Barba": 65, "Sobrancelha": 15}
HORARIOS = [f"{h:02d}:{m}" for h in range(9, 19) for m in ("00", "30") if h != 12]


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def fechar(_):
    c = g.pop("db", None)
    if c:
        c.close()


def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS agendamentos(
            id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT NOT NULL,
            telefone TEXT NOT NULL, servico TEXT NOT NULL, data TEXT NOT NULL,
            hora TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Agendado',
            UNIQUE(data, hora))""")
        c.execute("""CREATE TABLE IF NOT EXISTS clientes(
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
            telefone TEXT NOT NULL UNIQUE, email TEXT)""")


@app.route("/")
def index():
    return render_template("index.html", servicos=SERVICOS)


@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    hoje = date.today().isoformat()
    if request.method == "POST":
        f = {k: request.form.get(k, "").strip() for k in ("cliente", "telefone", "servico", "data", "hora")}
        if not all(f.values()) or f["servico"] not in SERVICOS or f["hora"] not in HORARIOS:
            flash("Preencha todos os campos corretamente.", "erro")
        elif f["data"] < hoje:
            flash("Não é possível agendar em data passada.", "erro")
        elif datetime.strptime(f["data"], "%Y-%m-%d").weekday() == 6:
            flash("A barbearia não abre aos domingos.", "erro")
        else:
            try:
                db().execute("INSERT INTO agendamentos(cliente,telefone,servico,data,hora) VALUES(?,?,?,?,?)", tuple(f.values()))
                db().commit()
                flash("Agendamento confirmado!", "ok")
                return redirect(url_for("agendar"))
            except sqlite3.IntegrityError:
                flash("Esse horário já está ocupado. Escolha outro.", "erro")
    ocupados = {}
    for r in db().execute("SELECT data,hora FROM agendamentos WHERE status!='Cancelado' AND data>=?", (hoje,)):
        ocupados.setdefault(r["data"], []).append(r["hora"])
    clientes = db().execute("SELECT nome, telefone FROM clientes ORDER BY nome").fetchall()
    return render_template("agendar.html", servicos=SERVICOS, horarios=HORARIOS, hoje=hoje, ocupados=ocupados, clientes=clientes)


@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        tel = "".join(ch for ch in request.form.get("telefone", "") if ch.isdigit())
        email = request.form.get("email", "").strip()
        if not nome or len(tel) < 10:
            flash("Informe o nome e um telefone válido com DDD.", "erro")
        else:
            try:
                db().execute("INSERT INTO clientes(nome,telefone,email) VALUES(?,?,?)", (nome, tel, email))
                db().commit()
                flash("Cliente cadastrado!", "ok")
                return redirect(url_for("clientes"))
            except sqlite3.IntegrityError:
                flash("Já existe um cliente com esse telefone.", "erro")
    lista = db().execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    return render_template("clientes.html", clientes=lista)


@app.route("/clientes/<int:id>/excluir", methods=["POST"])
def excluir_cliente(id):
    db().execute("DELETE FROM clientes WHERE id=?", (id,))
    db().commit()
    flash("Cliente removido.", "ok")
    return redirect(url_for("clientes"))


@app.route("/admin")
def admin():
    ag = db().execute("SELECT * FROM agendamentos ORDER BY data, hora").fetchall()
    total = sum(SERVICOS[a["servico"]] for a in ag if a["status"] == "Concluído")
    return render_template("admin.html", ags=ag, servicos=SERVICOS, total=total, hoje=date.today().isoformat())


@app.route("/admin/<int:id>/<acao>", methods=["POST"])
def mudar(id, acao):
    status = {"cancelar": "Cancelado", "concluir": "Concluído"}.get(acao)
    if status:
        db().execute("UPDATE agendamentos SET status=? WHERE id=?", (status, id))
        db().commit()
        flash(f"Agendamento {status.lower()}.", "ok")
    return redirect(url_for("admin"))


init_db()
if __name__ == "__main__":
    app.run(debug=True)
