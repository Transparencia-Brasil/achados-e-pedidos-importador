from importer.models import Agentes, TipoNivelFederativo, TipoPoder, Cidade, Uf
from datetime import datetime
from ..helper import add_placeholder


CONST_ATIVO = 1 # define o agente como ativo


def salvar_agente(agente_dict, target):
    poder = busca_poder(agente_dict['poder'], target)
    if poder is None:
        raise ValueError('Coluna Poder inválida!')
    nivel_feds = busca_nivel_fed(agente_dict['nivel_fed'], target)
    nivel_fed = None
    if nivel_feds is not None and len(nivel_feds) > 0:
        nivel_fed = nivel_feds[0]
    else:
        raise ValueError('Coluna Nivel Federativo inválida')
    uf = None
    cidade = None
    if agente_dict['uf']:
        uf = busca_uf(agente_dict['uf'], target)
    if agente_dict['cidade']:
        cidade = busca_cidade(agente_dict['cidade'], target)

    agente = Agentes(codigopoder=poder, codigonivelfederativo=nivel_fed, codigouf=uf, codigocidade=cidade,
                     nome=agente_dict['nome'], ativo=CONST_ATIVO, criacao=datetime.today(), alteracao=datetime.today())

    agente.save(using=target)
    
    pai = None
    if poder.nome.lower() == 'executivo' and nivel_fed.nome.lower() == 'federal':
        pai = busca_agentes("%Presidência da República%", nivel_fed.nome, target).first()
    elif poder.nome.lower() == 'executivo' and nivel_fed.nome.lower() == 'estadual':
        if uf.sigla == 'DF':
            pai = busca_agentes("%Governo d% Brasilia%" + uf.nome, nivel_fed.nome, target).first()
        else:
            pai = busca_agentes("%Governo d%" + uf.nome, nivel_fed.nome, target).first()
    elif poder.nome.lower() == 'executivo' and nivel_fed.nome.lower() == 'municipal':
        pai = busca_agentes("%Prefeitura d% " + cidade.nome, nivel_fed.nome, target).first()
    else:
        pai = agente

    if pai is not None and isinstance(pai, Agentes):
        agente.codigopai = pai.codigo
        agente.save(using=target, force_update=True, update_fields=['codigopai'])

def busca_agente_codigo(cod, target):
    return Agentes.objects.using(target).get(pk=cod)


def busca_agentes(nome_agente, nivel_fed, target):
    if nome_agente is None or nome_agente == '' or nivel_fed is None or nivel_fed == '':
        return None

    # Formata o nome do agente para evitar que alguns erros comuns (por exemplo falta de acentos) prejudiquem a busca
    nome_agente_formatado = add_placeholder(nome_agente)

    agentes = Agentes.objects.using(target).extra(where=['agentes.nome LIKE %s'], params=[nome_agente_formatado])
    agentes = agentes.filter(codigonivelfederativo__nome__iexact=nivel_fed)  # e por nivel federativo
    #print('AGENTEA {}'.format(agentes.query))

    return agentes


def busca_cidade(cidade, target):
    result = Cidade.objects.using(target).filter(nome__iexact=cidade)
    if result is not None and len(result) > 0:
        return result.first()

    return None


def busca_uf(uf, target):
    result = Uf.objects.using(target).filter(nome__iexact=uf)
    if not result.exists():
        result = Uf.objects.using(target).filter(sigla__iexact=uf)

    if result is not None and len(result) > 0:
        return result.first()
    return None


def busca_nivel_fed(nivel_fed, target):
    return TipoNivelFederativo.objects.using(target).filter(nome__iexact=nivel_fed)


def busca_poder(poder, target):
    result = TipoPoder.objects.using(target).filter(nome__iexact=poder)
    return result.first()
