


#Example
#constant.py
import sys, os
sys.path += ['/usr/local/django-apps']
sys.path += [os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]]
os.environ['DJANGO_SETTINGS_MODULE'] = 'gico01_01.settings'

IP_SERVIDOR = '192.168.3.202'
PORT = 9998
ALLOWED_IPS = ['127.0.0.1', '192.168.3.202', '192.168.3.254', '10.27.10.5']
ENTIDAD = 'COOP_MERCADO_N4'


