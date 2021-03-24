# -*- coding: utf-8 -*-
import socket
import random
from datetime import datetime
from constant import PORT, IP_SERVIDOR 

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
    Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ") or "10"
    if len(Codigo_de_Transaccion) > 2:
        print "Solo 2 digitos"
        Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ")
    ctaDebito=str(ctaDebito).rjust(10, '0')

    id_fantasma = random.randint(5405, 25000)


    importe=raw_input("Importe >") or '00'
    importe=str(importe).rjust(15, '0')
    SecuenciadorRevers=''
    for n in range(0, 15):
        bit=random.sample('123456789', 1)
        SecuenciadorRevers=SecuenciadorRevers+str(bit[0])
    ahora = datetime.now()

    mensaje=ctaDebito+'0000000000000000'+str(Codigo_de_Transaccion)+'00'+get_secuenciador_mensaje()+str(id_fantasma).rjust(15, '0')+str(importe)+'000000000000000'+'000000000000000'+'0000'+'00'+'000'+'00'+'0000'+'000'+'40-caracteres-para-el-nombre-de-comercio'+SecuenciadorRevers+'000'+str(ahora.day).rjust(2,'0')+str(ahora.month).rjust(2,'0')+str(ahora.year)+str(ahora.hour).rjust(2,'0')+str(ahora.minute).rjust(2,'0')+str(ahora.second).rjust(2,'0')

    #mensaje_manual ='000101429540000000000000001000000000000000011000000000057239000000000000000000000000000000000000000000000000000001000000D21Procard S.A.                         PRC00000000000000000021092016151637'
    cli.send(mensaje)
    respuesta = cli.recv(1024)
    print "ENT", mensaje
    print "OUT", respuesta
    if respuesta == "quit":
        break
    break

print "completado"
cli.close()

