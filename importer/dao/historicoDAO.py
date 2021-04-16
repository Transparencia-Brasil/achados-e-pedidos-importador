from importer.models import HistoricoImportacao
from datetime import datetime

CONST_TARGET = 'default'  # this table is on the sqlite database


# nome_usuario - nome do usuario usado no arquivo (nome do arquivo)
# num_pedidos - total de pedidos processados
# num_interacoes - total de interacoes processados
# usuario_logado - nome do usuario que importou a planilha usando o importador
def salvar_importacao(nome_usuario, num_pedidos, num_interacoes, num_anexos, nome_target, usuario_logado):
    historico = HistoricoImportacao(usuario = nome_usuario, pedidos = num_pedidos, interacoes = num_interacoes, criacao = datetime.now(), usuario_tb = usuario_logado, anexos = num_anexos, target = nome_target)

    historico.save(using=CONST_TARGET)


def busca_historico():
    historico = HistoricoImportacao.objects.using(CONST_TARGET).order_by('-criacao')
    return historico


