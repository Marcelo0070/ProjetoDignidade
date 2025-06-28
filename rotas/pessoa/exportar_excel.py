from flask import Blueprint, request, send_file, flash, redirect, url_for
from banco.conexao import conectar
from datetime import datetime
import pandas as pd
import io

pessoa_exportar = Blueprint("pessoa_exportar", __name__)

@pessoa_exportar.route("/pessoa/exportar", methods=["POST"])
def exportar_excel():
    try:
        ids = request.form.get("ids")
        colunas = request.form.get("colunas")

        if not ids or not colunas:
            flash("Nenhuma pessoa ou coluna selecionada para exportação.", "erro")
            return redirect(url_for("pessoa_listagem.lista_pessoas"))

        ids = [int(i) for i in eval(ids)]
        colunas = eval(colunas)

        campos_validos = {
            "nome": "nome",
            "apelido": "apelido",
            "documento": "documento",
            "data_nascimento": "data_nascimento",
            "idade": None,
            "nome_mae": "nome_mae",
            "dependencia": "dependencia",
            "contato": "contato",
            "endereco": ["rua_numero", "bairro", "cidade", "estado"],
            "observacoes": "observacoes",
            "naturalidade": "naturalidade",
            "tamanho_roupa": "tamanho_roupa",
            "aptidoes": "aptidoes",
            "saude": "saude",
            "alfabetizacao": "alfabetizacao",
            "termo_imagem": "termo_imagem",
            "primeiro_dia": "primeiro_dia"
        }

        campos_sql = []
        for c in colunas:
            f = campos_validos.get(c)
            if isinstance(f, list):
                campos_sql.extend(f)
            elif f:
                campos_sql.append(f)

        if "data_nascimento" not in campos_sql and "idade" in colunas:
            campos_sql.append("data_nascimento")

        if "nome" not in campos_sql:
            campos_sql.insert(0, "nome")

        with conectar() as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT {', '.join(campos_sql)} FROM pessoas
                WHERE id IN ({','.join(['?'] * len(ids))})
            """
            cursor.execute(query, ids)
            registros = cursor.fetchall()
            nomes_colunas = [col[0] for col in cursor.description]

        df = pd.DataFrame(registros, columns=nomes_colunas)

        # Cálculo da idade
        if "idade" in colunas and "data_nascimento" in df:
            def idade(data):
                try:
                    nascimento = datetime.strptime(data, "%Y-%m-%d")
                    hoje = datetime.today()
                    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
                except:
                    return ""
            df["idade"] = df["data_nascimento"].apply(idade)

        # Montagem do endereço
        if "endereco" in colunas:
            for p in ["rua_numero", "bairro", "cidade", "estado"]:
                if p not in df:
                    df[p] = ""
            df["endereco"] = df["rua_numero"] + ", " + df["bairro"] + ", " + df["cidade"] + " - " + df["estado"]
            df.drop(columns=["rua_numero", "bairro", "cidade", "estado"], inplace=True, errors="ignore")

        # Formatação da data
        if "primeiro_dia" in df:
            df["primeiro_dia"] = df["primeiro_dia"].apply(lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else "")

        # Reorganizar colunas na ordem correta
        colunas_final = []
        for c in colunas:
            if c in df.columns:
                colunas_final.append(c)
            elif c == "idade" and "idade" in df:
                colunas_final.append("idade")
            elif c == "endereco" and "endereco" in df:
                colunas_final.append("endereco")

        df = df[["nome"] + [c for c in colunas_final if c != "nome"]]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Pessoas")

        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="pessoas_exportadas.xlsx"
        )

    except Exception as e:
        flash(f"Erro ao exportar: {e}", "erro")
        return redirect(url_for("pessoa_listagem.lista_pessoas"))
