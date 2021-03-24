# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import time
from threading import Timer
import thread
from Tren import Solicitud, Respuesta, Transaccion, get_data_log
import json

from functions import get_cantidad_veces


from constant import os, PATH, BIN, RECARGO_ATM,\
                         FREE_CONSULTA_MES, RECARGO_CONSULTA_PROCARD, RECARGO_CONSULTA_DINELCO, \
                         FREE_EXTRACCION_MES, RECARGO_EXTRACCION_PROCARD, RECARGO_EXTRACCION_DINELCO, COUCHDB_SERVER, \
                         TIPO_DOCUMENTO, CONCEPTO_DEBITO

from codigos import CODIGOS_RESPUESTAS, CODIGOS_SOLICITUDES

#from models import Respuesta, TransaccionTD
from core.credito.models import prmapres # tctrxbepsa, tctarjeta, tccodopr, ahahorro, ahmovimi, ahtipo, ahsubtip, ahconcep
from core.tarjeta.models import tctrxbepsa, tccodopr
from core.ahorro.models import ahahorro, ahmovimi, ahconcep
#from models import Transaccion
from django.db import transaction
from datetime import datetime, date
import logging
logger = logging.getLogger("testlog.procesar")





@transaction.atomic
def negociar(trenRecibido):
    mensaje = None
    try:
        logger.debug("TREN :"+trenRecibido) #!IMPORTANTE
        request = Solicitud(trenRecibido)

        response = Respuesta()
        response.set_DOCUM(request.numero_boleta)
        response.set_LOCAL(request.numero_transaccion_banco)

        if request.codigo not in CODIGOS_SOLICITUDES.keys():
            response.set_CODRTN(CODIGOS_RESPUESTAS.keys()[CODIGOS_RESPUESTAS.values().index('TRANSACCION INVALIDA')])
        else:
            try:
                tarjeta = request.get_tarjeta
            except Exception, e:
                response.set_CODRTN(CODIGOS_RESPUESTAS.keys()[CODIGOS_RESPUESTAS.values().index('TARJETA / CUENTA BLOQUEADA POR LA ENTIDAD')])
                mensaje = unicode(e)
                tarjeta = None

            if type(tarjeta).__name__  == 'tctarjeta':
                if tarjeta.get_card_status != True:
                    response.set_CODRTN(CODIGOS_RESPUESTAS.keys()[CODIGOS_RESPUESTAS.values().index('TARJETA / CUENTA BLOQUEADA POR LA ENTIDAD')])
                    mensaje = unicode("CUENTA o SOCIO INACTIVO")
                    tarjeta = None

                else:
                    try:
                        cuenta_debito = request.get_cuenta_debito
                    except Exception, e:
                        response.set_CODRTN(CODIGOS_RESPUESTAS.keys()[CODIGOS_RESPUESTAS.values().index('NO APROBADA - NO EXISTE CUENTA DE AHORRO')])
                        mensaje = unicode(e)
                        cuenta_debito = None
                    else:
                        tran=Transaccion()
                        tran.TCT1_TCTAID  = tarjeta
                        tran.TCT1_TCOSID  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='OPE', TCOS_CODIGO=int(request.codigo))

                        tran.TCT1_CODREF  = request.numero_transaccion_banco
                        tran.TCT1_IMPORTE = request.get_importe
                        tran.TCT1_TREINP  = trenRecibido
                        tran.TCT1_CODOPR  = request.codigo
                        tran.TCT1_NOW     = datetime.now()
                        duplicado = tctrxbepsa.objects.filter(TCT1_CODREF=tran.TCT1_CODREF, TCT1_TCTAID=tran.TCT1_TCTAID, TCT1_ESTADO='ACE')
                        if duplicado:
                            response.set_SACTU(cuenta_debito.AHAH_SALDO)
                            response.set_SALDOS(cuenta_debito.get_saldo_disponible)
                            response.set_CODRTN('12') # INVALIDA
                            tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=12)
                            tran.TCT1_TREOUP  = response.armar_tren
                            tran.TCT1_ESTADO  = 'REC'
                            tran.save()
                            mensaje = unicode("Solicitud duplicada")
                            raise ValueError(mensaje)

                        #####################
                        ####   REVERSA   ####
                        #####################
                        if request.extorno == '99':
                            try:
                                reversar = Transaccion.objects.get(TCT1_CODREF=int(request.reversar_transaccion), \
                                                                    TCT1_TCTAID__TCTA_TIPO__TCTI_TIPO='TD1', \
                                                                    TCT1_ESTADO='ACE', TCT1_TCTAID=BIN+request.cuenta_debito)
                            except Exception, e:
                                response.set_SACTU(cuenta_debito.AHAH_SALDO)
                                response.set_SALDOS(cuenta_debito.get_saldo_disponible)
                                response.set_CODRTN('12') # INVALIDA
                                tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=12)
                                tran.TCT1_TREOUP  = response.armar_tren
                                tran.TCT1_ESTADO  = 'REC'
                                tran.save()
                                mensaje = unicode(e)
                            else:
                                tran.save()
                                try:
                                    reversado = reversar.reversar(tran)
                                except:
                                    response.set_SACTU(cuenta_debito.AHAH_SALDO)
                                    response.set_SALDOS(cuenta_debito.get_saldo_disponible)
                                    response.set_CODRTN('12') #TRANSACCION INVALIDA
                                    tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=12)
                                    tran.TCT1_TREOUP  = response.armar_tren
                                    tran.TCT1_ESTADO  = 'REC'
                                    tran.save()


                                if reversado:
                                    reversar.TCT1_ESTADO = 'REV'
                                    reversar.TCT1_TCT1ID = tran.id
                                    reversar.save()

                                    response.set_SACTU(cuenta_debito.AHAH_SALDO)
                                    response.set_SALDOS(cuenta_debito.get_saldo_disponible)
                                    response.set_CODRTN('00') # INVALIDA
                                    tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=00)
                                    tran.TCT1_TREOUP  = response.armar_tren
                                    tran.TCT1_ESTADO  = 'RAC'
                                    tran.save()
                        else:
                            #####################
                            ##   RECARGO ATM   ##
                            #####################
                            recargo = 0
                            if RECARGO_ATM:
                                cantidad_mes = get_cantidad_veces(tarjeta.TCTA_NUCTA, int(request.codigo))
                                if request.codigo == '05':
                                    if cantidad_mes >= FREE_EXTRACCION_MES:
                                        recargo = RECARGO_EXTRACCION_DINELCO
                                elif request.codigo in ['10','02']:
                                    if cantidad_mes >= FREE_CONSULTA_MES:
                                        recargo = RECARGO_CONSULTA_DINELCO

                            ############################
                            ###  CONSULTA DE SALDOS  ###
                            ############################
                            if request.codigo in [  CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('CONSULTA SALDO (POS)')],\
                                                    CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('CONSULTA SALDO (ATM)')] ]:

                                saldo = cuenta_debito.AHAH_SALDO
                                saldo_disponible = cuenta_debito.get_saldo_disponible
                                if recargo:
                                    if saldo_disponible < recargo:
                                        response.set_SACTU(saldo)
                                        response.set_SALDOS(saldo_disponible)
                                        response.set_CODRTN('51') #SALDO INSUFICIENTE
                                        tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=51)
                                        tran.TCT1_TREOUP  = response.armar_tren
                                        tran.TCT1_ESTADO  = 'REC'
                                        tran.save()
                                    else:
                                        tran.save()
                                        try:
                                            tran.aplicar_recargo(recargo)
                                        except Exception, e:
                                            response.set_CODRTN('06') # INVALIDA
                                            tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=06)
                                            tran.TCT1_TREOUP  = response.armar_tren
                                            tran.TCT1_ESTADO  = 'REC'
                                            tran.save()
                                            mensaje = unicode(e)

                                        else:
                                            response.set_SACTU(saldo)
                                            response.set_SALDOS(saldo_disponible)
                                            response.set_CODRTN('00') #ACEPTADO
                                            tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=00)
                                            tran.TCT1_TREOUP  = response.armar_tren
                                            tran.TCT1_ESTADO  = 'ACE'
                                            tran.save()
                                else:
                                    response.set_SACTU(saldo)
                                    response.set_SALDOS(saldo_disponible)
                                    response.set_CODRTN('00') #ACEPTADO
                                    tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=00)
                                    tran.TCT1_TREOUP  = response.armar_tren
                                    tran.TCT1_ESTADO  = 'ACE'
                                    tran.save()

                            ############################
                            ###  EXTRACCION/COMPRA   ###
                            ############################

                            if request.codigo in [  CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('COMPRA')], \
                                                    CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('ADELANTO EFECTIVO (POS)')], \
                                                    CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('EXTRACCION EFECTIVO (ATM)')], \
                                                    CODIGOS_SOLICITUDES.keys()[CODIGOS_SOLICITUDES.values().index('PAGO DE SERVICIOS')] ]:
                                saldo_disponible = cuenta_debito.get_saldo_disponible
                                saldo = cuenta_debito.AHAH_SALDO

                                if saldo_disponible < request.get_importe + recargo:
                                    response.set_SACTU(saldo)
                                    response.set_SALDOS(saldo_disponible)
                                    response.set_CODRTN('51') #SALDO INSUFICIENTE
                                    tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=51)
                                    tran.TCT1_TREOUP  = response.armar_tren
                                    tran.TCT1_ESTADO  = 'REC'
                                    tran.save()
                                else:
                                    tran.save()

                                    try:
                                        tran.debitar(importe=request.get_importe)
                                    except Exception, e:
                                        response.set_SACTU(saldo)
                                        response.set_SALDOS(saldo_disponible)
                                        response.set_CODRTN('06') #ERROR
                                        tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=06)
                                        tran.TCT1_TREOUP  = response.armar_tren
                                        tran.TCT1_ESTADO  = 'REC'
                                        mensaje = unicode(e)
                                        tran.save()

                                    else:
                                        if recargo:
                                            try:
                                                tran.aplicar_recargo(recargo)
                                            except Exception, e:
                                                mensaje = unicode(e)


                                        response.set_SACTU(cuenta_debito.AHAH_SALDO)
                                        response.set_SALDOS(cuenta_debito.get_saldo_disponible)
                                        response.set_CODRTN('00') #ACEPTADO
                                        tran.TCT1_CODRET  = tccodopr.objects.get(TCOS_PROCESO='BEP', TCOS_TIPCOD='RET', TCOS_CODIGO=00)
                                        tran.TCT1_TREOUP  = response.armar_tren
                                        tran.TCT1_ESTADO  = 'ACE'
                                        tran.save()
    except Exception, e:
        mensaje = unicode(e)
        logger.debug("mensaje :"+unicode(e)) #!IMPORTANTE
        if not 'request' in locals():
            request = trenRecibido
        if not 'response' in locals():
            response = Respuesta()

    return request, response, mensaje
    



