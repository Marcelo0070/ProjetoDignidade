from flask import Blueprint, render_template, request
from banco.conexao import conectar
import math

atividade_listagem = Blueprint("atividade_listagem", __name__)

@atividade_listagem.route("/atividade/lista", methods=["GET"])
def listar_atividades():
    data_filtro = request.args.get("data", "").strip()
    busca = request.args.get("busca", "").strip().lower()
    ordem = request.args.get("ordem", "atividade")
    direcao = request.args.get("direcao", "asc")
    pagina = int(request.args.get("pagina", 1))
    itens_por_pagina = 30

    query = """
        SELECT id, atividade, data, tema, responsavel, observacoes
        FROM atividades
        WHERE 1=1
    """
    params = []

    if data_filtro:
        query += " AND data = ?"
        params.append(data_filtro)

    if busca:
        query += " AND (LOWER(atividade) LIKE ? OR LOWER(responsavel) LIKE ?)"
        params += [f"%{busca}%"] * 2

    if ordem not in ["atividade", "data"]:
        ordem = "atividade"
    query += f" ORDER BY {ordem} {'DESC' if direcao == 'desc' else 'ASC'}"

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        atividades_raw = cursor.fetchall()

        cursor.execute("""
            SELECT ap.atividade_id, ap.beneficiario_id, ap.beneficiario_tipo,
                   COALESCE(p.nome, f.responsavel)
            FROM atividade_participantes ap
            LEFT JOIN pessoas p ON ap.beneficiario_tipo = 'pessoa' AND ap.beneficiario_id = p.id
            LEFT JOIN familias f ON ap.beneficiario_tipo = 'familia' AND ap.beneficiario_id = f.id
        """)
        participantes_raw = cursor.fetchall()

    participantes_por_atividade = {}
    for atividade_id, _, tipo, nome in participantes_raw:
        if atividade_id not in participantes_por_atividade:
            participantes_por_atividade[atividade_id] = []
        participantes_por_atividade[atividade_id].append({
            "nome": nome or "Desconhecido",
            "tipo": tipo
        })

    atividades = []
    for r in atividades_raw:
        data_formatada = "/".join(reversed(r[2].split("-"))) if r[2] else "—"
        atividades.append({
            "id": r[0],
            "atividade": r[1],
            "data": r[2],
            "data_formatada": data_formatada,
            "tema": r[3],
            "responsavel": r[4],
            "observacoes": r[5],
            "participantes": participantes_por_atividade.get(r[0], [])
        })

    total = len(atividades)
    total_paginas = math.ceil(total / itens_por_pagina)
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    atividades_pagina = atividades[inicio:fim]

    return render_template("atividade/listagem.html", atividades=atividades_pagina, filtros={
        "data": data_filtro,
        "busca": busca,
        "ordem": ordem,
        "direcao": direcao,
        "pagina": pagina,
        "total_paginas": total_paginas
    })
