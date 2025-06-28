from flask import Blueprint, render_template, request, flash, redirect, url_for
from banco.conexao import conectar
from rotas.utilidades.geral import capitalizar, salvar_foto_upload, converter_checkbox

pessoa_cadastro = Blueprint("pessoa_cadastro", __name__)

@pessoa_cadastro.route("/pessoa/cadastro", methods=["GET", "POST"])
def cadastrar_pessoa():
    if request.method == "POST":
        # Dados principais do formulário
        nome = capitalizar(request.form.get("nome", ""))
        apelido = capitalizar(request.form.get("apelido", ""))
        nome_mae = capitalizar(request.form.get("nome_mae", ""))
        documento = request.form.get("documento", "")
        data_nascimento = request.form.get("data_nascimento", "")

        # Endereço e contato
        rua_numero = request.form.get("rua_numero", "")
        bairro = request.form.get("bairro", "")
        cidade = request.form.get("cidade", "")
        estado = request.form.get("estado", "")
        dependencia = request.form.get("dependencia", "")
        contato = request.form.get("contato", "")

        # Campos complementares
        naturalidade = request.form.get("naturalidade", "")
        tamanho_roupa = request.form.get("tamanho_roupa", "")
        aptidoes = request.form.get("aptidoes", "")
        alergia = request.form.get("alergia", "")
        saude = request.form.get("saude", "")
        alfabetizacao = request.form.get("alfabetizacao", "")
        primeiro_dia = request.form.get("primeiro_dia", "")
        termo_imagem = converter_checkbox(request.form.get("termo_imagem"))
        observacoes = request.form.get("observacoes", "")

        # Validação mínima
        if not nome or not data_nascimento:
            flash("Preencha o nome e a data de nascimento.", "erro")
            return render_template("pessoa/cadastro.html", dados=request.form)

        # Processamento das imagens
        foto = None
        foto_extra = None

        if "foto" in request.files:
            arq = request.files["foto"]
            if arq and arq.filename:
                foto = salvar_foto_upload(arq, nome, "_1")

        if "foto_extra" in request.files:
            arq = request.files["foto_extra"]
            if arq and arq.filename:
                foto_extra = salvar_foto_upload(arq, nome, "_2")

        with conectar() as conn:
            cursor = conn.cursor()

            # Inserção da pessoa
            cursor.execute("""
                INSERT INTO pessoas (
                    nome, apelido, nome_mae, documento, data_nascimento,
                    rua_numero, bairro, cidade, estado, dependencia,
                    contato, observacoes, foto, naturalidade, familiares,
                    tamanho_roupa, aptidoes, alergia, saude, alfabetizacao,
                    foto_extra, termo_imagem, primeiro_dia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome, apelido, nome_mae, documento, data_nascimento,
                rua_numero, bairro, cidade, estado, dependencia,
                contato, observacoes, foto, naturalidade, "",  # 'familiares' legado, vazio
                tamanho_roupa, aptidoes, alergia, saude, alfabetizacao,
                foto_extra, termo_imagem, primeiro_dia
            ))

            pessoa_id = cursor.lastrowid

            # Inserção dos familiares vinculados à pessoa
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

        flash("Pessoa cadastrada com sucesso!", "sucesso")
        return redirect(url_for("pessoa_cadastro.cadastrar_pessoa"))

    return render_template("pessoa/cadastro.html", dados=None)