@transaction.atomic
def procesar(trenRecibido):
    request, response, mensaje =  negociar(trenRecibido)
    #############################################
    ###     IMPORTANTE!  PARA EL DEMONIO      ###
    #############################################
    cuenta_debito = request.get_cuenta_debito
    response.set_SACTU(cuenta_debito.AHAH_SALDO)
    response.set_SALDOS(cuenta_debito.get_saldo_disponible)
    try:
        import couchdb
        couch = couchdb.Server(COUCHDB_SERVER)
        data = get_data_log(solicitud=request, respuesta=response, mensaje=mensaje)
        dbtable = couch['bepsalog']
        dbtable.create(data)
    except:
        pass
    print ('OUT: {0}'.format(response.armar_tren))
    return response.armar_tren




####################################
####   A PARTIR DE AUI BORRAR   ####
####################################
# import random
# from django.db import connection
# def get_secuenciador_mensaje():
#     secuenciador=''
#     for n in range(0, 15):
#         bit=random.sample('123456789', 1)
#         secuenciador=secuenciador+str(bit[0])
#     return secuenciador


# ctaDebito= raw_input("Cuenta Debito [1033631]:") or "1033631"
# Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ")

# Marca_de_Reversion = raw_input("Marca de reversion [99]:") or '00'
# if len(Marca_de_Reversion) > 2 or Marca_de_Reversion not in ['99', '00']:
#     print "Solo 2 digitos"
#     Marca_de_Reversion = raw_input("Marca de reversion [99]:")

