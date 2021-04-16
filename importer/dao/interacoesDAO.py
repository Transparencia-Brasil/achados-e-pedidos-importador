from importer.models import Pedidos, PedidosInteracoes, PedidosAnexos, TipoPedidoResposta
from _datetime import datetime


CONST_TIPO_RESPOSTA = 1  # Tipo de reposta padrão do importador
CONST_ATIVO = 1  #Anexo Ativo


def inserir_interacao(colunas, pedido, tipo, target):
    if pedido is None:
        raise ValueError('Pedido não encontrado, verifique se há pedido para essa interação.')

    data = None
    if colunas[5] is None or colunas[5] == '':
        raise ValueError('Coluna Data vazia')
    try:
        spliter = '/' if '/' in colunas[5] else '-'
        pattern = '%d' + spliter + '%m' + spliter + '%Y'
        if ':' in colunas[5]:
            pattern = '%d' + spliter + '%m' + spliter + '%Y' + ' %H:%M:%S'
        if len(colunas) > 16 and colunas[16] != '':
            pattern = colunas[16]
        data = datetime.strptime(colunas[5], pattern)
    except ValueError:
        raise ValueError('Coluna Data incorreta!')
    except TypeError:
        raise ValueError('Coluna Data incorreta!')

    tipo_resposta = busca_tipo_resposta_nome(tipo, target)
    if tipo_resposta is None or len(tipo_resposta) < 1:
        raise ValueError('Tipo de resposta não encontrado!')

    old_interacao = busca_interacao(pedido, tipo_resposta[0], target)

    interacao = PedidosInteracoes(codigopedido=pedido, dataresposta=data, descricao=colunas[3],
                                  codigotipopedidoresposta=tipo_resposta[0], criacao=datetime.today(),
                                  alteracao=datetime.today())

    if old_interacao:
        interacao.codigo = old_interacao.codigo
        interacao.criacao = old_interacao.criacao

    interacao.save(using=target)
    return interacao


def inserir_anexo(interacao, path, filename, target):
    anexo = PedidosAnexos(codigopedidointeracao=interacao, arquivofullpath=path, ativo=CONST_ATIVO, criacao=datetime.today(),
                          alteracao=datetime.today(), codigostatusexportacaoes='esperando', arquivo=filename)

    old_anexo = busca_anexo(interacao, filename, target)
    if old_anexo is not None:
        anexo.codigo = old_anexo.codigo

    anexo.save(using=target)
    return anexo


def busca_interacao(pedido, tipo, target):
    interacao = PedidosInteracoes.objects.using(target).filter(codigopedido=pedido)
    interacao = interacao.filter(codigotipopedidoresposta=tipo)
    return interacao.first()


def busca_anexo(interacao, filename, target):
    anexo = PedidosAnexos.objects.using(target).filter(codigopedidointeracao=interacao)
    anexo = anexo.filter(arquivo__iexact=filename)
    return anexo.first()


def busca_interacoes_codigo(cod, target):
    return PedidosInteracoes.objects.using(target).get(pk=cod)


def busca_anexo_codigo(cod, target):
    return PedidosAnexos.objects.using(target).get(pk=cod)


def busca_tipo_resposta(cod, target):
    return TipoPedidoResposta.objects.using(target).get(pk=cod)


def busca_tipo_resposta_nome(tipo, target):
    if tipo == 'Resposta do Pedido':
        tipo = 'Resposta do órgão público'
    return TipoPedidoResposta.objects.using(target).filter(nome__iexact=tipo)

