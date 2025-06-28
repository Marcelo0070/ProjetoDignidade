from flask import Blueprint, request, make_response
from banco.conexao import conectar
import pandas as pd
from io import BytesIO
import json

voluntarios_exportar = Blueprint("voluntarios_exportar", __name__)

@voluntarios_exportar.route("/voluntarios/exportar", methods=["POST"])
def exportar_excel():
    try:
        ids = json.loads(request.form.get("ids", "[]"))
        colunas = json.loads(request.form.get("colunas", "[]"))
    except Exception:
        return "Erro ao processar dados da exportação.", 400

    if not ids:
        return "Nenhum voluntário selecionado para exportar.", 400

    colunas_disponiveis = {
        "contato": "contato",
        "data_nascimento": "data_nascimento"
    }
    colunas = [c for c in colunas if c in colunas_disponiveis]
    if not colunas:
        colunas = ["contato", "data_nascimento"]

    query = f"""
        SELECT id, nome, contato, data_nascimento
        FROM voluntarios
        WHERE id IN ({','.join(['?'] * len(ids))})
    """

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, ids)
        registros = cursor.fetchall()

    dados = []
    for r in registros:
        row = {
            "Nome": r[1],
        }
        if "contato" in colunas:
            row["Contato"] = r[2]
        if "data_nascimento" in colunas:
            row["Data de Nascimento"] = "/".join(reversed(r[3].split("-"))) if r[3] else "—"
        dados.append(row)

    df = pd.DataFrame(dados)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=voluntarios.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
