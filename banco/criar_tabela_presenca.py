from banco.conexao import conectar

def criar_tabela_presenca():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presenca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                beneficiario_id INTEGER NOT NULL,
                beneficiario_tipo TEXT NOT NULL
            )
        """)
        conn.commit()
