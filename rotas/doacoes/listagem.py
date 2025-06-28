from flask import Blueprint, render_template, request
from banco.conexao import conectar
import math


doacao_listagem = Blueprint("doacao_listagem", __name__)

@doacao_listagem.route("/doacoes/lista", methods=["GET"])
def listar_doacoes():
    tipo = request.args.get("tipo", "").strip().lower()
    origem_destino = request.args.get("origem_destino", "").strip().lower()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_fim = request.args.get("data_fim", "").strip()
    ordem = request.args.get("ordem", "data")
    direcao = request.args.get("direcao", "desc")
    colunas = request.args.get("colunas", "tipo,origem_destino,data,observacoes").split(",")
    pagina = int(request.args.get("pagina", 1))
    itens_por_pagina = 30

    colunas_disponiveis = ["tipo", "origem_destino", "data", "observacoes"]
    colunas = [c for c in colunas if c in colunas_disponiveis]
    if not colunas:
        colunas = ["tipo", "origem_destino", "data", "observacoes"]

    ordem_sql = {
        "tipo": "tipo",
        "data": "data",
        "observacoes": "observacoes"
    }.get(ordem, "data")
    direcao_sql = "DESC" if direcao == "desc" else "ASC"

    query_base = """
        SELECT d.id, d.tipo, d.origem, d.destino_id, d.destino_tipo,
               d.data, d.observacoes, d.tipo_movimentacao,
               COALESCE(p.nome, f.responsavel) AS destino_nome
        FROM doacoes d
        LEFT JOIN pessoas p ON d.destino_tipo = 'pessoa' AND d.destino_id = p.id
        LEFT JOIN familias f ON d.destino_tipo = 'familia' AND d.destino_id = f.id
        WHERE 1=1
    """
    params = []

    if tipo:
        query_base += " AND LOWER(d.tipo) LIKE ?"
        params.append(f"%{tipo}%")

    if origem_destino:
        query_base += " AND (LOWER(d.origem) LIKE ? OR LOWER(destino_nome) LIKE ? OR CAST(d.destino_id AS TEXT) LIKE ?)"
        params += [f"%{origem_destino}%"] * 3

    if data_inicio:
        query_base += " AND date(d.data) >= date(?)"
        params.append(data_inicio)

    if data_fim:
        query_base += " AND date(d.data) <= date(?)"
        params.append(data_fim)

    query_base += f" ORDER BY d.{ordem_sql} {direcao_sql}"

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query_base, params)
        todas = cursor.fetchall()

    entradas, saidas = [], []
    for d in todas:
        if d[7] == "entrada":
            registro = {
                "id": d[0],
                "tipo": d[1],
                "origem_destino": d[2] or "—",
                "data": "/".join(reversed(d[5].split("-"))) if d[5] else "—",
                "observacoes": d[6] or "—"
            }
            entradas.append(registro)
        else:
            destino_nome = d[8] or "—"
            registro = {
                "id": d[0],
                "tipo": d[1],
                "origem_destino": destino_nome,
                "data": "/".join(reversed(d[5].split("-"))) if d[5] else "—",
                "observacoes": d[6] or "—"
            }
            saidas.append(registro)

    total_paginas = max(math.ceil(len(entradas + saidas) / itens_por_pagina), 1)
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina

    return render_template("doacoes/listagem.html", entradas=entradas[inicio:fim], saidas=saidas[inicio:fim], filtros={
        "tipo": tipo,
        "origem_destino": origem_destino,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "colunas": colunas,
        "ordem": ordem,
        "direcao": direcao,
        "pagina": pagina,
        "total_paginas": total_paginas
    })


