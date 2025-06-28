from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

visitas_editar = Blueprint("visitas_editar", __name__)

@visitas_editar.route("/visitas/editar/<int:id>", methods=["GET", "POST"])
def editar_visita(id):
    with conectar() as conn:
        cursor = conn.cursor()

        # Buscar dados da visita
        cursor.execute("""
            SELECT beneficiario_id, beneficiario_tipo, data_visita, endereco, observacoes
            FROM visitas WHERE id = ?
        """, (id,))
        dados = cursor.fetchone()

        if not dados:
            flash("Visita não encontrada.", "erro")
            return redirect(url_for("visitas_listagem.listar_visitas"))

        beneficiario_id, beneficiario_tipo, data_visita, endereco, observacoes = dados

        # Se POST, atualiza os dados
        if request.method == "POST":
            novo_beneficiario_id = request.form.get("beneficiario_id")
            novo_beneficiario_tipo = request.form.get("beneficiario_tipo")
            nova_data = request.form.get("data_visita", "").strip()
            nova_observacoes = request.form.get("observacoes", "").strip()
            rua = request.form.get("rua_numero", "").strip()
            bairro = request.form.get("bairro", "").strip()
            cidade = request.form.get("cidade", "").strip()
            estado = request.form.get("estado", "").strip()

            voluntarios = []
            for key in request.form:
                if key.startswith("voluntarios[") and key.endswith("][id]"):
                    idx = key.split("[")[1].split("]")[0]
                    v_id = request.form.get(f"voluntarios[{idx}][id]", "").strip()
                    if v_id:
                        voluntarios.append(v_id)

            # Validação
            if not all([novo_beneficiario_id, novo_beneficiario_tipo, nova_data, rua, bairro, cidade, estado]) or not voluntarios:
                flash("Todos os campos obrigatórios devem ser preenchidos.", "erro")
                return redirect(url_for("visitas_editar.editar_visita", id=id))

            # Verificar beneficiário
            if novo_beneficiario_tipo == "pessoa":
                cursor.execute("SELECT id FROM pessoas WHERE id = ?", (novo_beneficiario_id,))
            elif novo_beneficiario_tipo == "familia":
                cursor.execute("SELECT id FROM familias WHERE id = ?", (novo_beneficiario_id,))
            else:
                flash("Tipo de beneficiário inválido.", "erro")
                return redirect(url_for("visitas_editar.editar_visita", id=id))

            if not cursor.fetchone():
                flash("Beneficiário não encontrado.", "erro")
                return redirect(url_for("visitas_editar.editar_visita", id=id))

            # Verificar voluntários
            for v_id in voluntarios:
                cursor.execute("SELECT id FROM voluntarios WHERE id = ?", (v_id,))
                if not cursor.fetchone():
                    flash(f"Voluntário com ID {v_id} não encontrado.", "erro")
                    return redirect(url_for("visitas_editar.editar_visita", id=id))

            # Atualiza visita
            endereco_final = f"{rua}, {bairro}, {cidade} - {estado}"
            cursor.execute("""
                UPDATE visitas
                SET beneficiario_id = ?, beneficiario_tipo = ?, data_visita = ?, endereco = ?, observacoes = ?
                WHERE id = ?
            """, (novo_beneficiario_id, novo_beneficiario_tipo, nova_data, endereco_final, nova_observacoes, id))

            # Atualiza voluntários
            cursor.execute("DELETE FROM visita_voluntarios WHERE visita_id = ?", (id,))
            for v_id in voluntarios:
                cursor.execute("INSERT INTO visita_voluntarios (visita_id, voluntario_id) VALUES (?, ?)", (id, v_id))

            conn.commit()
            flash("Visita atualizada com sucesso!", "sucesso")
            return redirect(url_for("visitas_listagem.listar_visitas", id=id))

        # Pré-carregar formulário no GET
        rua_numero, bairro, cidade, estado = "", "", "", ""
        try:
            rua_bairro, cidade_estado = endereco.split(", ", 1)
            rua_numero = rua_bairro
            bairro, cidade_estado = cidade_estado.split(", ", 1)
            cidade, estado = cidade_estado.split(" - ")
        except Exception:
            pass  # Se a string de endereço não estiver no formato esperado

        # Nome do beneficiário
        if beneficiario_tipo == "pessoa":
            cursor.execute("SELECT nome FROM pessoas WHERE id = ?", (beneficiario_id,))
        else:
            cursor.execute("SELECT responsavel FROM famílias WHERE id = ?", (beneficiario_id,))
        beneficiario_nome = cursor.fetchone()
        beneficiario_nome = beneficiario_nome[0] if beneficiario_nome else ""

        # Voluntários da visita
        cursor.execute("""
            SELECT v.id, v.nome
            FROM visita_voluntarios vv
            JOIN voluntarios v ON vv.voluntario_id = v.id
            WHERE vv.visita_id = ?
        """, (id,))
        voluntarios_data = [{"id": v[0], "nome": v[1]} for v in cursor.fetchall()]

        visita = {
            "beneficiario_id": beneficiario_id,
            "beneficiario_tipo": beneficiario_tipo,
            "beneficiario_nome": beneficiario_nome,
            "data_visita": data_visita,
            "observacoes": observacoes,
            "rua_numero": rua_numero,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "voluntarios_json": voluntarios_data
        }

        return render_template("visitas/editar.html", visita=visita)



