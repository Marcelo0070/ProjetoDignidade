
from flask import Blueprint, render_template, redirect, url_for, flash, request
from banco.conexao import conectar
from rotas.utilidades.geral import formatar_data

familia_perfil = Blueprint("familia_perfil", __name__)


@familia_perfil.route("/familia/perfil/<int:familia_id>")
def perfil(familia_id):
    with conectar() as conn:
        cursor = conn.cursor()

        # 🏠 Dados da família
        cursor.execute("SELECT * FROM familias WHERE id = ?", (familia_id,))
        dados = cursor.fetchone()
        if not dados:
            flash("Família não encontrada.", "erro")
            return redirect(url_for("familia_listagem.listar_familias"))

        colunas = [desc[0] for desc in cursor.description]
        familia = dict(zip(colunas, dados))

        # 👨‍👩‍👧 Membros da família
        cursor.execute("SELECT nome, parentesco FROM membros_familia WHERE familia_id = ?", (familia_id,))
        membros = cursor.fetchall()

        # 🧾 Visitas recebidas
        cursor.execute("""
            SELECT v.id, v.data_visita, v.endereco, vol.nome AS responsavel, v.observacoes
            FROM visitas v
            LEFT JOIN visita_voluntarios vv ON vv.visita_id = v.id
            LEFT JOIN voluntarios vol ON vv.voluntario_id = vol.id
            WHERE v.beneficiario_id = ? AND v.beneficiario_tipo = 'familia'
            ORDER BY v.data_visita DESC
        """, (familia_id,))
        visitas = [(v[0], formatar_data(v[1]), v[2], v[3], v[4]) for v in cursor.fetchall()]

        # 🎁 Doações recebidas
        cursor.execute("""
            SELECT id, tipo, origem, data, observacoes
            FROM doacoes
            WHERE destino_id = ? AND destino_tipo = 'familia'
            ORDER BY data DESC
        """, (familia_id,))
        doacoes = [{
            "id": d[0],
            "tipo": d[1],
            "origem": d[2],
            "data": formatar_data(d[3]),
            "observacoes": d[4],
            "url_editar": url_for("editar_saida.editar", doacao_id=d[0])
        } for d in cursor.fetchall()]

        # ✅ Presenças com suporte para data_original e formatada
        data_inicio = request.args.get("data_inicio", "")
        data_fim = request.args.get("data_fim", "")
        query = """
            SELECT data FROM presenca
            WHERE beneficiario_id = ? AND beneficiario_tipo = 'familia'
        """
        params = [familia_id]
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

        # 📘 Atividades participadas
        cursor.execute("""
            SELECT a.id, a.atividade, a.data, a.tema, a.responsavel, a.observacoes
            FROM atividades a
            JOIN atividade_participantes p ON a.id = p.atividade_id
            WHERE p.beneficiario_id = ? AND p.beneficiario_tipo = 'familia'
            ORDER BY a.data DESC
        """, (familia_id,))
        atividades = [(a[0], a[1], formatar_data(a[2]), a[3], a[4], a[5]) for a in cursor.fetchall()]

    return render_template(
        "familia/perfil.html",
        familia=familia,
        membros=membros,
        visitas=visitas,
        doacoes=doacoes,
        presencas=presencas,
        atividades=atividades
    )
