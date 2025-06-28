from flask import Blueprint, redirect, url_for, flash
from banco.conexao import conectar

familia_excluir = Blueprint("familia_excluir", __name__)

@familia_excluir.route("/familia/excluir/<int:familia_id>", methods=["POST"])
def excluir_familia(familia_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Verificar se a família existe
        cursor.execute("SELECT id FROM familias WHERE id = ?", (familia_id,))
        if not cursor.fetchone():
            flash("Família não encontrada.", "erro")
            return redirect(url_for("familia_listagem.lista_familias"))

        # Excluir membros da família
        cursor.execute("DELETE FROM membros_familia WHERE familia_id = ?", (familia_id,))

        # Excluir a família
        cursor.execute("DELETE FROM familias WHERE id = ?", (familia_id,))
        conn.commit()

    flash("Família excluída com sucesso!", "sucesso")
    return redirect(url_for("familia_listagem.lista_familias"))


