from flask import Blueprint, render_template, request
from banco.conexao import conectar
import math

presenca_listagem = Blueprint("presenca_listagem", __name__)

@presenca_listagem.route("/presencas/lista", methods=["GET"])
def listar_presencas():
    data_filtro = request.args.get("data", "").strip()
    ordem = request.args.get("ordem", "data")
    direcao = request.args.get("direcao", "desc")
    colunas = request.args.get("colunas", "").split(",")
    pagina = int(request.args.get("pagina", 1))

    query = """
        SELECT p.data, p.beneficiario_id, p.beneficiario_tipo,
               COALESCE(pessoas.nome, familias.responsavel) AS nome
        FROM presenca p
        LEFT JOIN pessoas ON p.beneficiario_tipo = 'pessoa' AND p.beneficiario_id = pessoas.id
        LEFT JOIN familias ON p.beneficiario_tipo = 'familia' AND p.beneficiario_id = familias.id
        WHERE 1=1
    """
    params = []

    if data_filtro:
        query += " AND p.data = ?"
        params.append(data_filtro)

    query += " ORDER BY p.data DESC, nome ASC"  # Ordena apenas por data para não gerar erro

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        registros = cursor.fetchall()

    dias = {}
    for data, benef_id, benef_tipo, nome in registros:
        if data not in dias:
            dias[data] = []
        dias[data].append({
            "id": benef_id,
            "tipo": benef_tipo,
            "nome": nome or "Desconhecido"
        })

    dias_ordenados = []
    for data, beneficiarios in dias.items():
        data_formatada = "/".join(reversed(data.split("-")))
        dias_ordenados.append({
            "data": data,
            "data_formatada": data_formatada,
            "beneficiarios": beneficiarios,
            "quantidade": len(beneficiarios)
        })

    if ordem == "quantidade":
        dias_ordenados.sort(key=lambda x: x["quantidade"], reverse=(direcao != "asc"))
    elif ordem == "data":
        dias_ordenados.sort(key=lambda x: x["data"], reverse=(direcao != "asc"))

    itens_por_pagina = 20
    total = len(dias_ordenados)
    total_paginas = math.ceil(total / itens_por_pagina)
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    presencas_pagina = dias_ordenados[inicio:fim]

    filtros = {
        "data": data_filtro,
        "ordem": ordem,
        "direcao": direcao,
        "colunas": colunas,
        "pagina": pagina,
        "total_paginas": total_paginas
    }

    return render_template("presenca/listagem.html", presencas=presencas_pagina, filtros=filtros)
