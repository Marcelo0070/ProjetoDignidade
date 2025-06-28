from flask import Blueprint, render_template, request
from banco.conexao import conectar
import math

voluntarios_listagem = Blueprint("voluntarios_listagem", __name__)

@voluntarios_listagem.route("/voluntarios/lista", methods=["GET"])
def listar_voluntarios():
    busca = request.args.get("busca", "").strip()
    data_inicio = request.args.get("data_inicio", "").strip()
    data_fim = request.args.get("data_fim", "").strip()
    ordem = request.args.get("ordem", "nome").strip()
    direcao = request.args.get("direcao", "asc").strip().lower()
    colunas = request.args.get("colunas", "contato,data_nascimento").split(",")
    pagina = int(request.args.get("pagina", 1))

    colunas_disponiveis = ["contato", "data_nascimento"]
    colunas = [c for c in colunas if c in colunas_disponiveis]
    if not colunas:
        colunas = ["contato", "data_nascimento"]

    colunas_ordenaveis = {
        "nome": "nome",
        "data_nascimento": "data_nascimento"
    }
    campo_ordenar = colunas_ordenaveis.get(ordem, "nome")
    direcao_sql = "ASC" if direcao == "asc" else "DESC"

    query = f"""
        SELECT id, nome, contato, data_nascimento
        FROM voluntarios
        WHERE 1=1
    """
    params = []

    if busca:
        query += " AND nome LIKE ?"
        params.append(f"%{busca}%")

    if data_inicio:
        query += " AND date(data_nascimento) >= date(?)"
        params.append(data_inicio)

    if data_fim:
        query += " AND date(data_nascimento) <= date(?)"
        params.append(data_fim)

    query += f" ORDER BY {campo_ordenar} {direcao_sql}"

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        registros = cursor.fetchall()

    voluntarios = []
    for r in registros:
        voluntarios.append({
            "id": r[0],
            "nome": r[1],
            "contato": r[2],
            "data_nascimento": "/".join(reversed(r[3].split("-"))) if r[3] else "—"
        })

    itens_por_pagina = 30
    total = len(voluntarios)
    total_paginas = math.ceil(total / itens_por_pagina)
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    voluntarios_pagina = voluntarios[inicio:fim]

    return render_template("voluntarios/listagem.html", voluntarios=voluntarios_pagina, filtros={
        "busca": busca,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "colunas": colunas,
        "ordem": ordem,
        "direcao": direcao,
        "pagina": pagina,
        "total_paginas": total_paginas
    })