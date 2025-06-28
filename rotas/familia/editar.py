from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
from rotas.utilidades.geral import capitalizar

familia_editar = Blueprint("familia_editar", __name__)

@familia_editar.route("/familia/editar/<int:familia_id>", methods=["GET", "POST"])
def editar_familia(familia_id):
    with conectar() as conn:
        cursor = conn.cursor()

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

            if not responsavel or not documento or not data_nascimento or not contato or not rua_numero or not bairro or not cidade or not estado:
                flash("Preencha todos os campos obrigatórios!", "erro")
                return redirect(url_for("familia_editar.editar_familia", familia_id=familia_id))

            # Atualiza dados da família
            cursor.execute("""
                UPDATE familias SET
                    responsavel=?, documento=?, data_nascimento=?, contato=?,
                    rua_numero=?, bairro=?, cidade=?, estado=?, observacoes=?
                WHERE id=?
            """, (
                responsavel, documento, data_nascimento, contato,
                rua_numero, bairro, cidade, estado, observacoes, familia_id
            ))

            # Remove membros antigos
            cursor.execute("DELETE FROM membros_familia WHERE familia_id = ?", (familia_id,))

            # Insere membros restantes do formulário
            for chave in request.form:
                if chave.startswith("membros[") and chave.endswith("][nome]"):
                    idx = chave.split("[")[1].split("]")[0]
                    nome = capitalizar(request.form.get(f"membros[{idx}][nome]", ""))
                    parentesco = request.form.get(f"membros[{idx}][parentesco]", "")
                    data_membro = request.form.get(f"membros[{idx}][data_nascimento]", "")

                    # Evita duplicar o responsável
                    if (
                        nome.strip().lower() == responsavel.strip().lower()
                        and parentesco.strip().lower() == "responsável pela família"
                    ):
                        continue

                    if nome and parentesco and data_membro:
                        cursor.execute("""
                            INSERT INTO membros_familia (
                                familia_id, nome, parentesco, data_nascimento
                            ) VALUES (?, ?, ?, ?)
                        """, (familia_id, nome, parentesco, data_membro))

            conn.commit()
            flash("Família atualizada com sucesso!", "sucesso")
            return redirect(url_for("familia_editar.editar_familia", familia_id=familia_id))

        # GET: Buscar dados da família
        cursor.execute("SELECT * FROM familias WHERE id = ?", (familia_id,))
        dados_familia = cursor.fetchone()
        if not dados_familia:
            flash("Família não encontrada.", "erro")
            return redirect(url_for("comum.home"))

        colunas = [col[0] for col in cursor.description]
        familia = dict(zip(colunas, dados_familia))

        # Buscar membros da família
        cursor.execute("SELECT nome, parentesco, data_nascimento FROM membros_familia WHERE familia_id = ?", (familia_id,))
        membros = [dict(zip(["nome", "parentesco", "data_nascimento"], linha)) for linha in cursor.fetchall()]
        familia["membros"] = membros  # 🔑 ESSENCIAL para funcionar no HTML


    return render_template("familia/editar.html", familia=familia)