from rotas.doacoes.entrada import doacao_entrada
from rotas.doacoes.saida import doacao_saida
from rotas.doacoes.listagem import doacao_listagem
from rotas.doacoes.editar_entrada import editar_entrada
from rotas.doacoes.editar_saida import editar_saida
from rotas.doacoes.excluir import doacao_excluir
from rotas.doacoes.exportar_excel import doacao_exportar

rotas_doacoes = [
    doacao_entrada,
    doacao_saida,
    doacao_listagem,
    editar_entrada,
    editar_saida,
    doacao_excluir,
    doacao_exportar
]