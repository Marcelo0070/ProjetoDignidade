from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
from rotas.utilidades.geral import capitalizar

familia_cadastro = Blueprint("familia_cadastro", __name__)

@familia_cadastro.route("/familia/cadastro", methods=["GET", "POST"])
def cadastrar_familia():
    if request.method == "POST":
        responsavel = capitalizar(request.form.get("responsavel", "").strip())
        documento = request.form.get("documento", "").strip()
        data_nascimento = request.form.get("data_nascimento", "").strip()
        contato = request.form.get("contato", "").strip()
        rua_numero = request.form.get("rua_numero", "").strip()
        bairro = request.form.get("bairro", "").strip()
        cidade = request.form.get("cidade", "").strip()
        estado = request.form.get("estado", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        # Verificação dos campos obrigatórios
        if not responsavel or not documento or not data_nascimento or not contato or not rua_numero or not bairro or not cidade or not estado:
            flash("Preencha todos os campos obrigatórios!", "erro")
            return render_template("familia/cadastro.html", dados=request.form)

        # Coleta os membros da família do formulário
        membros = []
        for chave in request.form:
            if chave.startswith("membros[") and chave.endswith("][nome]"):
                idx = chave.split("[")[1].split("]")[0]
                nome = capitalizar(request.form.get(f"membros[{idx}][nome]", ""))
                parentesco = request.form.get(f"membros[{idx}][parentesco]", "")
                data_membro = request.form.get(f"membros[{idx}][data_nascimento]", "")
                if nome and parentesco and data_membro:
                    membros.append((nome, parentesco, data_membro))

        # Inserção no banco de dados
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO familias (
                    responsavel, documento, data_nascimento, contato,
                    rua_numero, bairro, cidade, estado, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                responsavel, documento, data_nascimento, contato,
                rua_numero, bairro, cidade, estado, observacoes
            ))
            familia_id = cursor.lastrowid

            # Insere o responsável como membro principal
            cursor.execute("""
                INSERT INTO membros_familia (
                    familia_id, nome, parentesco, data_nascimento
                ) VALUES (?, ?, ?, ?)
            """, (
                familia_id, responsavel, "Responsável pela família", data_nascimento
            ))

            # Insere os demais membros
            for nome, parentesco, nascimento in membros:
                cursor.execute("""
                    INSERT INTO membros_familia (
                        familia_id, nome, parentesco, data_nascimento
                    ) VALUES (?, ?, ?, ?)
                """, (familia_id, nome, parentesco, nascimento))

            conn.commit()

        flash("Família cadastrada com sucesso!", "sucesso")
        return redirect(url_for("familia_cadastro.cadastrar_familia"))

    return render_template("familia/cadastro.html", dados=None)
