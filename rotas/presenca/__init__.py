from rotas.presenca.cadastro import presenca_cadastro
from rotas.presenca.editar import presenca_editar
from rotas.presenca.excluir import presenca_excluir
from rotas.presenca.listagem import presenca_listagem
from rotas.presenca.exportar_excel import presenca_exportar

rotas_presenca = [
    presenca_cadastro,
    presenca_editar,
    presenca_excluir,
    presenca_listagem,
    presenca_exportar
]
