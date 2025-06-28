from flask import Blueprint, redirect, url_for, flash
from banco.conexao import conectar

presenca_excluir = Blueprint("presenca_excluir", __name__)

@presenca_excluir.route("/presenca/excluir/<data>", methods=["POST"])
def excluir_presenca(data):
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM presenca WHERE data = ?", (data,))
        total = cursor.fetchone()[0]

        if total == 0:
            flash("Nenhum registro de presença encontrado para esta data.", "erro")
            return redirect(url_for("comum.home"))

        cursor.execute("DELETE FROM presenca WHERE data = ?", (data,))
        conn.commit()

    flash(f"Presença do dia {data} excluída com sucesso!", "sucesso")
    return redirect(url_for("comum.home"))
