#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import random
from datetime import datetime
from constant import PORT, IP_SERVIDOR 
from django.db import connection

cli = socket.socket()
cli.connect((IP_SERVIDOR, PORT))
respuesta=''

cli.send('0001039452|000|0001039452|000|05|00|000021012629318|000102634809542|000000050000000|000000000000000|000000000000000|0000|00|000|00|0000|000|T501- ATM BCO CONTINENTAL SUC.          |000000000000000|000|20210126|161204|')
respuesta = cli.recv(1024)
#print "ENT", mensaje
print "OUT", respuesta

print "completado"
cli.close()
