from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

editar_saida = Blueprint("editar_saida", __name__)

@editar_saida.route("/doacoes/editar_saida/<int:doacao_id>", methods=["GET", "POST"])
def editar(doacao_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # POST: atualizar os dados
        if request.method == "POST":
            tipo = request.form.get("tipo", "").strip()
            beneficiario_id = request.form.get("beneficiario_id", "").strip()
            beneficiario_tipo = request.form.get("beneficiario_tipo", "").strip()
            data = request.form.get("data", "").strip()
            observacoes = request.form.get("observacoes", "").strip()

            if not tipo or not data:
                flash("Preencha todos os campos obrigatórios.", "erro")
                return redirect(request.url)

            if beneficiario_id and beneficiario_tipo:
                destino_id = beneficiario_id
                destino_tipo = beneficiario_tipo
            else:
                destino_id = None
                destino_tipo = None

            cursor.execute("""
                UPDATE doacoes
                SET tipo = ?, destino_id = ?, destino_tipo = ?, origem = NULL, data = ?, observacoes = ?
                WHERE id = ?
            """, (tipo, destino_id, destino_tipo, data, observacoes, doacao_id))

            conn.commit()
            flash("Doação de saída atualizada com sucesso!", "sucesso")
            return redirect(url_for("doacao_listagem.listar_doacoes"))

        # GET: carregar os dados existentes
        cursor.execute("SELECT * FROM doacoes WHERE id = ?", (doacao_id,))
        dados = cursor.fetchone()
        if not dados:
            flash("Doação não encontrada.", "erro")
            return redirect(url_for("doacao_listagem.listar_doacoes"))

        colunas = [desc[0] for desc in cursor.description]
        doacao = dict(zip(colunas, dados))

    return render_template("doacoes/editar_saida.html", dados=doacao)
