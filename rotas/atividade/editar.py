from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
import json

atividade_editar = Blueprint("atividade_editar", __name__)

@atividade_editar.route("/atividade/editar/<int:atividade_id>", methods=["GET", "POST"])
def editar_atividade(atividade_id):
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            atividade = request.form.get("atividade", "").strip()
            data = request.form.get("data", "").strip()
            tema = request.form.get("tema", "").strip()
            responsavel = request.form.get("responsavel", "").strip()
            participantes_json = request.form.get("participantes_json", "[]")
            observacoes = request.form.get("observacoes", "").strip()

            if not atividade or not data or not responsavel:
                flash("Preencha os campos obrigatórios.", "erro")
                return redirect(url_for("atividade_editar.editar_atividade", atividade_id=atividade_id))

            try:
                participantes = json.loads(participantes_json)
            except Exception:
                flash("Erro ao processar os participantes.", "erro")
                return redirect(url_for("atividade_editar.editar_atividade", atividade_id=atividade_id))

            # Atualizar atividade
            cursor.execute("""
                UPDATE atividades
                SET atividade = ?, data = ?, tema = ?, responsavel = ?, observacoes = ?
                WHERE id = ?
            """, (atividade, data, tema, responsavel, observacoes, atividade_id))

            # Atualizar participantes
            cursor.execute("DELETE FROM atividade_participantes WHERE atividade_id = ?", (atividade_id,))
            for p in participantes:
                cursor.execute("""
                    INSERT INTO atividade_participantes (atividade_id, beneficiario_id, beneficiario_tipo)
                    VALUES (?, ?, ?)
                """, (atividade_id, p["id"], p["tipo"]))

            conn.commit()
            flash("Atividade atualizada com sucesso!", "sucesso")
            return redirect(url_for("atividade_listagem.listar_atividades", atividade_id=atividade_id))

        # GET
        # Buscar atividade
        cursor.execute("SELECT * FROM atividades WHERE id = ?", (atividade_id,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("Atividade não encontrada.", "erro")
            return redirect(url_for("atividade_listagem.listar_atividades"))

        colunas = [col[0] for col in cursor.description]
        dados = dict(zip(colunas, resultado))

        # Participantes
        cursor.execute("""
            SELECT a.beneficiario_id, a.beneficiario_tipo,
                   COALESCE(p.nome, f.responsavel) AS nome
            FROM atividade_participantes a
            LEFT JOIN pessoas p ON a.beneficiario_tipo = 'pessoa' AND a.beneficiario_id = p.id
            LEFT JOIN familias f ON a.beneficiario_tipo = 'familia' AND a.beneficiario_id = f.id
            WHERE a.atividade_id = ?
        """, (atividade_id,))
        participantes = [{"id": r[0], "tipo": r[1], "nome": r[2]} for r in cursor.fetchall()]

        # Dados para autocomplete
        cursor.execute("SELECT id, nome FROM pessoas")
        return render_template("atividade/editar.html",
                           dados=dados,
                           participantes=participantes)