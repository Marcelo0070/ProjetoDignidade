from flask import Blueprint, redirect, url_for, flash
from banco.conexao import conectar

atividade_excluir = Blueprint("atividade_excluir", __name__)

@atividade_excluir.route("/atividade/excluir/<int:atividade_id>", methods=["POST"])
def excluir_atividade(atividade_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Verificar se a atividade existe
        cursor.execute("SELECT id FROM atividades WHERE id = ?", (atividade_id,))
        if not cursor.fetchone():
            flash("Atividade não encontrada.", "erro")
            return redirect(url_for("atividade_listagem.lista_atividades"))

        # Excluir participantes primeiro
        cursor.execute("DELETE FROM atividade_participantes WHERE atividade_id = ?", (atividade_id,))

        # Excluir atividade
        cursor.execute("DELETE FROM atividades WHERE id = ?", (atividade_id,))
        conn.commit()

        flash("Atividade excluída com sucesso.", "sucesso")
        return redirect(url_for("atividade_listagem.listar_atividades"))
