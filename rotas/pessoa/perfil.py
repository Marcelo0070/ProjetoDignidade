from flask import Blueprint, render_template, redirect, url_for, flash, request
from banco.conexao import conectar
from rotas.utilidades.geral import calcular_idade, formatar_data

pessoa_perfil = Blueprint("pessoa_perfil", __name__)

@pessoa_perfil.route("/pessoa/perfil/<int:pessoa_id>")
def perfil(pessoa_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # 🧍 Buscar dados da pessoa
        cursor.execute("SELECT * FROM pessoas WHERE id = ?", (pessoa_id,))
        dados = cursor.fetchone()
        if not dados:
            flash("Pessoa não encontrada.", "erro")
            return redirect(url_for("pessoa_listagem.lista_pessoas"))

        # Transforma o resultado em dicionário para facilitar o acesso no template
        colunas = [desc[0] for desc in cursor.description]
        pessoa = dict(zip(colunas, dados))
        pessoa["data_nascimento"] = formatar_data(pessoa.get("data_nascimento", ""))
        pessoa["idade"] = calcular_idade(dados[colunas.index("data_nascimento")])

        # 🧾 Visitas com responsáveis (voluntários)
        cursor.execute("""
            SELECT v.id, v.data_visita, v.endereco, vol.nome AS responsavel, v.observacoes
            FROM visitas v
            LEFT JOIN visita_voluntarios vv ON vv.visita_id = v.id
            LEFT JOIN voluntarios vol ON vv.voluntario_id = vol.id
            WHERE v.beneficiario_id = ? AND v.beneficiario_tipo = 'pessoa'
            ORDER BY v.data_visita DESC
        """, (pessoa_id,))
        visitas = [(v[0], formatar_data(v[1]), v[2], v[3], v[4]) for v in cursor.fetchall()]

        # 🎁 Doações recebidas pela pessoa
        cursor.execute("""
            SELECT id, tipo, origem, data, observacoes
            FROM doacoes
            WHERE destino_id = ? AND destino_tipo = 'pessoa'
            ORDER BY data DESC
        """, (pessoa_id,))
        doacoes = [{
            "id": d[0],
            "tipo": d[1],
            "origem": d[2],
            "data": formatar_data(d[3]),
            "observacoes": d[4],
            "url_editar": url_for("editar_saida.editar", doacao_id=d[0])
        } for d in cursor.fetchall()]

        # ✅ Presenças (com filtro por data opcional)
        data_inicio = request.args.get("data_inicio", "")
        data_fim = request.args.get("data_fim", "")
        query = """
            SELECT data FROM presenca 
            WHERE beneficiario_id = ? AND beneficiario_tipo = 'pessoa'
        """
        params = [pessoa_id]

        # Adiciona filtros de data se fornecidos
        if data_inicio:
            query += " AND date(data) >= date(?)"
            params.append(data_inicio)
        if data_fim:
            query += " AND date(data) <= date(?)"
            params.append(data_fim)

        query += " ORDER BY data DESC"
        cursor.execute(query, tuple(params))
        presencas = [{
            "data_original": row[0],
            "data_formatada": formatar_data(row[0])
        } for row in cursor.fetchall()]


        # 📘 Atividades em que a pessoa participou
        cursor.execute("""
            SELECT a.id, a.atividade, a.data, a.tema, a.responsavel, a.observacoes
            FROM atividades a
            JOIN atividade_participantes p ON a.id = p.atividade_id
            WHERE p.beneficiario_id = ? AND p.beneficiario_tipo = 'pessoa'
            ORDER BY a.data DESC
        """, (pessoa_id,))
        atividades = [(a[0], a[1], formatar_data(a[2]), a[3], a[4], a[5]) for a in cursor.fetchall()]

    # Renderiza o template passando todos os dados coletados
    return render_template(
        "pessoa/perfil.html",
        pessoa=pessoa,
        visitas=visitas,
        doacoes=doacoes,
        presencas=presencas,
        atividades=atividades
    )

