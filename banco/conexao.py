import sqlite3

def conectar():
    """Abre conexão com o banco SQLite local."""
    return sqlite3.connect("banco.db")

