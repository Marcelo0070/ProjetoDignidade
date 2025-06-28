from banco.conexao import conectar

def criar_tabela_voluntarios():
    """Cria a tabela de voluntários, se ainda não existir."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voluntarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT NOT NULL,
                data_nascimento TEXT
            )
        """)
        conn.commit()
