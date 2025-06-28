from banco.conexao import conectar

def criar_tabela_atividade():
    with conectar() as conn:
        cursor = conn.cursor()

        # Cria a tabela atividades se não existir (estrutura completa)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atividade TEXT NOT NULL,
                data TEXT NOT NULL,
                tema TEXT,
                responsavel TEXT,
                responsavel_id INTEGER,
                responsavel_tipo TEXT CHECK(responsavel_tipo IN ('pessoa', 'familia', 'voluntario', 'externo')),
                observacoes TEXT
            )
        """)

        # Cria a tabela de participantes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividade_participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atividade_id INTEGER NOT NULL,
                beneficiario_id INTEGER NOT NULL,
                beneficiario_tipo TEXT NOT NULL CHECK(beneficiario_tipo IN ('pessoa', 'familia')),
                FOREIGN KEY (atividade_id) REFERENCES atividades(id)
            )
        """)
        conn.commit()

