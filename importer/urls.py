from django.urls import path, include
from django.http import HttpResponseRedirect
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', lambda r: HttpResponseRedirect('index')),
    path('index', views.index, name='index'),
    path('resultado', views.resultado, name='resultado'),
    path('inserir-agentes', views.inserir_agentes, name='inserir_agentes'),
    path('pendencias', views.pendencias, name='pendencias'),
    path('loading', views.loading, name='loading'),
    path('historico', views.historico, name='historico'),
]

handler404 = views.handler404
handler500 = views.handler500
