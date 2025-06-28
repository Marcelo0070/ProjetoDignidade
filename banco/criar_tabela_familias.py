from banco.conexao import conectar

def criar_tabela_familias():
    with conectar() as conn:
        cursor = conn.cursor()
        # Tabela principal de Responsavel da Familia
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS familias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                responsavel TEXT NOT NULL,
                data_nascimento TEXT,
                documento TEXT,
                rua_numero TEXT NOT NULL,
                bairro TEXT NOT NULL,
                cidade TEXT NOT NULL,
                estado TEXT NOT NULL,
                contato TEXT NOT NULL,
                observacoes TEXT
            )
        """)
        # Tabela de familiares vinculada a Responsavel
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membros_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                familia_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                parentesco TEXT NOT NULL,
                data_nascimento TEXT,
                FOREIGN KEY (familia_id) REFERENCES familias(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
