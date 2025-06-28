from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

voluntarios_cadastro = Blueprint("voluntarios_cadastro", __name__)

def capitalizar(texto):
    excecoes = {"da", "de", "do", "das", "dos"}
    return " ".join([
        p.capitalize() if p.lower() not in excecoes else p.lower()
        for p in texto.split()
    ])

@voluntarios_cadastro.route("/voluntarios/cadastro", methods=["GET", "POST"])
def cadastrar_voluntarios():
    if request.method == "POST":
        nome = capitalizar(request.form.get("nome", "").strip())
        contato = request.form.get("contato", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()

        if not nome or not contato:
            flash("Preencha todos os campos obrigatórios!", "erro")
            return render_template("voluntarios/cadastro.html", dados=request.form)

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voluntarios (nome, contato, data_nascimento)
                VALUES (?, ?, ?)
            """, (nome, contato, data_nascimento))
            conn.commit()

        flash("Voluntário cadastrado com sucesso!", "sucesso")
        return redirect(url_for("voluntarios_cadastro.cadastrar_voluntarios"))

    return render_template("voluntarios/cadastro.html", dados=None)
