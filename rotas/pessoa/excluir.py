from flask import Blueprint, redirect, url_for, flash, request
from banco.conexao import conectar
import os

pessoa_excluir = Blueprint("pessoa_excluir", __name__)
CAMINHO_FOTOS = "static/fotos"

@pessoa_excluir.route("/pessoa/excluir/<int:pessoa_id>", methods=["POST"])
def excluir_pessoa(pessoa_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Buscar a foto antes de excluir
        cursor.execute("SELECT foto FROM pessoas WHERE id = ?", (pessoa_id,))
        resultado = cursor.fetchone()

        if not resultado:
            flash("Pessoa não encontrada.", "erro")
            return redirect(url_for("pessoa_listagem.lista_pessoas"))

        caminho_foto = resultado[0]

        # Excluir do banco
        cursor.execute("DELETE FROM pessoas WHERE id = ?", (pessoa_id,))
        conn.commit()

    # Excluir a imagem (se houver)
    if caminho_foto:
        try:
            caminho_completo = os.path.join(CAMINHO_FOTOS, os.path.basename(caminho_foto))
            if os.path.exists(caminho_completo):
                os.remove(caminho_completo)
        except Exception as e:
            flash(f"Erro ao excluir imagem: {e}", "erro")

    flash("Pessoa excluída com sucesso!", "sucesso")
    return redirect(url_for("pessoa_listagem.lista_pessoas"))
