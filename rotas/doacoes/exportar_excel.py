from flask import Blueprint, request, make_response
from banco.conexao import conectar
from io import BytesIO
import pandas as pd
import json

doacao_exportar = Blueprint("doacao_exportar", __name__)

@doacao_exportar.route("/doacoes/exportar", methods=["POST"])
def exportar_excel():
    try:
        ids = json.loads(request.form.get("ids", "[]"))
        colunas = json.loads(request.form.get("colunas", "[]"))
    except Exception as e:
        return f"Erro ao processar dados da exportação: {e}", 400

    if not ids:
        return "Nenhuma doação selecionada para exportar.", 400

    colunas_disponiveis = {
        "tipo": "Tipo",
        "origem_destino": "Origem/Destino",
        "data": "Data",
        "observacoes": "Observações"
    }

    colunas = [c for c in colunas if c in colunas_disponiveis]
    if not colunas:
        colunas = list(colunas_disponiveis.keys())

    query = f"""
        SELECT id, tipo, origem, destino_id, destino_tipo, data, observacoes, tipo_movimentacao
        FROM doacoes
        WHERE id IN ({','.join(['?'] * len(ids))})
    """

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, ids)
        registros = cursor.fetchall()

        # Buscar nomes de beneficiários (somente se tiver saída)
        cursor.execute("SELECT id, nome FROM pessoas")
        pessoas = {r[0]: r[1] for r in cursor.fetchall()}

        cursor.execute("SELECT id, responsavel FROM familias")
        familias = {r[0]: r[1] for r in cursor.fetchall()}

    dados = []
    for r in registros:
        tipo, origem, destino_id, destino_tipo, data, obs, mov = r[1:8]

        if mov == "entrada":
            origem_destino = origem or "—"
        else:
            if destino_tipo == "pessoa":
                origem_destino = pessoas.get(destino_id, "Pessoa não encontrada")
            elif destino_tipo == "familia":
                origem_destino = familias.get(destino_id, "Família não encontrada")
            else:
                origem_destino = "—"

        linha = {
            "Tipo": tipo,
            "Origem/Destino": origem_destino,
            "Data": "/".join(reversed(data.split("-"))) if data else "—",
            "Observações": obs or "—"
        }

        # Reduz a linha às colunas solicitadas
        dados.append({colunas_disponiveis[c]: linha[colunas_disponiveis[c]] for c in colunas})

    df = pd.DataFrame(dados)

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    response = make_response(output.read())
    response.headers["Content-Disposition"] = "attachment; filename=doacoes.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
