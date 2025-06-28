from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar
from werkzeug.utils import secure_filename
from rotas.utilidades.geral import capitalizar, salvar_foto_upload, converter_checkbox

pessoa_editar = Blueprint("pessoa_editar", __name__)
CAMINHO_FOTOS = "static/fotos/"

@pessoa_editar.route("/pessoa/editar/<int:pessoa_id>", methods=["GET", "POST"])
def editar_pessoa(pessoa_id):
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            # Coleta os dados do formulário
            nome = capitalizar(request.form.get("nome", ""))
            apelido = capitalizar(request.form.get("apelido", ""))
            nome_mae = capitalizar(request.form.get("nome_mae", ""))
            documento = request.form.get("documento", "")
            data_nascimento = request.form.get("data_nascimento", "")
            rua_numero = request.form.get("rua_numero", "")
            bairro = request.form.get("bairro", "")
            cidade = request.form.get("cidade", "")
            estado = request.form.get("estado", "")
            dependencia = request.form.get("dependencia", "")
            contato = request.form.get("contato", "")
            observacoes = request.form.get("observacoes", "")
            naturalidade = request.form.get("naturalidade", "")
            tamanho_roupa = request.form.get("tamanho_roupa", "")
            aptidoes = request.form.get("aptidoes", "")
            alergia = request.form.get("alergia", "")
            saude = request.form.get("saude", "")
            alfabetizacao = request.form.get("alfabetizacao", "")
            primeiro_dia = request.form.get("primeiro_dia", "")
            termo_imagem = converter_checkbox(request.form.get("termo_imagem"))

            # Processa imagens
            caminho_foto = None
            caminho_foto_extra = None
            nome_arquivo_base = secure_filename(nome.lower().replace(" ", "_"))

            if "foto" in request.files:
                arquivo = request.files["foto"]
                if arquivo and arquivo.filename:
                    caminho_foto = salvar_foto_upload(arquivo, nome_arquivo_base, "_1")

            if "foto_extra" in request.files:
                arquivo = request.files["foto_extra"]
                if arquivo and arquivo.filename:
                    caminho_foto_extra = salvar_foto_upload(arquivo, nome_arquivo_base, "_2")

            # Atualização da pessoa
            campos = [
                nome, apelido, nome_mae, documento, data_nascimento,
                rua_numero, bairro, cidade, estado, dependencia,
                contato, observacoes, naturalidade, tamanho_roupa,
                aptidoes, alergia, saude, alfabetizacao,
                primeiro_dia, termo_imagem
            ]
            query = """
                UPDATE pessoas SET
                    nome=?, apelido=?, nome_mae=?, documento=?, data_nascimento=?,
                    rua_numero=?, bairro=?, cidade=?, estado=?, dependencia=?,
                    contato=?, observacoes=?, naturalidade=?, tamanho_roupa=?,
                    aptidoes=?, alergia=?, saude=?, alfabetizacao=?,
                    primeiro_dia=?, termo_imagem=?
            """

            if caminho_foto:
                query += ", foto=?"
                campos.append(caminho_foto)

            if caminho_foto_extra:
                query += ", foto_extra=?"
                campos.append(caminho_foto_extra)

            query += " WHERE id=?"
            campos.append(pessoa_id)

            cursor.execute(query, tuple(campos))

            # Atualiza os familiares (remove e reinsere)
            cursor.execute("DELETE FROM familiares_pessoa WHERE pessoa_id = ?", (pessoa_id,))
            i = 0
            while True:
                nome_f = request.form.get(f"membros[{i}][nome]")
                if not nome_f:
                    break
                parentesco = request.form.get(f"membros[{i}][parentesco]", "")
                data_nasc = request.form.get(f"membros[{i}][data_nascimento]", "")
                cursor.execute("""
                    INSERT INTO familiares_pessoa (pessoa_id, nome, parentesco, data_nascimento)
                    VALUES (?, ?, ?, ?)
                """, (pessoa_id, capitalizar(nome_f), parentesco, data_nasc))
                i += 1

            conn.commit()
            flash("Dados atualizados com sucesso!", "sucesso")
            return redirect(url_for("pessoa_listagem.lista_pessoas"))

        # GET: busca dados da pessoa
        cursor.execute("SELECT * FROM pessoas WHERE id = ?", (pessoa_id,))
        dados = cursor.fetchone()

        if not dados:
            flash("Pessoa não encontrada.", "erro")
            return redirect(url_for("pessoa_listagem.lista_pessoas"))

        colunas = [col[0] for col in cursor.description]
        pessoa = dict(zip(colunas, dados))

        # Busca familiares vinculados e transforma em dicionários
        cursor.execute("SELECT nome, parentesco, data_nascimento FROM familiares_pessoa WHERE pessoa_id = ?", (pessoa_id,))
        familiares = cursor.fetchall()
        pessoa["familiares"] = [dict(zip(["nome", "parentesco", "data_nascimento"], f)) for f in familiares]

    return render_template("pessoa/editar.html", pessoa=pessoa)
