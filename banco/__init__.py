from banco.criar_tabela_pessoas import criar_tabela_pessoas
from banco.criar_tabela_familias import criar_tabela_familias
from banco.criar_tabela_visitas import criar_tabela_visitas
from banco.criar_tabela_doacoes import criar_tabela_doacoes
from banco.criar_tabela_voluntarios import criar_tabela_voluntarios
from banco.criar_tabela_presenca import criar_tabela_presenca
from banco.criar_tabela_atividade import criar_tabela_atividade

def inicializar_banco():
    criar_tabela_pessoas()
    criar_tabela_visitas()
    criar_tabela_doacoes()
    criar_tabela_voluntarios()
    criar_tabela_familias()
    criar_tabela_presenca()
    criar_tabela_atividade()
