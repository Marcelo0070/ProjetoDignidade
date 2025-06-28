from banco.conexao import conectar

def criar_tabela_visitas():
    """Cria a tabela de visitas e a tabela associativa para múltiplos voluntários."""
    with conectar() as conn:
        cursor = conn.cursor()

        # Tabela principal de visitas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                beneficiario_id INTEGER NOT NULL,
                beneficiario_tipo TEXT NOT NULL CHECK(beneficiario_tipo IN ('pessoa', 'familia')),
                data_visita TEXT NOT NULL,
                endereco TEXT NOT NULL,
                observacoes TEXT,
                FOREIGN KEY (beneficiario_id) REFERENCES pessoas(id)
            )
        """)

        # Tabela de associação entre visita e voluntários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visita_voluntarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visita_id INTEGER NOT NULL,
                voluntario_id INTEGER NOT NULL,
                FOREIGN KEY (visita_id) REFERENCES visitas(id) ON DELETE CASCADE,
                FOREIGN KEY (voluntario_id) REFERENCES voluntarios(id)
            )
        """)

        conn.commit()
        print("Tabelas 'visitas' e 'visita_voluntarios' criadas (ou já existentes).")

if __name__ == "__main__":
    criar_tabela_visitas()

