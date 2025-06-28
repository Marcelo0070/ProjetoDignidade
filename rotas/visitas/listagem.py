from flask import Blueprint, render_template, request
from banco.conexao import conectar
import math

visitas_listagem = Blueprint("visitas_listagem", __name__)

@visitas_listagem.route("/visitas/lista", methods=["GET"])
def listar_visitas():
    data = request.args.get("data", "").strip()
    beneficiario = request.args.get("beneficiario", "").strip().lower()
    voluntario = request.args.get("voluntario", "").strip().lower()
    ordem = request.args.get("ordem", "data_visita")
    direcao = request.args.get("direcao", "desc")
    pagina = int(request.args.get("pagina", 1))

    query = """
        SELECT v.id, v.data_visita, v.endereco, v.observacoes,
               v.beneficiario_tipo, v.beneficiario_id,
               CASE 
                   WHEN v.beneficiario_tipo = 'pessoa' THEN p.nome
                   WHEN v.beneficiario_tipo = 'familia' THEN f.responsavel
                   ELSE ''
               END AS beneficiario_nome,
               GROUP_CONCAT(vol.nome, ', ') AS voluntarios
        FROM visitas v
        LEFT JOIN pessoas p ON v.beneficiario_tipo = 'pessoa' AND v.beneficiario_id = p.id
        LEFT JOIN familias f ON v.beneficiario_tipo = 'familia' AND v.beneficiario_id = f.id
        LEFT JOIN visita_voluntarios vv ON v.id = vv.visita_id
        LEFT JOIN voluntarios vol ON vv.voluntario_id = vol.id
        WHERE 1=1
    """

    params = []
    if data:
        query += " AND v.data_visita = ?"
        params.append(data)
    if beneficiario:
        query += " AND LOWER(CASE WHEN v.beneficiario_tipo = 'pessoa' THEN p.nome ELSE f.responsavel END) LIKE ?"
        params.append(f"%{beneficiario}%")
    if voluntario:
        query += """
            AND v.id IN (
                SELECT visita_id FROM visita_voluntarios vv
                JOIN voluntarios vol ON vv.voluntario_id = vol.id
                WHERE LOWER(vol.nome) LIKE ?
            )
        """

        params.append(f"%{voluntario}%")

    query += f" GROUP BY v.id ORDER BY {ordem} {'ASC' if direcao == 'asc' else 'DESC'}"

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        registros = cursor.fetchall()
        colunas = [col[0] for col in cursor.description]

    todas_visitas = [dict(zip(colunas, linha)) for linha in registros]

    itens_por_pagina = 20
    total = len(todas_visitas)
    total_paginas = math.ceil(total / itens_por_pagina)
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    visitas_pagina = todas_visitas[inicio:fim]

    filtros = {
        "data": data,
        "beneficiario": beneficiario,
        "voluntario": voluntario,
        "ordem": ordem,
        "direcao": direcao,
        "pagina": pagina,
        "total_paginas": total_paginas
    }

    return render_template("visitas/listagem.html", visitas=visitas_pagina, filtros=filtros)
