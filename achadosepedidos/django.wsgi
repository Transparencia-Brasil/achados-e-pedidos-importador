import os
import sys

path='/var/www/stage.achadosepedidos.org.br/achadosepedidos'

if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'achadosepedidos.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
