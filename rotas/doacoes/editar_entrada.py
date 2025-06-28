from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

editar_entrada = Blueprint("editar_entrada", __name__)

@editar_entrada.route("/doacoes/editar_entrada/<int:doacao_id>", methods=["GET", "POST"])
def editar(doacao_id):
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            tipo = request.form.get("tipo", "").strip()
            origem = request.form.get("origem", "").strip()
            data = request.form.get("data", "").strip()
            observacoes = request.form.get("observacoes", "").strip()

            if not tipo or not origem or not data:
                flash("Preencha todos os campos obrigatórios.", "erro")
                return render_template("doacoes/editar_entrada.html", dados=request.form)

            cursor.execute("""
                UPDATE doacoes
                SET tipo = ?, origem = ?, data = ?, observacoes = ?
                WHERE id = ?
            """, (tipo, origem, data, observacoes, doacao_id))
            conn.commit()

            flash("Doação atualizada com sucesso!", "sucesso")
            return redirect(url_for("doacao_listagem.listar_doacoes"))

        # Método GET
        cursor.execute("SELECT * FROM doacoes WHERE id = ?", (doacao_id,))
        dados = cursor.fetchone()

        if not dados:
            flash("Doação não encontrada.", "erro")
            return redirect(url_for("doacao_listagem.listar_doacoes"))

        colunas = [desc[0] for desc in cursor.description]
        doacao = dict(zip(colunas, dados))

        return render_template("doacoes/editar_entrada.html", dados=doacao)
