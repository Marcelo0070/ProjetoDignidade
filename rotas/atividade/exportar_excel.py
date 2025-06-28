from flask import Blueprint, request, make_response
from banco.conexao import conectar
from io import BytesIO
import pandas as pd
import json

atividade_exportar = Blueprint("atividade_exportar", __name__)

@atividade_exportar.route("/atividade/exportar", methods=["POST"])
def exportar_excel():
    try:
        ids = json.loads(request.form.get("ids", "[]"))
    except Exception:
        return "Erro ao processar IDs para exportação.", 400

    if not ids:
        return "Nenhuma atividade selecionada para exportar.", 400

    query_atividades = f"""
        SELECT id, atividade, data, tema, responsavel, observacoes
        FROM atividades
        WHERE id IN ({','.join(['?'] * len(ids))})
    """

    query_participantes = """
        SELECT ap.atividade_id, ap.beneficiario_id, ap.beneficiario_tipo,
               COALESCE(p.nome, f.responsavel) AS nome
        FROM atividade_participantes ap
        LEFT JOIN pessoas p ON ap.beneficiario_tipo = 'pessoa' AND ap.beneficiario_id = p.id
        LEFT JOIN familias f ON ap.beneficiario_tipo = 'familia' AND ap.beneficiario_id = f.id
        WHERE ap.atividade_id IN ({})
    """.format(",".join(['?'] * len(ids)))

    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute(query_atividades, ids)
        atividades = {r[0]: {
            "Atividade": r[1],
            "Data": "/".join(reversed(r[2].split("-"))) if r[2] else "—",
            "Tema": r[3] or "—",
            "Responsável": r[4],
            "Observações": r[5] or "—",
            "Participantes": []
        } for r in cursor.fetchall()}

        cursor.execute(query_participantes, ids)
        for aid, _, tipo, nome in cursor.fetchall():
            if aid in atividades:
                atividades[aid]["Participantes"].append(f"{nome} ({tipo})")

    # Preparar dataframe
    dados = []
    for atividade in atividades.values():
        linha = {
            "Atividade": atividade["Atividade"],
            "Data": atividade["Data"],
            "Tema": atividade["Tema"],
            "Responsável": atividade["Responsável"],
            "Participantes": ", ".join(atividade["Participantes"]),
            "Observações": atividade["Observações"]
        }
        dados.append(linha)

    df = pd.DataFrame(dados)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=atividades.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
