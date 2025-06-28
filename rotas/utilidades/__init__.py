from .buscar_beneficiario import buscar_beneficiario
from .buscar_voluntario import buscar_voluntario
from .buscar_endereco import buscar_endereco
from rotas.utilidades.backup import backup_bp

rotas_utilidades = [
    buscar_beneficiario,
    buscar_voluntario,
    buscar_endereco, 
    backup_bp
]

