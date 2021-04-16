from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .forms import UploadFileForm
from .helper import upload_file, remove_file
from .dao import agentesDAO, historicoDAO
from .tasks import processaPlanilha
import csv
import traceback


# Tela inicial do sistema (se logado)
@login_required
def index(request):
    if request.method == 'POST':
        filename = ''
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():  # verifica se um arquivo (planilha) foi detectado
            target = request.POST.get('target', 'stage')
            planilha = request.FILES['pedidos']
            filename = planilha.name
            # request.session['filename'] = filename
            try:
                request.session['filename'] = upload_file(planilha, planilha.name)
            except UnicodeDecodeError:  # erro de codificação
                mensagem = 'Erro de enconding, verifique se o csv está codificado em UTF-8'
                return render(request, 'importer/index.html', {'mensagem': mensagem})
            if target not in ['stage', 'production']:  # não foi detectado se a importação será p/ stage ou produção
                mensagem = 'Seleção de destino da importação não encontrada, por favor selecione Stage ou Produção'
                return render(request, 'importer/index.html', {'mensagem': mensagem})
            else:  # salva o 'target' na sessão, pois será usado em outras telas
                request.session['target'] = target

            job = processaPlanilha.delay(filename, target)  # inicia o processamento da planilha em outra thread
            contexto = {'job_id':job.id}  # passa o id da thread p/ a tela da barra de progresso
            return render(request, 'importer/loading_bar.html', contexto)
    else:
        form = UploadFileForm()
        return render(request, 'importer/index.html', {'form': form})


@login_required
def loading(request):  # não está ligado a uma tela, mas ao javascript q controla a barra de progresso (ver loading_bar.html nos templates)
    data = 'fail'
    if 'job_id' in request.POST.keys() and request.POST['job_id']:
        job_id = request.POST.get('job_id','')  # pega o id da thread
        job = AsyncResult(job_id)  # pega informações da thread a partir do id
        data = job.result or job.state
        if job.state == 'SUCCESS':  # se o processo finalizou corretamente salva o resultado na sessão p/ ser mostrado na outra tela
            request.session['resultado'] = job.result
        if job.failed():
            request.session['erro'] = job.traceback
    return JsonResponse({'data':data})  # passa os status da thread para o javascript


@login_required
def resultado(request):  # tela de resultado
    contexto = {}
    pendencias = 0
    novos_agentes = {}

    try:
        resultado = request.session.pop('resultado', {})  # pega o resultado salvo na sessão
        erro = request.session.pop('erro', '')
        filename = request.session.pop('filename', '')
        target = request.session.get('target', 'stage')

        if resultado and len(resultado) > 0:  # encontrou um resultado
            if 'pendencias' in resultado and  len(resultado['pendencias']) > 1:  # salva pendencias na sessão, caso haja alguma
                request.session['csv_pendencias_file'] = {'csv_pendencias': resultado['pendencias'], 'csv_nome': resultado['csv_pendencias']}
                pendencias = len(resultado['pendencias'])-1

            if 'novos_agentes' in resultado and len(resultado['novos_agentes']) > 0:  # salva os novos agentes na sessão, caso haja algum
                request.session['novos_agentes'] = {'novos_agentes': resultado['novos_agentes']}
                novos_agentes = resultado['novos_agentes']

            if len(resultado) == 1 and 'mensagem' in resultado:  # caso haja erro conhecido no processamento, ele devolve somente a msg de erro
                contexto = {'mensagem': resultado['mensagem']}
            else:  # tudo correu bem, mostra os resultados, as pendencias, caso haja alguma, e os novos agentes, caso haja algum
                usuario_logado = request.user.username  # pega o 'login' do usuario logado
                historicoDAO.salvar_importacao(filename, resultado['pedidos'], resultado['interacoes'], resultado['anexos'], target, usuario_logado)  # salva a importacao no historico
                contexto = {'num_pendencias': pendencias, 'num_pedidos': resultado['pedidos'], 'mensagem': resultado['mensagem'],
                    'num_interacoes': resultado['interacoes'], 'anexos': resultado['anexos'], 'agentes': novos_agentes}
                print('ENTROU NO RESULTADO CORRETO: {}'.format(len(contexto)))
        elif erro and erro != '':
            contexto = {'mensagem':'Erro desconhecido\n{}'. format(erro)}
        else:
            contexto = {'mensagem':'Erro na leitura do resultado, por favor tente novamente.'}
            print('DEU ERRO: {}'.format(len(contexto)))

        if filename and filename != '':
            remove_file(filename)  # depois de tudo processado, remove a planilha do disco para não ocupar espaço
    except FileNotFoundError:
        traceback.print_exc(limit=2)
    except KeyError:
        traceback.print_exc(limit=2)
        contexto = {'mensagem':'Resultado não encontrado, por favor tente novamente!'}

    return render(request, 'importer/resultado.html', contexto)


@login_required
def inserir_agentes(request):  # tela que mostra o nº de agentes inseridos
    num_agentes = 0

    if request.method == 'POST':
        agentes = request.session.pop('novos_agentes', None)  # pega os novos agentes da sessão
        target = request.session.get('target', 'stage')  # pega o target da sessão

        if agentes is not None:
            for agente in agentes['novos_agentes']:
                #if isinstance(agente, agentesDAO.Agentes) and agente is not None:
                agentesDAO.salvar_agente(agente, target)
                num_agentes += 1

    url = '/importer/'
    return render(request, 'importer/inserir-agentes.html', {'agentes': num_agentes, 'url': url})


@login_required
def pendencias(request):  # vinculado ao link para baixar pendencias, monta a planilha e habilita o download
    csv_pendencias_dict = request.session.get('csv_pendencias_file', None)  # pega as pendencias da sessao
    csv_pendencias = csv_pendencias_dict['csv_pendencias']
    csv_name = csv_pendencias_dict['csv_nome']
    if csv_pendencias is not None:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(csv_name)
        writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        for pend in csv_pendencias:  # monta o csv em memoria (ou num arquivo temporario se muito grande)
            writer.writerow(pend)
        return response  # envia o csv p/ download

    return render(request, '404.html', status=404)


@login_required
def historico(request):
    importacoes = historicoDAO.busca_historico()
    return render(request, 'importer/historico.html', {'importacoes':importacoes})


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)

