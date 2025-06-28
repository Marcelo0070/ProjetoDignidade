from rotas.visitas.cadastro import visitas_cadastro
from rotas.visitas.editar import visitas_editar
from rotas.visitas.excluir import visitas_excluir
from rotas.visitas.listagem import visitas_listagem
from rotas.visitas.exportar_excel import visitas_exportar

rotas_visitas = [
    visitas_cadastro,
    visitas_editar,
    visitas_excluir,
    visitas_listagem,
    visitas_exportar
]