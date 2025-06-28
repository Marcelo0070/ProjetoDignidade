from flask import Blueprint, jsonify
from banco.conexao import conectar

buscar_voluntario = Blueprint("buscar_voluntario", __name__)

@buscar_voluntario.route("/util/buscar_voluntarios")
def buscar():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM voluntarios")
        voluntarios = [{"id": r[0], "nome": r[1]} for r in cursor.fetchall()]
    return jsonify(voluntarios)
