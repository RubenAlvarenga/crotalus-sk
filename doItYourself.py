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


def get_secuenciador_mensaje():
    secuenciador=''
    for n in range(0, 15):
        bit=random.sample('123456789', 1)
        secuenciador=secuenciador+str(bit[0])
    return secuenciador


while True:
    ctaDebito= raw_input("Cuenta Debito [1041088]:") or "1041088"



    Marca_de_Reversion = raw_input("Marca de reversion [99]:") or '00'
    if len(Marca_de_Reversion) > 2 or Marca_de_Reversion not in ['99', '00']:
        print "Solo 2 digitos 00 o 99"
        Marca_de_Reversion = raw_input("Marca de reversion [99]:")



    Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ") or "10"
    if len(Codigo_de_Transaccion) > 2:
        print "Solo 2 digitos"
        Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ")
    ctaDebito=str(ctaDebito).rjust(10, '0')

    #################
    ####   RRN   ####
    #################
    RRN = raw_input("RRN [Numero Unico de Transaccion] > ") or "0"

    if RRN == "0":
        query = (''' SELECT id FROM tctrxbepsa ORDER BY id DESC LIMIT 1  ''')
        cursor = connection.cursor()
        cursor.execute(query)
        RRN = cursor.fetchall()[0][0] + 50000000

    print "RRN: ", RRN 

    importe=raw_input("Importe >") or '00'
    importe=str(importe).rjust(15, '0')
    SecuenciadorRevers=''
    for n in range(0, 15):
        bit=random.sample('123456789', 1)
        SecuenciadorRevers=SecuenciadorRevers+str(bit[0])
    ahora = datetime.now()


    if Marca_de_Reversion == '99':
        RRN = raw_input("Numero unico de transaccion:")
        mensaje=ctaDebito\
        +'|'+'000'+'|'+'0000000000'+'|'+'000'\
        +'|'+str(Codigo_de_Transaccion)\
        +'|'+Marca_de_Reversion\
        +'|'+RRN.rjust(15, '0')\
        +'|'+get_secuenciador_mensaje()\
        +'|'+str(importe)\
        +'|'+'000000000000000'\
        +'|'+'000000000000000'\
        +'|'+'0000'\
        +'|'+'00'\
        +'|'+'000'\
        +'|'+'00'\
        +'|'+'0000'\
        +'|'+'000'\
        +'|'+'40-caracteres-para-el-nombre-de-comercio'\
        +'|'+RRN.rjust(15, '0')\
        +'|'+'000'\
        +'|'+str(ahora.day).rjust(2,'0')+str(ahora.month).rjust(2,'0')+str(ahora.year)\
        +'|'+str(ahora.hour).rjust(2,'0')+str(ahora.minute).rjust(2,'0')+str(ahora.second).rjust(2,'0')+"|"
    else:
        mensaje=ctaDebito\
        +'|'+'000'+'|'+'0000000000'+'|'+'000'\
        +'|'+str(Codigo_de_Transaccion)\
        +'|'+'00'\
        +'|'+str(RRN).rjust(15, '0')\
        +'|'+get_secuenciador_mensaje()\
        +'|'+str(importe)\
        +'|'+'000000000000000'\
        +'|'+'000000000000000'\
        +'|'+'0000'\
        +'|'+'00'\
        +'|'+'000'\
        +'|'+'00'\
        +'|'+'0000'\
        +'|'+'000'\
        +'|'+'40-caracteres-para-el-nombre-de-comercio'\
        +'|'+SecuenciadorRevers\
        +'|'+'000'\
        +'|'+str(ahora.day).rjust(2,'0')+str(ahora.month).rjust(2,'0')+str(ahora.year)\
        +'|'+str(ahora.hour).rjust(2,'0')+str(ahora.minute).rjust(2,'0')+str(ahora.second).rjust(2,'0')+"|"

    cli.send(mensaje)
    respuesta = cli.recv(1024)
    print "ENT", mensaje
    print "OUT", respuesta
    if respuesta == "quit":
        break
    break

print "completado"
cli.close()
