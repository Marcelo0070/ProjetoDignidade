from flask import Flask, send_from_directory
from pathlib import Path
import webbrowser
from threading import Thread
import time
import http.client
import sys
import os
import socket

from banco import inicializar_banco
from rotas import rotas

# 🔒 Impede múltiplas instâncias usando porta exclusiva
def impedir_multiplas_instancias(porta=54321):
    """Evita múltiplas instâncias do app usando uma porta exclusiva."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", porta))
    except socket.error:
        sys.exit(0)  # já tem uma instância rodando

# 🌐 Inicialização do Flask
app = Flask(__name__, static_folder="static")
app.secret_key = "projeto-dignidade-chave-secreta"

# Diretórios
BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
PASTA_STATIC = BASE_DIR / "static"
PASTA_FOTOS = PASTA_STATIC / "fotos"
PASTA_FOTOS.mkdir(parents=True, exist_ok=True)

# Registrar rotas
for rota in rotas:
    app.register_blueprint(rota)

# Inicializar banco
inicializar_banco()

@app.route("/")
def home():
    return "Projeto Dignidade rodando com sucesso."

@app.route("/static/fotos/<nome_arquivo>")
def servir_foto_static(nome_arquivo):
    return send_from_directory(PASTA_FOTOS, nome_arquivo)

def iniciar_flask():
    app.run(debug=False, port=5000, use_reloader=False)

def esperar_servidor():
    while True:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", 5000, timeout=2)
            conn.request("GET", "/")
            if conn.getresponse().status == 200:
                return
        except:
            time.sleep(1)

def monitorar_navegador():
    falhas = 0
    while True:
        time.sleep(3)
        try:
            conn = http.client.HTTPConnection("127.0.0.1", 5000, timeout=2)
            conn.request("GET", "/")
            conn.getresponse()
            falhas = 0
        except:
            falhas += 1
            if falhas >= 5:
                os._exit(0)

if __name__ == "__main__":
    impedir_multiplas_instancias()  # ✅ trava se já tiver aberto
    Thread(target=iniciar_flask, daemon=True).start()
    esperar_servidor()
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")
    Thread(target=monitorar_navegador, daemon=True).start()
    while True:
        time.sleep(1)
