from banco.conexao import conectar

def criar_tabela_pessoas():
    """Cria a tabela de pessoas atendidas e seus familiares, se ainda não existirem."""
    with conectar() as conn:
        cursor = conn.cursor()

        # Tabela principal de pessoas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                apelido TEXT,
                nome_mae TEXT,
                documento TEXT,
                data_nascimento TEXT,
                rua_numero TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                dependencia TEXT,
                contato TEXT,
                observacoes TEXT,
                foto TEXT,
                naturalidade TEXT,
                familiares TEXT,
                tamanho_roupa TEXT,
                aptidoes TEXT,
                alergia TEXT,
                saude TEXT,
                alfabetizacao TEXT,
                foto_extra TEXT,
                termo_imagem INTEGER,
                primeiro_dia TEXT
            )
        """)

        # Tabela de familiares vinculada a cada pessoa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS familiares_pessoa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pessoa_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                parentesco TEXT NOT NULL,
                data_nascimento TEXT,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Tabelas 'pessoas' e 'familiares_pessoa' criadas (ou já existentes).")

if __name__ == "__main__":
    criar_tabela_pessoas()

