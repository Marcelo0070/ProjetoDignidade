from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
import json

presenca_cadastro = Blueprint("presenca_cadastro", __name__)

@presenca_cadastro.route("/presenca/cadastro", methods=["GET", "POST"])
def cadastrar_presenca():
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            data = request.form.get("data", "").strip()
            presentes_json = request.form.get("presentes_json", "[]")

            if not data:
                flash("Informe a data da presença.", "erro")
                return redirect(url_for("presenca_cadastro.cadastrar_presenca"))

            try:
                presentes = json.loads(presentes_json)
            except Exception:
                flash("Erro ao processar os beneficiários.", "erro")
                return redirect(url_for("presenca_cadastro.cadastrar_presenca"))

            cursor.execute("DELETE FROM presenca WHERE data = ?", (data,))
            for p in presentes:
                cursor.execute("""
                    INSERT INTO presenca (data, beneficiario_id, beneficiario_tipo)
                    VALUES (?, ?, ?)
                """, (data, p["id"], p["tipo"]))

            conn.commit()
            flash("Presença registrada com sucesso!", "sucesso")
            return redirect(url_for("presenca_cadastro.cadastrar_presenca"))

    return render_template("presenca/cadastro.html")
