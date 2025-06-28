from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from banco.conexao import conectar
from rotas.utilidades.geral import capitalizar
import json

atividade_cadastro = Blueprint("atividade_cadastro", __name__)

@atividade_cadastro.route("/atividade/cadastro", methods=["GET", "POST"])
def cadastrar_atividade():
    if request.method == "POST":
        data = request.form.get("data", "").strip()
        nome_atividade = request.form.get("atividade", "").strip()
        tema = request.form.get("tema", "").strip()
        responsavel = capitalizar(request.form.get("responsavel", "").strip())
        observacoes = request.form.get("observacoes", "").strip()
        participantes_json = request.form.get("participantes_json", "[]")

        if not data or not nome_atividade or not responsavel:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("atividade/cadastro.html", dados=request.form)

        try:
            participantes = json.loads(participantes_json)
        except Exception:
            flash("Erro ao processar os participantes.", "erro")
            return render_template("atividade/cadastro.html", dados=request.form)

        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO atividades (
                    data, atividade, tema, responsavel, observacoes
                ) VALUES (?, ?, ?, ?, ?)
            """, (data, nome_atividade, tema, responsavel, observacoes))
            atividade_id = cursor.lastrowid

            for p in participantes:
                cursor.execute("""
                    INSERT INTO atividade_participantes (
                        atividade_id, beneficiario_id, beneficiario_tipo
                    ) VALUES (?, ?, ?)
                """, (atividade_id, p["id"], p["tipo"]))

            conn.commit()

        flash("Atividade registrada com sucesso!", "sucesso")
        return redirect(url_for("atividade_cadastro.cadastrar_atividade"))

    return render_template("atividade/cadastro.html", dados=None)


@atividade_cadastro.route("/atividades/carregar_presencas")
def carregar_presencas():
    data = request.args.get("data")
    if not data:
        return jsonify([])

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT beneficiario_id, beneficiario_tipo
            FROM presenca
            WHERE data = ?
        """, (data,))
        registros = cursor.fetchall()

        participantes = []
        for id_, tipo in registros:
            if tipo == "pessoa":
                cursor.execute("SELECT nome FROM pessoas WHERE id = ?", (id_,))
            elif tipo == "familia":
                cursor.execute("SELECT responsavel FROM familias WHERE id = ?", (id_,))
            else:
                continue

            nome_row = cursor.fetchone()
            nome = nome_row[0] if nome_row else "Desconhecido"
            participantes.append({"id": id_, "tipo": tipo, "nome": nome})

    return jsonify(participantes)

