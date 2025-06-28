from flask import Blueprint, render_template, request
from banco.conexao import conectar
from rotas.utilidades.geral import calcular_idade, formatar_data

pessoa_listagem = Blueprint("pessoa_listagem", __name__)

@pessoa_listagem.route("/pessoa/lista", methods=["GET"])
def lista_pessoas():
    filtros = {
        "busca": request.args.get("busca", "").strip(),
        "ordem": request.args.get("ordem", "nome"),
        "direcao": request.args.get("direcao", "asc"),
        "colunas": request.args.get("colunas", ""),
        "pagina": int(request.args.get("pagina", 1))
    }

    por_pagina = 50
    offset = (filtros["pagina"] - 1) * por_pagina

    campos_disponiveis = [
        "apelido", "documento", "data_nascimento", "idade",
        "nome_mae", "dependencia", "contato", "endereco", "observacoes",
        "naturalidade", "tamanho_roupa", "aptidoes", "saude", "alfabetizacao",
        "termo_imagem", "primeiro_dia"
    ]

    colunas_selecionadas = [c for c in filtros["colunas"].split(",") if c in campos_disponiveis]

    query_base = '''
        SELECT id, nome, apelido, documento, data_nascimento, nome_mae,
               dependencia, contato, rua_numero, bairro, cidade, estado,
               observacoes, naturalidade, tamanho_roupa, aptidoes, saude,
               alfabetizacao, termo_imagem, primeiro_dia
        FROM pessoas
        WHERE 1=1
    '''
    parametros = []

    if filtros["busca"]:
        busca = filtros["busca"] + "%"
        query_base += " AND (nome LIKE ? OR apelido LIKE ? OR documento LIKE ?)"
        parametros.extend([busca, busca, busca])

    ordem_usuario = filtros["ordem"]
    if ordem_usuario == "idade":
        campo_sql = "data_nascimento"
        direcao = "DESC" if filtros["direcao"] == "asc" else "ASC"
    else:
        campo_sql = ordem_usuario if ordem_usuario in campos_disponiveis else "nome"
        direcao = filtros["direcao"].upper() if filtros["direcao"] in ["asc", "desc"] else "ASC"

    ordenacao_sql = f" ORDER BY {campo_sql} {direcao}"
    query_paginada = query_base + ordenacao_sql + " LIMIT ? OFFSET ?"

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM (" + query_base + ")", parametros)
        total = cursor.fetchone()[0]
        total_paginas = (total + por_pagina - 1) // por_pagina

        cursor.execute(query_paginada, (*parametros, por_pagina, offset))
        registros = cursor.fetchall()

    pessoas = []
    for r in registros:
        endereco = ", ".join([r[8], r[9], r[10], r[11]])
        pessoas.append({
            "id": r[0],
            "nome": r[1],
            "apelido": r[2],
            "documento": r[3],
            "data_nascimento": formatar_data(r[4]),
            "idade": calcular_idade(r[4]),
            "nome_mae": r[5],
            "dependencia": r[6],
            "contato": r[7],
            "endereco": endereco,
            "observacoes": r[12],
            "naturalidade": r[13],
            "tamanho_roupa": r[14],
            "aptidoes": r[15],
            "saude": r[16],
            "alfabetizacao": r[17],
            "termo_imagem": r[18],
            "primeiro_dia": formatar_data(r[19])
        })

    return render_template("pessoa/listagem.html", pessoas=pessoas, filtros={
        "busca": filtros["busca"],
        "ordem": filtros["ordem"],
        "direcao": filtros["direcao"],
        "colunas": colunas_selecionadas or ["apelido", "documento", "idade"],
        "pagina": filtros["pagina"],
        "total_paginas": total_paginas
    })

