from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

visitas_cadastro = Blueprint("visitas_cadastro", __name__)

@visitas_cadastro.route("/visitas/cadastro", methods=["GET", "POST"])
def cadastrar_visita():
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            beneficiario_id = request.form.get("beneficiario_id")
            beneficiario_tipo = request.form.get("beneficiario_tipo")
            data_visita = request.form.get("data_visita", "").strip()
            observacoes = request.form.get("observacoes", "").strip()

            rua_numero = request.form.get("rua_numero", "").strip()
            bairro = request.form.get("bairro", "").strip()
            cidade = request.form.get("cidade", "").strip()
            estado = request.form.get("estado", "").strip()

            # Extrai voluntários do formulário
            voluntarios = []
            for key in request.form:
                if key.startswith("voluntarios[") and key.endswith("][id]"):
                    idx = key.split("[")[1].split("]")[0]
                    voluntario_id = request.form.get(f"voluntarios[{idx}][id]", "").strip()
                    if voluntario_id:
                        voluntarios.append(voluntario_id)

            # Validação
            if not all([beneficiario_id, beneficiario_tipo, data_visita, rua_numero, bairro, cidade, estado]) or not voluntarios:
                flash("Todos os campos obrigatórios devem ser preenchidos.", "erro")
                return redirect(url_for("visitas_cadastro.cadastrar_visita"))

            # Verifica se beneficiário existe
            if beneficiario_tipo == "pessoa":
                cursor.execute("SELECT id FROM pessoas WHERE id = ?", (beneficiario_id,))
            elif beneficiario_tipo == "familia":
                cursor.execute("SELECT id FROM familias WHERE id = ?", (beneficiario_id,))
            else:
                flash("Tipo de beneficiário inválido.", "erro")
                return redirect(url_for("visitas_cadastro.cadastrar_visita"))

            if not cursor.fetchone():
                flash("Beneficiário não encontrado.", "erro")
                return redirect(url_for("visitas_cadastro.cadastrar_visita"))

            # Verifica se todos os voluntários existem
            for v_id in voluntarios:
                cursor.execute("SELECT id FROM voluntarios WHERE id = ?", (v_id,))
                if not cursor.fetchone():
                    flash(f"Voluntário com ID {v_id} não encontrado.", "erro")
                    return redirect(url_for("visitas_cadastro.cadastrar_visita"))

            # Monta endereço
            endereco = f"{rua_numero}, {bairro}, {cidade} - {estado}"

            # Insere visita
            cursor.execute("""
                INSERT INTO visitas (
                    beneficiario_id, beneficiario_tipo,
                    data_visita, endereco, observacoes
                ) VALUES (?, ?, ?, ?, ?)
            """, (beneficiario_id, beneficiario_tipo, data_visita, endereco, observacoes))
            visita_id = cursor.lastrowid

            # Insere voluntários associados
            for v_id in voluntarios:
                cursor.execute("""
                    INSERT INTO visita_voluntarios (visita_id, voluntario_id)
                    VALUES (?, ?)
                """, (visita_id, v_id))

            conn.commit()
            flash("Visita registrada com sucesso!", "sucesso")
            return redirect(url_for("visitas_cadastro.cadastrar_visita"))

    return render_template("visitas/cadastro.html")

