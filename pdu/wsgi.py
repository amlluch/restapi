
""" WSGI config for pdu project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys

sys.path.append('/home/alfonso/pdu/pdu/pdu')
sys.path.append('/home/alfonso/pdu/pduenv/lib/python2.7/site-packages')
#os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('/home/alfonso/pdu/pdu')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdu.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
