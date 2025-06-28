from banco.conexao import conectar

def criar_tabela_doacoes():
    """Cria a tabela de doações se ainda não existir."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                origem TEXT,
                destino_id INTEGER,
                destino_tipo TEXT,  -- 'pessoa' ou 'familia'
                data TEXT NOT NULL,
                observacoes TEXT,
                tipo_movimentacao TEXT NOT NULL  -- 'entrada' ou 'saida'
            )
        """)
        conn.commit()