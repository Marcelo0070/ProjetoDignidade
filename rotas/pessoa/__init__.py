from rotas.pessoa.cadastro import pessoa_cadastro
from rotas.pessoa.editar import pessoa_editar
from rotas.pessoa.excluir import pessoa_excluir
from rotas.pessoa.listagem import pessoa_listagem
from rotas.pessoa.perfil import pessoa_perfil
from rotas.pessoa.exportar_excel import pessoa_exportar

rotas_pessoa = [
    pessoa_cadastro,
    pessoa_editar,
    pessoa_excluir,
    pessoa_listagem,
    pessoa_perfil,
    pessoa_exportar
]