from flask import Blueprint, jsonify
from banco.conexao import conectar

buscar_beneficiario = Blueprint("buscar_beneficiario", __name__)

@buscar_beneficiario.route("/util/buscar_beneficiarios")
def buscar():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, rua_numero, bairro, cidade, estado FROM pessoas")
        pessoas = [{
            "id": r[0],
            "nome": r[1],
            "rua_numero": r[2],
            "bairro": r[3],
            "cidade": r[4],
            "estado": r[5],
            "tipo": "pessoa"
        } for r in cursor.fetchall()]

        cursor.execute("SELECT id, responsavel, rua_numero, bairro, cidade, estado FROM familias")
        familias = [{
            "id": r[0],
            "nome": r[1],
            "rua_numero": r[2],
            "bairro": r[3],
            "cidade": r[4],
            "estado": r[5],
            "tipo": "familia"
        } for r in cursor.fetchall()]

    return jsonify(pessoas + familias)
