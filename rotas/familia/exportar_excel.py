from flask import Blueprint, request, send_file, flash, redirect, url_for
from banco.conexao import conectar
import pandas as pd
import io
from datetime import datetime

familia_exportar = Blueprint("familia_exportar", __name__)

@familia_exportar.route("/familia/exportar", methods=["POST"])
def exportar_excel():
    try:
        raw_ids = eval(request.form.get("ids"))
        colunas = eval(request.form.get("colunas"))

        if not raw_ids or not colunas:
            flash("Nenhum indivíduo ou coluna selecionada para exportação.", "erro")
            return redirect(url_for("familia_listagem.lista_familias"))

        # Separa IDs de membros e IDs de responsáveis
        ids_membros = [int(i) for i in raw_ids if str(i).isdigit()]
        ids_responsaveis = [int(i[1:]) for i in raw_ids if isinstance(i, str) and i.startswith("r")]

        # Campos obrigatórios e opcionais
        obrigatorios = ["nome", "parentesco", "responsavel", "idade"]
        opcionais = ["documento", "contato", "endereco", "observacoes"]
        todos_campos = obrigatorios + [c for c in colunas if c in opcionais]

        # Função para calcular idade
        def calcular_idade(data_nascimento):
            try:
                nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
                hoje = datetime.today()
                return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            except:
                return ""

        with conectar() as conn:
            cursor = conn.cursor()

            # Carrega membros
            cursor.execute("SELECT * FROM membros_familia")
            col_membro = [desc[0] for desc in cursor.description]
            membros_raw = [dict(zip(col_membro, row)) for row in cursor.fetchall()]

            # Carrega famílias
            cursor.execute("SELECT * FROM familias")
            col_familia = [desc[0] for desc in cursor.description]
            familias_raw = {row[0]: dict(zip(col_familia, row)) for row in cursor.fetchall()}

        linhas = []

        # Adiciona membros selecionados
        for m in membros_raw:
            if m["id"] in ids_membros:
                familia = familias_raw.get(m["familia_id"])
                if not familia:
                    continue
                linha = {
                    "nome": m["nome"],
                    "parentesco": m["parentesco"],
                    "responsavel": familia.get("responsavel", ""),
                    "idade": calcular_idade(m.get("data_nascimento")),
                    "documento": familia.get("documento", ""),
                    "contato": familia.get("contato", ""),
                    "endereco": f"{familia.get('rua_numero','')}, {familia.get('bairro','')}, {familia.get('cidade','')} - {familia.get('estado','')}",
                    "observacoes": familia.get("observacoes", "")
                }
                linhas.append({k: linha[k] for k in todos_campos if k in linha})

        # Adiciona responsáveis selecionados
        for f_id in ids_responsaveis:
            f = familias_raw.get(f_id)
            if not f:
                continue
            linha = {
                "nome": f["responsavel"],
                "parentesco": "Responsável",
                "responsavel": f["responsavel"],
                "idade": calcular_idade(f.get("data_nascimento")),
                "documento": f.get("documento", ""),
                "contato": f.get("contato", ""),
                "endereco": f"{f.get('rua_numero','')}, {f.get('bairro','')}, {f.get('cidade','')} - {f.get('estado','')}",
                "observacoes": f.get("observacoes", "")
            }
            linhas.append({k: linha[k] for k in todos_campos if k in linha})

        if not linhas:
            flash("Nenhum dado encontrado para exportação.", "erro")
            return redirect(url_for("familia_listagem.lista_familias"))

        # Gera o Excel
        df = pd.DataFrame(linhas)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Individuos")

        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="individuos_exportados.xlsx"
        )

    except Exception as e:
        flash(f"Erro ao exportar: {e}", "erro")
        return redirect(url_for("familia_listagem.lista_familias"))
