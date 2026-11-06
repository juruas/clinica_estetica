
from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave_sistema_clinica"

# Conexão com o banco de dados
def conectar_banco():
    conexao = sqlite3.connect("clinica.db")
    conexao.row_factory = sqlite3.Row
    return conexao

# Criação das tabelas
def criar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (servico_id) REFERENCES servicos(id)
        )
    """)

    conexao.commit()
    conexao.close()

# Página inicial
@app.route("/")
def inicio():
    return render_template("index.html")

# Página de clientes
@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

# Cadastro de clientes
@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():
    nome = request.form["nome"]
    telefone = request.form["telefone"]
    email = request.form["email"]

    conexao = conectar_banco()
    conexao.execute("""
        INSERT INTO clientes (nome, telefone, email)
        VALUES (?, ?, ?)
    """, (nome, telefone, email))

    conexao.commit()
    conexao.close()

    flash("Cliente cadastrado com sucesso!")
    return redirect("/clientes")

# Página de serviços
@app.route("/servicos")
def servicos():
    return render_template("servicos.html")

# Cadastro de serviços
@app.route("/cadastrar_servico", methods=["POST"])
def cadastrar_servico():
    nome = request.form["nome"]
    descricao = request.form["descricao"]
    preco = request.form["preco"]

    conexao = conectar_banco()
    conexao.execute("""
        INSERT INTO servicos (nome, descricao, preco)
        VALUES (?, ?, ?)
    """, (nome, descricao, preco))

    conexao.commit()
    conexao.close()

    flash("Serviço cadastrado com sucesso!")
    return redirect("/servicos")

# Página de agendamentos
@app.route("/agendamentos")
def agendamentos():
    conexao = conectar_banco()

    clientes = conexao.execute(
        "SELECT * FROM clientes ORDER BY nome"
    ).fetchall()

    servicos = conexao.execute(
        "SELECT * FROM servicos ORDER BY nome"
    ).fetchall()

    conexao.close()

    return render_template(
        "agendamentos.html",
        clientes=clientes,
        servicos=servicos
    )

# Cadastro de agendamentos
@app.route("/cadastrar_agendamento", methods=["POST"])
def cadastrar_agendamento():
    cliente_id = request.form["cliente_id"]
    servico_id = request.form["servico_id"]
    data = request.form["data"]
    horario = request.form["horario"]

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO agendamentos
        (cliente_id, servico_id, data, horario)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, servico_id, data, horario))

    conexao.commit()
    conexao.close()

    flash("Agendamento realizado com sucesso!")
    return redirect("/agendamentos")

# Consulta de todos os registros
@app.route("/consultas")
def consultas():
    conexao = conectar_banco()

    clientes = conexao.execute(
        "SELECT * FROM clientes ORDER BY nome"
    ).fetchall()

    servicos = conexao.execute(
        "SELECT * FROM servicos ORDER BY nome"
    ).fetchall()

    agendamentos = conexao.execute("""
        SELECT
            agendamentos.data,
            agendamentos.horario,
            clientes.nome AS cliente,
            servicos.nome AS servico
        FROM agendamentos
        INNER JOIN clientes
            ON agendamentos.cliente_id = clientes.id
        INNER JOIN servicos
            ON agendamentos.servico_id = servicos.id
        ORDER BY agendamentos.data, agendamentos.horario
    """).fetchall()

    conexao.close()

    return render_template(
        "consultas.html",
        clientes=clientes,
        servicos=servicos,
        agendamentos=agendamentos
    )

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
