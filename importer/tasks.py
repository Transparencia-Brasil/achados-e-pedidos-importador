from __future__ import absolute_import, unicode_literals
from celery import app, shared_task, current_task, task
from django.db import IntegrityError
from .dao import pedidosDAO, agentesDAO, interacoesDAO
from .helper import upload_file, get_file, format_text_value, write_file, save_file, remove_file
from datetime import datetime
from os import listdir, path
import csv
import time
import traceback
import dotenv


# Processa a planilha em background
@task(ignore_result=False, bind=True)
def processaPlanilha(self, filename, target):
    mensagem = None
    pedidos = 0  # numero de pedidos processados
    row_interacoes = []  # lista de interacoes ainda não processadas
    interacoes = 0  # numero de interacoes processadas
    pendencias = []  # lista de pendencias
    anexos = 0  # numero de anexos
    novos_agentes = []  # lista de orgãos não encontrados no banco (serão adicionados perante confirmação)
    csv_pendencias = ''  # define o nome do csv pendencias
    lines_num = 0  # numero de linhas do arquivo
    file = None

    reader = None
    header = None
    try:
        file = get_file(filename)
        lines_num = len(file.readlines())

        nome_usuario = ''
        # pega o nome do usuario a partir do nome do arquivo
        if '-' in filename:
            nome_usuario = filename.split('-')[0]
        else:
            nome_usuario = filename[:-4]
        usuario = pedidosDAO.busca_codigo_usuario(nome_usuario.strip(), target)

        # se o usuario não for encontrado, então não o processo não vai funcionar
        if usuario is None:
            mensagem = 'Usuário não encontrado, por favor verifique o nome do arquivo.'
            time.sleep(1)
            return {'mensagem': mensagem}

        file.seek(0)
        reader = csv.reader(file, delimiter=';', escapechar='\\')
        header = next(reader)  # salva o cabeçalho da planilha
        header[0] = 'Erro'  # substitui o cabeçalho id por Erro, pois é onde ele indica os erros na planilha de pendencias
        if len(header) < 15:
            mensagem = 'Só foram encontradas {} colunas, por favor verifique o arquivo!'.format(len(header))
            time.sleep(1)
            return {'mensagem': mensagem}            
    except UnicodeDecodeError:
        mensagem = 'Erro de enconding, verifique se o csv está codificado em UTF-8'
        time.sleep(1)
        return {'mensagem': mensagem}

    pendencias.append(header)
    for row in reader:
        tipo_interacao = format_text_value(row[4])
        # Verifica se é pedido ou interação, pois as interações são processadas posteriormente
        if 'resposta' not in tipo_interacao and 'recurso' not in tipo_interacao\
                and 'reclamacao' not in tipo_interacao:
            try:
                agente = agentesDAO.busca_agentes(row[7], row[13], target)
                if agente is not None and len(agente) > 0:
                    # insere o pedido na base e guarda o pedido inserido na lista
                    pedidosDAO.inserir_pedido(row, usuario, agente[0], target)
                    pedidos += 1
                    # calcula a porcentagem de linhas processadas, é usado para a barra de prograsso
                    process_percent = (pedidos*1/lines_num*1) * 100
                    current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})
                else:
                    if e_novo_agente(novos_agentes, row[7]):
                        novos_agentes.append(novo_agente_dict(row))
                    row[0] = 'Agente não encontrado.'
                    pendencias.append(row)
            except TypeError as tErr:
                traceback.print_exc(limit=2)
                row[0] = 'Erro desconhecido encontrado: ' + str(tErr)
                pendencias.append(row)
            except IndexError as iErr:
                traceback.print_exc(limit=2)
                row[0] = 'Erro desconhecido encontrado: ' + str(iErr)
                pendencias.append(row)
            except ValueError as vErr:
                traceback.print_exc(limit=2)
                row[0] = str(vErr)
                pendencias.append(row)
            except UnicodeDecodeError:
                traceback.print_exc(limit=2)
                row[0] = 'Erro na codificação do arquivo, caracteres invalidos encontrados!'
                pendencias.append(row)
        else:
            row_interacoes.append(row)  # as linhas q forem row_interacoes serao trabalhadas posteriormente

    # comeca a trabalhar com as interacoes
    for row_interacao in row_interacoes:
        try:
            agente = agentesDAO.busca_agentes(row_interacao[7], row_interacao[13], target)
            if agente is not None and len(agente) > 0:
                # Busca um pedido existente, a busca por pedido é por protocolo, agente e usuário
                pedido_interacao = pedidosDAO.busca_pedido(row_interacao[1], agente[0], usuario, target)
                interacao = interacoesDAO.inserir_interacao(row_interacao, pedido_interacao, row_interacao[4], target)
                interacoes += 1

                # Processamento de Anexos
                # Em cada interação o sistema busca se contêm anexo
                if row_interacao[14] is not None and row_interacao[14] != '':
                    tipo_interacao = interacao.codigotipopedidoresposta
                    nome_pasta = row_interacao[14]
                    if nome_pasta and nome_pasta != '':
                        nome_pasta = nome_pasta.strip()
                    caminho =  dotenv.get_key('.env', 'DIR_ASSETS') + nome_pasta

                    # Logica de anexos para qualquer planilha que não seja da CGU
                    if path.isdir(caminho) and nome_pasta and nome_pasta.lower() != 'cgu':
                        nome_anexo = row_interacao[15] if len(row_interacao) > 15 else ''
                        if nome_anexo != '':
                            # Caso haja mais de um anexo na planilha eles sao separados por | (pipe)
                            if '|' in nome_anexo:
                                nomes_anexos = nome_anexo.split('|')
                                for n_a in nomes_anexos:
                                    nome_completo = nome_pasta + '/'  + n_a.strip()
                                    interacoesDAO.inserir_anexo(interacao, caminho, nome_completo, target)
                                    anexos += 1
                            # Caso só haja um anexo
                            else:
                                nome_completo = nome_pasta + '/'  + nome_anexo
                                interacoesDAO.inserir_anexo(interacao, caminho, nome_completo, target)
                                anexos += 1
                        # Caso o nome do anexo não tenha sido especificado, ele adiciona todos os arquivos da pasta
                        else:
                            for nome_arquivo in listdir(caminho):
                                nome_completo = nome_pasta + '/'  + nome_arquivo
                                interacoesDAO.inserir_anexo(interacao, caminho, nome_completo, target)
                                anexos += 1
                    # Caso específico da CGU, procurar pasta CGU > pasta protocolo > arquivo com o tipo da interacao no nome
                    elif path.isdir(caminho) and nome_pasta and nome_pasta.lower() == 'cgu':
                        # prot = verificaProtocolo(row_interacao[1], caminho) - Problemas de otimização
                        if caminho.endswith('/'):
                            caminho = caminho + row_interacao[1] + '/'
                        else:
                            caminho = caminho + '/' + row_interacao[1] + '/'
                        for nome_arquivo in listdir(caminho):
                            if mapear_tipo_interacao(row_interacao[4], nome_arquivo):
                                nome_completo = nome_pasta + '/' + row_interacao[1] + '/' + nome_arquivo
                                anexo = interacoesDAO.inserir_anexo(interacao, caminho, nome_completo, target)
                                anexos += 1

                # calcula a porcentagem de linhas processadas, é usado para a barra de prograsso
                process_percent = ((pedidos+interacoes)*1/lines_num*1) * 100
                current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})
            else:
                if e_novo_agente(novos_agentes, row_interacao[7]):
                    novos_agentes.append(novo_agente_dict(row_interacao))
                row_interacao[0] = 'Agente não encontrado.'
                pendencias.append(row_interacao)
        except ValueError as vErr:
            traceback.print_exc(limit=2)
            row_interacao[0] = str(vErr)
            pendencias.append(row_interacao)
        except IndexError as iErr:
            traceback.print_exc(limit=2)
            row_interacao[0] = 'Erro desconhecido encontrado: ' + str(iErr)
            pendencias.append(row_interacao)
        except TypeError as tErr:
            traceback.print_exc(limit=2)
            row_interacao[0] = 'Erro desconhecido encontrado: ' + str(tErr)
            pendencias.append(row_interacao)
        except IntegrityError:
            traceback.print_exc(limit=2)
        except UnicodeDecodeError:
            traceback.print_exc(limit=2)
            row[0] = 'Erro na codificação do arquivo, caracteres invalidos encontrados!'
            pendencias.append(row)
        except FileNotFoundError:
            traceback.print_exc(limit=2)
            row[0] = 'Interação processada sem anexo, arquivo não encontrado'
            pendencias.append(row)

    if len(pendencias) > 1:  # se houver pendencias, entao salva o csv na sessão para poder ser baixado posteriormente
        csv_pendencias = nome_usuario + ' - pendencias_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'

    processo = {'mensagem': mensagem, 'pedidos': pedidos, 'interacoes': interacoes, 'anexos': anexos, 
                'novos_agentes': novos_agentes, 'pendencias': pendencias, 'csv_pendencias': csv_pendencias}

    if file:
        file.close()

    time.sleep(1)
    return processo


