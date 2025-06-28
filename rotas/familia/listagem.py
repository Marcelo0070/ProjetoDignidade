from flask import Blueprint, render_template, request
from banco.conexao import conectar
from rotas.utilidades.geral import calcular_idade
import math

familia_listagem = Blueprint("familia_listagem", __name__)

@familia_listagem.route("/familia/lista")
def lista_familias():
    filtros = {
        "busca": request.args.get("busca", "").strip().lower(),
        "ordem": request.args.get("ordem", "nome"),
        "direcao": request.args.get("direcao", "asc"),
        "colunas": request.args.get("colunas", "idade,documento,contato,endereco,observacoes").split(","),
        "modo": request.args.get("modo", "responsaveis"),
        "filtro_parentesco": request.args.get("filtro_parentesco", "").strip().lower(),
        "pagina": int(request.args.get("pagina", 1))
    }

    itens_por_pagina = 20

    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM familias")
        col_familia = [desc[0] for desc in cursor.description]
        familias_raw = [dict(zip(col_familia, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM membros_familia")
        col_membro = [desc[0] for desc in cursor.description]
        membros_raw = [dict(zip(col_membro, row)) for row in cursor.fetchall()]

    familias = []

    for f in familias_raw:
        f_id = f["id"]
        membros = [m for m in membros_raw if m["familia_id"] == f_id]

        responsavel_nome = f["responsavel"]
        endereco = f["rua_numero"] + ", " + f["bairro"] + ", " + f["cidade"] + " - " + f["estado"]
        idade_responsavel = calcular_idade(f["data_nascimento"])
        dados_comuns = {
            "documento": f["documento"],
            "contato": f["contato"],
            "endereco": endereco,
            "observacoes": f["observacoes"],
        }

        if filtros["modo"] == "responsaveis":
            if filtros["busca"] in responsavel_nome.lower() or filtros["busca"] in (f["documento"] or "").lower():
                familias.append({
                    "id": f_id,
                    "familia_id": f_id,
                    "nome": responsavel_nome,
                    "parentesco": "Responsável",
                    "responsavel": responsavel_nome,
                    "idade": idade_responsavel,
                    **dados_comuns,
                    "membros": [
                        {
                            "nome": m["nome"],
                            "parentesco": m["parentesco"],
                            "idade": calcular_idade(m["data_nascimento"] or "")
                        } for m in membros
                    ]
                })

        elif filtros["modo"] == "todos":
            nomes_vistos = set()
            todos = []

            incluir_responsavel = not filtros["filtro_parentesco"] or filtros["filtro_parentesco"] in ["", "todos", "responsável"]
            if incluir_responsavel:
                todos.append({
                    "id": f_id,
                    "familia_id": f_id,
                    "nome": responsavel_nome,
                    "parentesco": "Responsável",
                    "responsavel": responsavel_nome,
                    "idade": idade_responsavel,
                    **dados_comuns
                })
                nomes_vistos.add((responsavel_nome.lower(), "responsável"))

            for m in membros:
                nome = m["nome"]
                parentesco = (m["parentesco"] or "").strip()
                chave = (nome.lower(), parentesco.lower())

                if chave in nomes_vistos:
                    continue
                nomes_vistos.add(chave)

                if filtros["filtro_parentesco"] not in ["", "todos"] and filtros["filtro_parentesco"] != parentesco.lower():
                    continue

                todos.append({
                    "familia_id": f_id,
                    "membro_id": m["id"],
                    "nome": nome,
                    "parentesco": parentesco,
                    "responsavel": responsavel_nome,
                    "idade": calcular_idade(m["data_nascimento"] or ""),
                    **dados_comuns
                })

            for item in todos:
                if filtros["busca"] in item["nome"].lower():
                    familias.append(item)

    reverse = filtros["direcao"] == "desc"
    chave = filtros["ordem"]
    try:
        familias.sort(key=lambda x: (x.get(chave) if isinstance(x.get(chave), (int, float)) else (x.get(chave) or "").lower()), reverse=reverse)
    except TypeError:
        familias.sort(key=lambda x: str(x.get(chave) or "").lower(), reverse=reverse)

    total = len(familias)
    total_paginas = math.ceil(total / itens_por_pagina)
    inicio = (filtros["pagina"] - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    familias_pagina = familias[inicio:fim]

    return render_template("familia/listagem.html", familias=familias_pagina, filtros={**filtros, "total_paginas": total_paginas})

