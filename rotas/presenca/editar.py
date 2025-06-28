from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
import json

presenca_editar = Blueprint("presenca_editar", __name__)

@presenca_editar.route("/presenca/editar/<data>", methods=["GET", "POST"])
def editar_presenca(data):
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            nova_data = request.form.get("data", "").strip()
            presentes_json = request.form.get("presentes_json", "").strip()

            if not nova_data or not presentes_json:
                flash("Preencha a data e selecione ao menos um presente.", "erro")
                return redirect(url_for("presenca_editar.editar_presenca", data=data))

            try:
                presentes = json.loads(presentes_json)
            except Exception:
                flash("Erro ao interpretar a lista de presença.", "erro")
                return redirect(url_for("presenca_editar.editar_presenca", data=data))

            # Apaga os antigos e insere os novos
            cursor.execute("DELETE FROM presenca WHERE data = ?", (data,))
            for p in presentes:
                cursor.execute("""
                    INSERT INTO presenca (data, beneficiario_id, beneficiario_tipo)
                    VALUES (?, ?, ?)
                """, (nova_data, p["id"], p["tipo"]))
            conn.commit()

            flash("Presença atualizada com sucesso!", "sucesso")
            return redirect(url_for("presenca_editar.editar_presenca", data=nova_data))

        # GET — carregar lista de presença da data informada
        cursor.execute("""
            SELECT p.beneficiario_id, p.beneficiario_tipo,
                   COALESCE(pe.nome, f.responsavel) AS nome
            FROM presenca p
            LEFT JOIN pessoas pe ON (p.beneficiario_tipo = 'pessoa' AND p.beneficiario_id = pe.id)
            LEFT JOIN familias f ON (p.beneficiario_tipo = 'familia' AND p.beneficiario_id = f.id)
            WHERE p.data = ?
        """, (data,))
        presentes = [{"id": r[0], "tipo": r[1], "nome": r[2]} for r in cursor.fetchall()]

        # Beneficiários para o autocomplete
        cursor.execute("SELECT id, nome, rua_numero, bairro, cidade, estado FROM pessoas")
        return render_template("presenca/editar.html",
                           data=data,
                           presentes=presentes)
