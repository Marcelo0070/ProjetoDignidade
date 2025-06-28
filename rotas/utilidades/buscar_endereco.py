from flask import Blueprint, request, jsonify
from banco.conexao import conectar

buscar_endereco = Blueprint("buscar_endereco", __name__)

@buscar_endereco.route("/util/buscar_endereco")
def buscar_endereco_func():
    id = request.args.get("id")
    tipo = request.args.get("tipo")

    if not id or not tipo:
        return jsonify({})

    with conectar() as conn:
        cursor = conn.cursor()
        if tipo == "pessoa":
            cursor.execute("""
                SELECT rua_numero, bairro, cidade, estado
                FROM pessoas
                WHERE id = ?
            """, (id,))
        elif tipo == "familia":
            cursor.execute("""
                SELECT rua_numero, bairro, cidade, estado
                FROM familias
                WHERE id = ?
            """, (id,))
        else:
            return jsonify({})

        resultado = cursor.fetchone()

    if resultado:
        return jsonify({
            "rua_numero": resultado[0] or "",
            "bairro": resultado[1] or "",
            "cidade": resultado[2] or "",
            "estado": resultado[3] or ""
        })
    else:
        return jsonify({})