# if len(Codigo_de_Transaccion) > 2:
#     print "Solo 2 digitos"
#     Codigo_de_Transaccion = raw_input("Codigo_de_Transaccion > ")
# ctaDebito=str(ctaDebito).rjust(10, '0')

# ################
# ###   RRN   ####
# ################
# query = (''' SELECT id FROM tctrxbepsa ORDER BY id DESC LIMIT 1  ''')
# cursor = connection.cursor()
# cursor.execute(query)
# RRN = cursor.fetchall()[0][0] + 50000000
# print "RRN: ", RRN 


# importe=raw_input("Importe >")
# importe=str(importe).rjust(15, '0')

# SecuenciadorRevers=''
# for n in range(0, 15):
#     bit=random.sample('123456789', 1)
#     SecuenciadorRevers=SecuenciadorRevers+str(bit[0])

# ahora = datetime.now()


# if Marca_de_Reversion == '99':
#     RRN = raw_input("Numero unico de transaccion:")
#     mensaje=ctaDebito\
#     +'|'+'000'+'|'+'0000000000'+'|'+'000'\
#     +'|'+str(Codigo_de_Transaccion)\
#     +'|'+Marca_de_Reversion\
#     +'|'+RRN.rjust(15, '0')\
#     +'|'+get_secuenciador_mensaje()\
#     +'|'+str(importe)\
#     +'|'+'000000000000000'\
#     +'|'+'000000000000000'\
#     +'|'+'0000'\
#     +'|'+'00'\
#     +'|'+'000'\
#     +'|'+'00'\
#     +'|'+'0000'\
#     +'|'+'000'\
#     +'|'+'40-caracteres-para-el-nombre-de-comercio'\
#     +'|'+RRN.rjust(15, '0')\
#     +'|'+'000'\
#     +'|'+str(ahora.day).rjust(2,'0')+str(ahora.month).rjust(2,'0')+str(ahora.year)\
#     +'|'+str(ahora.hour).rjust(2,'0')+str(ahora.minute).rjust(2,'0')+str(ahora.second).rjust(2,'0')+"|"
# else:
#     mensaje=ctaDebito\
#     +'|'+'000'+'|'+'0000000000'+'|'+'000'\
#     +'|'+str(Codigo_de_Transaccion)\
#     +'|'+'00'\
#     +'|'+str(RRN).rjust(15, '0')\
#     +'|'+get_secuenciador_mensaje()\
#     +'|'+str(importe)\
#     +'|'+'000000000000000'\
#     +'|'+'000000000000000'\
#     +'|'+'0000'\
#     +'|'+'00'\
#     +'|'+'000'\
#     +'|'+'00'\
#     +'|'+'0000'\
#     +'|'+'000'\
#     +'|'+'40-caracteres-para-el-nombre-de-comercio'\
#     +'|'+SecuenciadorRevers\
#     +'|'+'000'\
#     +'|'+str(ahora.day).rjust(2,'0')+str(ahora.month).rjust(2,'0')+str(ahora.year)\
#     +'|'+str(ahora.hour).rjust(2,'0')+str(ahora.minute).rjust(2,'0')+str(ahora.second).rjust(2,'0')+"|"
# salida = procesar(mensaje)
# print "ENT", mensaje
# print "OUT", salida
