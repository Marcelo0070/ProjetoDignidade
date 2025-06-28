from rotas.atividade.cadastro import atividade_cadastro
from rotas.atividade.editar import atividade_editar
from rotas.atividade.excluir import atividade_excluir
from rotas.atividade.listagem import atividade_listagem
from rotas.atividade.exportar_excel import atividade_exportar

rotas_atividade = [
    atividade_cadastro,
    atividade_editar,
    atividade_excluir,
    atividade_listagem,
    atividade_exportar
]
