from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

doacao_entrada = Blueprint("doacao_entrada", __name__)

@doacao_entrada.route("/doacoes/entrada", methods=["GET", "POST"])
def registrar_entrada():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        origem = request.form.get("origem", "").strip()
        data = request.form.get("data", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not tipo or not data:
            flash("Preencha os campos obrigatórios: Tipo e Data.", "erro")
            return render_template("doacoes/entrada.html", dados=request.form)

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO doacoes (tipo, origem, data, observacoes, tipo_movimentacao)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo, origem, data, observacoes, "entrada"))
            conn.commit()

        flash("Doação de entrada registrada com sucesso!", "sucesso")
        return redirect(url_for("doacao_entrada.registrar_entrada"))

    return render_template("doacoes/entrada.html", dados=None)
