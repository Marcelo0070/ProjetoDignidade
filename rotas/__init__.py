from rotas.comum import comum
from rotas.pessoa import rotas_pessoa
from rotas.familia import rotas_familia
from rotas.visitas import rotas_visitas
from rotas.voluntarios import rotas_voluntarios
from rotas.doacoes import rotas_doacoes
from rotas.presenca import rotas_presenca
from rotas.atividade import rotas_atividade
from rotas.utilidades import rotas_utilidades  

rotas = (
    [comum]
    + rotas_pessoa
    + rotas_familia
    + rotas_visitas
    + rotas_voluntarios
    + rotas_doacoes
    + rotas_presenca
    + rotas_atividade
    + rotas_utilidades 
)
