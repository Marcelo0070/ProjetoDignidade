import os
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime

CAMINHO_FOTOS = "static/fotos/"

def capitalizar(texto):
    """Capitaliza nomes próprios, mantendo preposições minúsculas."""
    excecoes = {"da", "de", "do", "das", "dos"}
    return " ".join([
        p.capitalize() if p.lower() not in excecoes else p.lower()
        for p in texto.split()
    ])

def salvar_foto_upload(arquivo, nome_base, sufixo=""):
    """
    Salva uma imagem enviada pelo usuário:
    - Redimensiona para 300x300px.
    - Salva em JPEG, com qualidade 60.
    - Retorna caminho relativo para salvar no banco.
    """
    os.makedirs(CAMINHO_FOTOS, exist_ok=True)
    nome_arquivo = secure_filename(nome_base.lower().replace(" ", "_") + sufixo)
    caminho_final = os.path.join(CAMINHO_FOTOS, f"{nome_arquivo}.jpg")

    imagem = Image.open(arquivo)
    imagem = imagem.convert("RGB")
    imagem.thumbnail((300, 300))
    imagem.save(caminho_final, format="JPEG", quality=60)

    return f"fotos/{nome_arquivo}.jpg"

def limpar_texto(texto):
    """Remove espaços duplos, quebras de linha e capitaliza."""
    if not texto:
        return ""
    return capitalizar(" ".join(texto.strip().split()))

def converter_checkbox(valor):
    """Converte valor de checkbox (on/None) em 1 ou 0."""
    return 1 if valor else 0

def calcular_idade(data_nascimento):
    try:
        nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
        hoje = datetime.today()
        return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    except:
        return "—"

def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return "—"