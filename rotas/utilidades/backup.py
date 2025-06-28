import os
import shutil
import subprocess
import platform
from datetime import datetime
from flask import Blueprint, jsonify, request

backup_bp = Blueprint("backup", __name__)

# Caminhos base
CAMINHO_BASE = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CAMINHO_BANCO = os.path.join(CAMINHO_BASE, "banco.db")
CAMINHO_FOTOS = os.path.join(CAMINHO_BASE, "static", "fotos")
CAMINHO_BACKUPS = os.path.join(CAMINHO_BASE, "backups")


@backup_bp.route("/fazer-backup")
def fazer_backup():
    try:
        os.makedirs(CAMINHO_BACKUPS, exist_ok=True)

        agora = datetime.now().strftime("backup_%Y-%m-%d_%H-%M-%S")
        caminho_backup = os.path.join(CAMINHO_BACKUPS, agora)
        os.makedirs(caminho_backup)

        # Banco
        if os.path.exists(CAMINHO_BANCO):
            shutil.copy2(CAMINHO_BANCO, os.path.join(caminho_backup, "banco.db"))
        else:
            return jsonify({"sucesso": False, "erro": "Banco de dados não encontrado."})

        # Fotos
        destino_static = os.path.join(caminho_backup, "static")
        destino_fotos = os.path.join(destino_static, "fotos")
        if os.path.exists(CAMINHO_FOTOS):
            os.makedirs(destino_static, exist_ok=True)
            shutil.copytree(CAMINHO_FOTOS, destino_fotos)
        else:
            os.makedirs(destino_fotos)

        # Abrir pasta de backups
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{CAMINHO_BACKUPS}"')
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", CAMINHO_BACKUPS])
        else:
            subprocess.Popen(["xdg-open", CAMINHO_BACKUPS])

        return jsonify({"sucesso": True, "mensagem": f"Backup salvo em: backups/{agora}/"})

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)})


@backup_bp.route("/instrucoes-backup")
def instrucoes_backup():
    try:
        instrucoes = """⚠️ ATENÇÃO

Para restaurar um backup manualmente, siga os passos:

1. Feche completamente o sistema Projeto Dignidade. Se tiver dificuldades, pressione Ctrl + Shift + Esc, vá na aba "Detalhes", localize "ProjetoDignidade.exe", clique com o botão direito e escolha "Finalizar processo".

2. Acesse a pasta 'backups' (que será aberta automaticamente agora).

3. Escolha uma das pastas com o nome: backup_YYYY-MM-DD_HH-MM-SS

4. Copie o arquivo 'banco.db' e a pasta 'static/' dessa pasta e cole na pasta principal do sistema, substituindo os arquivos existentes.

5. Após isso, reabra o sistema normalmente.

🔁 Dica: Abrindo a pasta 'backups' dentro da pasta do sistema, você pode escolher o backup e copiar manualmente para a pasta original, sem o sistema estar em execução. Isso evita erros de substituição.

⚠️ Todos os dados atuais serão perdidos ao fazer isso!
"""
        caminho_txt = os.path.join(CAMINHO_BACKUPS, "como_restaurar_backup.txt")
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(instrucoes)

        # Abrir pasta + bloco de notas
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{CAMINHO_BACKUPS}"')
            subprocess.Popen(["notepad", caminho_txt])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", CAMINHO_BACKUPS])
            subprocess.Popen(["open", caminho_txt])
        else:
            subprocess.Popen(["xdg-open", CAMINHO_BACKUPS])
            subprocess.Popen(["xdg-open", caminho_txt])

        return jsonify({"sucesso": True, "mensagem": "Instruções abertas com sucesso."})
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)})


@backup_bp.route("/listar-backups")
def listar_backups():
    try:
        os.makedirs(CAMINHO_BACKUPS, exist_ok=True)
        pastas = sorted(os.listdir(CAMINHO_BACKUPS), reverse=True)
        return jsonify({"pastas": pastas})
    except Exception as e:
        return jsonify({"erro": str(e)})
