from rotas.familia.cadastro import familia_cadastro
from rotas.familia.editar import familia_editar
from rotas.familia.excluir import familia_excluir
from rotas.familia.listagem import familia_listagem
from rotas.familia.exportar_excel import familia_exportar
from rotas.familia.perfil import familia_perfil

rotas_familia = [
    familia_cadastro,
    familia_editar,
    familia_excluir,
    familia_listagem,
    familia_perfil,
    familia_exportar
]
