from flask import Blueprint, redirect, url_for, flash, request
from banco.conexao import conectar

voluntarios_excluir = Blueprint("voluntarios_excluir", __name__)

@voluntarios_excluir.route("/voluntarios/excluir/<int:voluntario_id>", methods=["POST"])
def excluir_voluntarios(voluntario_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Verificar se existe
        cursor.execute("SELECT id FROM voluntarios WHERE id = ?", (voluntario_id,))
        if not cursor.fetchone():
            flash("Voluntário não encontrado.", "erro")
            return redirect(url_for("voluntarios_listagem.lista_voluntarios"))

        # Excluir
        cursor.execute("DELETE FROM voluntarios WHERE id = ?", (voluntario_id,))
        conn.commit()

    flash("Voluntário excluído com sucesso!", "sucesso")
    return redirect(request.referrer or url_for("voluntarios_listagem.listar_voluntarios"))

