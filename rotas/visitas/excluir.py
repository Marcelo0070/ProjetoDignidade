from flask import Blueprint, redirect, url_for, flash, request
from banco.conexao import conectar

visitas_excluir = Blueprint("visitas_excluir", __name__)

@visitas_excluir.route("/visitas/excluir/<int:id>", methods=["POST"])
def excluir_visita(id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Verifica se a visita existe
        cursor.execute("SELECT id FROM visitas WHERE id = ?", (id,))
        if not cursor.fetchone():
            flash("Visita não encontrada.", "erro")
            return redirect(request.referrer or url_for("visitas_listagem.listar_visitas"))

        # Executa exclusão
        cursor.execute("DELETE FROM visitas WHERE id = ?", (id,))
        conn.commit()

        flash("Visita excluída com sucesso.", "sucesso")
        return redirect(request.referrer or url_for("visitas_listagem.listar_visitas"))
