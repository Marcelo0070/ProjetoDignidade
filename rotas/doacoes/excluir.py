from flask import Blueprint, redirect, url_for, flash, request
from banco.conexao import conectar

doacao_excluir = Blueprint("doacao_excluir", __name__)

@doacao_excluir.route("/doacoes/excluir/<int:doacao_id>", methods=["POST"])
def excluir_doacao(doacao_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doacoes WHERE id = ?", (doacao_id,))
        conn.commit()

    flash("Doação excluída com sucesso.", "sucesso")
    return redirect(url_for("doacao_listagem.listar_doacoes"))
