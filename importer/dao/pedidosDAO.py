import sys
from importer.helper import format_text_value
from importer.models import Pedidos, StatusPedido, TipoPedidoOrigem, TipoPedidoSituacao, Agentes, Usuarios
from _datetime import datetime
from ..helper import get_slug, format_text_value

CONST_TIPO_ORIGEM = 3  # define o "tipo origem" do pedido como importação
CONST_STATUS_INTERNO = 4  # define o status interno como 'não classificado'
CONST_ATIVO = 1 # define o pedido como ativo


def inserir_pedido(colunas, usuario, agente, target):
    situacao = busca_pedido_situacao(colunas[9], target)
    if situacao is None or len(situacao) <= 0:
        raise ValueError('Coluna Situacao incorreta')
    status = busca_status_pedido(colunas[8], target)
    if status is None or len(status) <= 0:
        raise ValueError('Coluna Status incorreta')
    status_interno = busca_status_interno(target)
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
        raise ValueError('Coluna Data incorreta')
    except TypeError:
        raise ValueError('Coluna Data incorreta')

    prorrogado = 0
    if colunas[6] is not None and format_text_value(colunas[6]) == 'sim':
        prorrogado = 1

    pedido = Pedidos(codigousuario=usuario, codigoagente=agente, codigotipoorigem=busca_pedido_origem(target),
                     codigotipopedidosituacao=situacao[0], codigostatuspedido=status[0], codigostatuspedidointerno=status_interno,
                     protocolo=colunas[1], titulo=colunas[2], descricao=colunas[3], dataenvio=data, foiprorrogado=prorrogado,
                     ativo=CONST_ATIVO, criacao=datetime.today(), alteracao=datetime.today())

    update = busca_pedido_data(colunas[1], agente, data, usuario, target).first()
    if update:
        pedido.codigo = update.codigo
        pedido.slug = update.slug
        pedido.criacao = update.criacao
        pedido.save(force_update=True, using=target)
    else:
        pedido.criacao=datetime.today()
        pedido.save(force_insert=True, using=target)
        if pedido is not None and pedido.codigo is not None:
            slug = get_slug(pedido.titulo, pedido.codigo)
            pedido.slug = slug
            pedido.save(using=target, force_update=True, update_fields=['slug'])
        else:
            raise ValueError('Erro desconhecido ao salvar pedido, por favor tente novamente!')

    return pedido


def busca_pedido_codigo(cod, target):
    return Pedidos.objects.using(target).get(pk=cod)


def busca_pedido(num_protocolo, agente, usuario, target):
    pedido = Pedidos.objects.using(target).filter(protocolo=num_protocolo)  # busca os pedidos com tal protocolo
    pedido = pedido.filter(codigoagente=agente)  # feitos a tal agente
    pedido = pedido.filter(codigousuario=usuario)  # por tal usuario

    # print('TESTEF {}'.format(pedido.query))  # FOR DEBUG PURPOSES ONLY

    return pedido.first()


def busca_pedido_data(num_protocolo, agente, data, usuario, target):
    pedido = Pedidos.objects.using(target).filter(protocolo=num_protocolo)  # busca os pedidos com tal protocolo
    pedido = pedido.filter(codigoagente=agente)  # feitos a tal agente
    pedido = pedido.filter(codigousuario=usuario)  # por tal usuario
    pedido = pedido.filter(dataenvio=data)

    return pedido


def busca_status_pedido(status, target):
    return StatusPedido.objects.using(target).filter(nome__iexact=status)


def busca_status_interno(target):
    return StatusPedido.objects.using(target).get(pk=CONST_STATUS_INTERNO)


def busca_pedido_origem(target):
    return TipoPedidoOrigem.objects.using(target).get(pk=CONST_TIPO_ORIGEM)


def busca_pedido_situacao(situacao, target):
    return TipoPedidoSituacao.objects.using(target).filter(nome__iexact=situacao)


def busca_codigo_usuario(usuario, target):
    usuario = format_text_value(usuario)
    usuarios = Usuarios.objects.using(target).filter(nome__iexact=usuario)
    if usuarios is not None and len(usuarios) > 0:
        return usuarios[0]
    return None
