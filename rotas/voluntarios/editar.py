from flask import Blueprint, render_template, request, redirect, url_for, flash
from banco.conexao import conectar

voluntarios_editar = Blueprint("voluntarios_editar", __name__)

def capitalizar(texto):
    excecoes = {"da", "de", "do", "das", "dos"}
    return " ".join([
        p.capitalize() if p.lower() not in excecoes else p.lower()
        for p in texto.split()
    ])

@voluntarios_editar.route("/voluntarios/editar/<int:voluntario_id>", methods=["GET", "POST"])
def editar_voluntarios(voluntario_id):
    with conectar() as conn:
        cursor = conn.cursor()

        if request.method == "POST":
            nome = capitalizar(request.form.get("nome", "").strip())
            contato = request.form.get("contato", "").strip()
            data_nascimento = request.form.get("data_nascimento", "").strip()

            if not nome or not contato:
                flash("Preencha os campos obrigatórios!", "erro")
                return redirect(url_for("voluntarios_editar.editar_voluntarios", voluntario_id=voluntario_id))

            cursor.execute("""
                UPDATE voluntarios SET
                    nome = ?, contato = ?, data_nascimento = ?
                WHERE id = ?
            """, (nome, contato, data_nascimento, voluntario_id))
            conn.commit()

            flash("Dados do voluntário atualizados com sucesso!", "sucesso")
            return redirect(url_for("voluntarios_editar.editar_voluntarios", voluntario_id=voluntario_id))

        # GET
        cursor.execute("SELECT * FROM voluntarios WHERE id = ?", (voluntario_id,))
        dados = cursor.fetchone()
        if not dados:
            flash("Voluntário não encontrado.", "erro")
            return redirect(url_for("comum.home"))

        colunas = [col[0] for col in cursor.description]
        voluntario = dict(zip(colunas, dados))

    return render_template("voluntarios/editar.html", voluntario=voluntario)