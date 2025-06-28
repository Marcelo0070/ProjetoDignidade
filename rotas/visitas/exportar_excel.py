from flask import Blueprint, request, make_response
from banco.conexao import conectar
import pandas as pd
from io import BytesIO
import json

visitas_exportar = Blueprint("visitas_exportar", __name__)

@visitas_exportar.route("/visitas/exportar", methods=["POST"])
def exportar_excel():
    try:
        ids = json.loads(request.form.get("ids", "[]"))
        colunas = request.form.get("colunas", "").split(",")
    except Exception:
        return "Erro ao processar dados da exportação.", 400

    if not ids:
        return "Nenhuma visita selecionada para exportar.", 400

    colunas_disponiveis = {
        "beneficiario": "beneficiario_nome",
        "voluntario": "voluntario_nome",
        "endereco": "endereco",
        "observacoes": "observacoes",
        "data_visita": "data_visita"
    }

    colunas = [c for c in colunas if c in colunas_disponiveis]
    if not colunas:
        colunas = ["beneficiario", "voluntario", "data_visita"]

    query = f"""
        SELECT visitas.id, visitas.data_visita, visitas.endereco, visitas.observacoes,
               visitas.beneficiario_tipo, visitas.beneficiario_id,
               v.nome AS voluntario_nome,
               CASE
                   WHEN visitas.beneficiario_tipo = 'pessoa' THEN p.nome
                   WHEN visitas.beneficiario_tipo = 'familia' THEN f.responsavel
                   ELSE ''
               END AS beneficiario_nome
        FROM visitas
        LEFT JOIN voluntarios v ON v.id = visitas.voluntario_id
        LEFT JOIN pessoas p ON visitas.beneficiario_tipo = 'pessoa' AND visitas.beneficiario_id = p.id
        LEFT JOIN familias f ON visitas.beneficiario_tipo = 'familia' AND visitas.beneficiario_id = f.id
        WHERE visitas.id IN ({','.join(['?'] * len(ids))})
    """

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, ids)
        registros = cursor.fetchall()

    # Montar os dados com base nas colunas requisitadas
    dados = []
    for r in registros:
        linha = {}
        campos = {
            "beneficiario": r[7],
            "voluntario": r[6],
            "endereco": r[2],
            "observacoes": r[3],
            "data_visita": "/".join(reversed(r[1].split("-"))) if r[1] else ""
        }
        for c in colunas:
            linha[c.title().replace("_", " ")] = campos.get(c)
        dados.append(linha)

    df = pd.DataFrame(dados)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=visitas_exportadas.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response
