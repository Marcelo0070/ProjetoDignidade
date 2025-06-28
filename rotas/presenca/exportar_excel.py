from flask import Blueprint, request, make_response
from banco.conexao import conectar
from io import BytesIO
import pandas as pd
import json

presenca_exportar = Blueprint("presenca_exportar", __name__)

@presenca_exportar.route("/presencas/exportar", methods=["POST"])
def exportar_excel():
    try:
        datas = json.loads(request.form.get("datas", "[]"))
    except Exception:
        return "Erro ao processar as datas para exportação.", 400

    if not datas:
        return "Nenhuma data selecionada para exportar.", 400

    query = """
        SELECT p.data, p.beneficiario_id, p.beneficiario_tipo,
               COALESCE(pessoas.nome, familias.responsavel) AS nome
        FROM presenca p
        LEFT JOIN pessoas ON p.beneficiario_tipo = 'pessoa' AND p.beneficiario_id = pessoas.id
        LEFT JOIN familias ON p.beneficiario_tipo = 'familia' AND p.beneficiario_id = familias.id
        WHERE p.data IN ({})
        ORDER BY p.data, nome
    """.format(",".join(["?"] * len(datas)))

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, datas)
        registros = cursor.fetchall()

    dados = []
    for data, _, tipo, nome in registros:
        data_br = "/".join(reversed(data.split("-")))
        dados.append({
            "Data": data_br,
            "Nome": nome or "—",
            "Tipo": tipo
        })

    df = pd.DataFrame(dados)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=presencas.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
