from django.db import models


# Create your models here.
class TipoUsuario(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_usuario'


class Usuarios(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigotipousuario = models.ForeignKey(TipoUsuario, on_delete=models.DO_NOTHING, db_column='CodigoTipoUsuario')  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=150)  # Field name made lowercase.
    slug = models.CharField(db_column='Slug', max_length=100)  # Field name made lowercase.
    senha = models.CharField(db_column='Senha', max_length=200)  # Field name made lowercase.
    bloqueado = models.SmallIntegerField(db_column='Bloqueado', blank=True, null=True)  # Field name made lowercase.
    chaverecuperacaosenha = models.CharField(db_column='ChaveRecuperacaoSenha', max_length=500, blank=True, null=True)  # Field name made lowercase.
    datageracaosenha = models.DateTimeField(db_column='DataGeracaoSenha', blank=True, null=True)  # Field name made lowercase.
    ativo = models.SmallIntegerField(db_column='Ativo', blank=True, null=True)  # Field name made lowercase.
    aceitecomunicacao = models.SmallIntegerField(db_column='AceiteComunicacao', blank=True, null=True)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'usuarios'


class Pais(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pais'


class Uf(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigopais = models.ForeignKey(Pais, on_delete=models.DO_NOTHING, db_column='CodigoPais')  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=200)  # Field name made lowercase.
    sigla = models.CharField(db_column='Sigla', max_length=2)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'uf'


class Cidade(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigouf = models.ForeignKey('Uf', on_delete=models.DO_NOTHING, db_column='CodigoUF')  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=200)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cidade'


class TipoPoder(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_poder'


class TipoNivelFederativo(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_nivel_federativo'


class Agentes(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigopoder = models.ForeignKey('TipoPoder', on_delete=models.DO_NOTHING, db_column='CodigoPoder')  # Field name made lowercase.
    codigonivelfederativo = models.ForeignKey('TipoNivelFederativo', on_delete=models.DO_NOTHING, db_column='CodigoNivelFederativo')  # Field name made lowercase.
    codigouf = models.ForeignKey('Uf', on_delete=models.DO_NOTHING, db_column='CodigoUF', blank=True, null=True)  # Field name made lowercase.
    codigopai = models.IntegerField(db_column='CodigoPai', blank=True, null=True)  # Field name made lowercase.
    codigocidade = models.ForeignKey('Cidade', on_delete=models.DO_NOTHING, db_column='CodigoCidade', blank=True, null=True)  # Field name made lowercase.
    criadoexternamente = models.IntegerField(db_column='CriadoExternamente', blank=True, null=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    slug = models.CharField(db_column='Slug', max_length=1500, blank=True, null=True)  # Field name made lowercase.
    descricao = models.CharField(db_column='Descricao', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    link = models.CharField(db_column='Link', max_length=300, blank=True, null=True)  # Field name made lowercase.
    ativo = models.IntegerField(db_column='Ativo', blank=True, null=True)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'agentes'


class StatusPedido(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'status_pedido'


class TipoPedidoOrigem(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_pedido_origem'


class TipoPedidoSituacao(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_pedido_situacao'


class Pedidos(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigousuario = models.ForeignKey('Usuarios', on_delete=models.DO_NOTHING, db_column='CodigoUsuario')  # Field name made lowercase.
    codigoagente = models.ForeignKey(Agentes, on_delete=models.DO_NOTHING, db_column='CodigoAgente')  # Field name made lowercase.
    codigotipoorigem = models.ForeignKey('TipoPedidoOrigem', on_delete=models.DO_NOTHING, db_column='CodigoTipoOrigem')  # Field name made lowercase.
    codigotipopedidosituacao = models.ForeignKey('TipoPedidoSituacao', on_delete=models.DO_NOTHING, db_column='CodigoTipoPedidoSituacao')  # Field name made lowercase.
    codigostatuspedido = models.ForeignKey('StatusPedido', on_delete=models.DO_NOTHING, related_name='status', db_column='CodigoStatusPedido')  # Field name made lowercase.
    codigostatuspedidointerno = models.ForeignKey('StatusPedido', on_delete=models.DO_NOTHING, related_name='statusInterno', db_column='CodigoStatusPedidoInterno')  # Field name made lowercase.
    identificadorexterno = models.CharField(db_column='IdentificadorExterno', max_length=150, blank=True, null=True)  # Field name made lowercase.
    protocolo = models.CharField(db_column='Protocolo', max_length=200, blank=True, null=True)  # Field name made lowercase.
    titulo = models.CharField(db_column='Titulo', max_length=250, blank=True, null=True)  # Field name made lowercase.
    slug = models.CharField(db_column='Slug', max_length=300, blank=True, null=True)  # Field name made lowercase.
    descricao = models.TextField(db_column='Descricao', blank=True, null=True)  # Field name made lowercase.
    dataenvio = models.DateTimeField(db_column='DataEnvio', blank=True, null=True)  # Field name made lowercase.
    foiprorrogado = models.IntegerField(db_column='FoiProrrogado', blank=True, null=True)  # Field name made lowercase.
    anonimo = models.IntegerField(db_column='Anonimo', blank=True, null=True)  # Field name made lowercase.
    ativo = models.IntegerField(db_column='Ativo', blank=True, null=True)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidos'
        unique_together = (('codigoagente', 'protocolo', 'titulo', 'slug'),)


class TipoPedidoResposta(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    nome = models.CharField(db_column='Nome', max_length=150)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tipo_pedido_resposta'


class PedidosInteracoes(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigopedido = models.ForeignKey(Pedidos, on_delete=models.DO_NOTHING, db_column='CodigoPedido')  # Field name made lowercase.
    codigotipopedidoresposta = models.ForeignKey('TipoPedidoResposta', on_delete=models.DO_NOTHING, db_column='CodigoTipoPedidoResposta')  # Field name made lowercase.
    dataresposta = models.DateTimeField(db_column='DataResposta', blank=True, null=True)  # Field name made lowercase.
    descricao = models.TextField(db_column='Descricao', blank=True, null=True)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidos_interacoes'
        unique_together = (('codigopedido', 'codigotipopedidoresposta', 'dataresposta'),)


class PedidosAnexos(models.Model):
    codigo = models.AutoField(db_column='Codigo', primary_key=True)  # Field name made lowercase.
    codigopedidointeracao = models.ForeignKey('PedidosInteracoes', on_delete=models.DO_NOTHING, db_column='CodigoPedidoInteracao')  # Field name made lowercase.
    arquivofullpath = models.CharField(db_column='ArquivoFullPath', max_length=255)  # Field name made lowercase.
    ativo = models.IntegerField(db_column='Ativo', blank=True, null=True)  # Field name made lowercase.
    criacao = models.DateTimeField(db_column='Criacao')  # Field name made lowercase.
    alteracao = models.DateTimeField(db_column='Alteracao', blank=True, null=True)  # Field name made lowercase.
    codigostatusexportacaoes = models.CharField(db_column='CodigoStatusExportacaoES', max_length=9)  # Field name made lowercase.
    arquivo = models.CharField(db_column='Arquivo', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedidos_anexos'
        unique_together = (('codigopedidointeracao', 'arquivo'),)


class HistoricoImportacao(models.Model):
    codigo =  models.AutoField(db_column='Codigo', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=255, null=False)
    usuario_tb = models.CharField(db_column='usuario_tb', max_length=255)
    pedidos = models.IntegerField(db_column='Linhas', null=False)
    interacoes = models.IntegerField(db_column='interacao', null=False)
    anexos = models.IntegerField(db_column='anexos', null=False)
    target = models.CharField(db_column='target', max_length=80)
    criacao = models.DateTimeField(db_column='Criacao')

    class Meta:
        managed = False
        db_table = 'Historico_Importacao'