# Cria um dicionario usando os dados de Agente, isso sera usado na insercao do agente posteriormente
def novo_agente_dict(colunas):
    agente_dict = {'nome': colunas[7], 'poder': colunas[12], 'nivel_fed': colunas[13], 'uf': colunas[10],
                   'cidade': colunas[11]}
    return agente_dict


# Verifica se deve adicionar o agente na lista de novos agentes
def e_novo_agente(agentes, nome):
    if len(agentes) <= 0:
        return True
    for agente in agentes:
        if nome == agente['nome']:
            return False
    return True


# Usado para reconhecer qual tipo de interação cada anexo esta relacionado (Somente caso 'CGU')
def mapear_tipo_interacao(tipo, arquivo):
    tipos = arquivo.split('_')
    if tipo == 'Resposta do Pedido' and len(tipos) > 0 and (format_text_value(tipos[0]) == 'pedido' or \
       (format_text_value(tipos[0]) == 'resposta' and format_text_value(tipos[1]) == 'pedido')):
        return True
    elif tipo == 'Reclamação' and len(tipos) > 0 and format_text_value(tipos[0]) == 'reclamacao':
        return True
    elif tipo == 'Resposta da Reclamação' and len(tipos) > 1 and format_text_value(tipos[0]) == 'resposta' and \
         format_text_value(tipos[1]) == 'reclamacao':
        return True
    elif tipo == 'Recurso - 1º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'recurso' and \
         format_text_value(tipos[1]) == '1':
        return True
    elif tipo == 'Recurso - 2º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'recurso' and \
         format_text_value(tipos[1]) == '2':
        return True
    elif tipo == 'Recurso - 3º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'recurso' and \
         format_text_value(tipos[1]) == '3':
        return True
    elif tipo == 'Resposta do recurso - 1º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'resposta' and \
         format_text_value(tipos[1]) == 'recurso' and format_text_value(tipos[2]) == '1':
        return True
    elif tipo == 'Resposta do recurso - 2º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'resposta' and \
         format_text_value(tipos[1]) == 'recurso' and format_text_value(tipos[2]) == '2':
        return True
    elif tipo == 'Resposta do recurso - 3º Instância' and len(tipos) > 1 and format_text_value(tipos[0]) == 'resposta' and \
         format_text_value(tipos[1]) == 'recurso' and format_text_value(tipos[2]) == '3':
        return True
    elif tipo == 'Recurso - 4º Judicial' and len(tipos) > 1 and format_text_value(tipos[0]) == 'recurso' and \
         format_text_value(tipos[1]) == '4':
        return True
    elif tipo == 'Resposta do recurso - 4º Judicial' and len(tipos) > 1 and format_text_value(tipos[0]) == 'resposta' and \
         format_text_value(tipos[1]) == 'recurso' and format_text_value(tipos[2]) == '4':
        return True

    return False


# TODO Aumentou muito o tempo de processamento, é preciso otimizar
# Verifica se é preciso adicionar 0 na frente do protocolo para "bater" com as pastas dos anexos
def verificaProtocolo(protocolo, caminho):
    novo_prot = protocolo
    if protocolo != '' and not protocolo.startswith('0'):  # só adiciona 0 se o protocolo original não tiver 0s na frente
        for folder in listdir(caminho):  # olha cada pasta dentro de CGU
            if folder.startswith('0'):  # se a pasta tiver 0 na frente, analisa
                folder_len = len(folder)
                prot_len = len(novo_prot)
                while folder_len < prot_len:  # se o protocolo for maior que a pasta, então não é essa pasta
                    if folder == novo_prot:  # achou a pasta, devolve o protocolo "correto"
                        return novo_prot
                    else:  # não tem certeza ainda, adiciona o 0 no protocolo, atualiza o tamanho e testa novamente
                        novo_prot = '0' + novo_prot
                        prot_len = len(novo_prot)
    return protocolo
