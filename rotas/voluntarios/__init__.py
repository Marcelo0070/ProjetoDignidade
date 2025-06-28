from rotas.voluntarios.cadastro import voluntarios_cadastro
from rotas.voluntarios.editar import voluntarios_editar
from rotas.voluntarios.excluir import voluntarios_excluir
from rotas.voluntarios.listagem import voluntarios_listagem
from rotas.voluntarios.exportar_excel import voluntarios_exportar

rotas_voluntarios = [
    voluntarios_cadastro,
    voluntarios_editar,
    voluntarios_excluir,
    voluntarios_listagem,
    voluntarios_exportar
]