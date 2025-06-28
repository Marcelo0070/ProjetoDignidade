from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

doacao_saida = Blueprint("doacao_saida", __name__)

@doacao_saida.route("/doacoes/saida", methods=["GET", "POST"])
def registrar_saida():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        beneficiario_id = request.form.get("beneficiario_id", "").strip()
        beneficiario_tipo = request.form.get("beneficiario_tipo", "").strip()
        data = request.form.get("data", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        if not tipo or not beneficiario_id or not beneficiario_tipo or not data:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("doacoes/saida.html", dados=request.form)

        with conectar() as conn:
            cursor = conn.cursor()

            # Verifica se o beneficiário existe
            if beneficiario_tipo == "pessoa":
                cursor.execute("SELECT id FROM pessoas WHERE id = ?", (beneficiario_id,))
            elif beneficiario_tipo == "familia":
                cursor.execute("SELECT id FROM familias WHERE id = ?", (beneficiario_id,))
            else:
                flash("Tipo de beneficiário inválido.", "erro")
                return redirect(url_for("doacao_saida.registrar_saida"))

            if not cursor.fetchone():
                flash("Beneficiário não encontrado.", "erro")
                return redirect(url_for("doacao_saida.registrar_saida"))

            # Salva a doação
            cursor.execute("""
                INSERT INTO doacoes (tipo, destino_id, destino_tipo, data, observacoes, tipo_movimentacao)
                VALUES (?, ?, ?, ?, ?, 'saida')
            """, (tipo, beneficiario_id, beneficiario_tipo, data, observacoes))
            conn.commit()

        flash("Doação de saída registrada com sucesso!", "sucesso")
        return redirect(url_for("doacao_saida.registrar_saida"))

    return render_template("doacoes/saida.html", dados=None)
