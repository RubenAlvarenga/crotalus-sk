# -*- coding: utf-8 -*-
#!/usr/bin/env python
from constant import os
from core.ahorro.models import ahahorro, ahmovimi, ahconcep
from core.tarjeta.models import tctarjeta, tctrxbepsa
from datetime import date, datetime
from django.db import transaction
from constant import BIN, TIPO_DOCUMENTO, CONCEPTO_CREDITO, CONCEPTO_DEBITO, CONCEPTO_DEBITO_RECARGO, CONCEPTO_CREDITO_RECARGO, TIPO_DOCUMENTO_RECARGO
from codigos import CODIGOS_RESPUESTAS, CODIGOS_SOLICITUDES

class Solicitud(object):
    def __init__(self, tren):
        super(Solicitud, self).__init__()
        trensplitado = tren.split('|')
        try:
            self.cuenta_debito            = trensplitado[0]
            self.banco_debito             = trensplitado[1]
            self.cuenta_credito           = trensplitado[2]
            self.banco_credito            = trensplitado[3]
            self.codigo                   = trensplitado[4]
            self.extorno                  = trensplitado[5]
            self.numero_transaccion_banco = trensplitado[6]
            self.numero_boleta            = trensplitado[7] #(RRN)
            self.importe                  = trensplitado[8]
            self.IMPOB                    = trensplitado[9]
            self.IMPOC                    = trensplitado[10]
            self.CANHQ                    = trensplitado[11]
            self.moneda                   = trensplitado[12]
            self.LUNAR                    = trensplitado[13]
            self.CAJA                     = trensplitado[14]
            self.NUMTRCJ                  = trensplitado[15]
            self.HORA14                   = trensplitado[16]
            self.negocio                  = trensplitado[17]
            self.reversar_transaccion     = trensplitado[18]
            self.ATMBCO                   = trensplitado[19]
            self.fecha                    = trensplitado[20]
            self.hora                     = trensplitado[21]
        except Exception, e:
            return e
        # self.cuenta_debito            = tren[0:10]
        # self.banco_debito             = tren[10:13]
        # self.cuenta_credito           = tren[13:23]
        # self.banco_credito            = tren[23:26]
        # self.codigo                   = tren[26:28]
        # self.extorno                  = tren[28:30]
        # self.numero_transaccion_banco = tren[30:45]
        # self.numero_boleta            = tren[45:60] #(RRN)
        # self.importe                  = tren[60:75]
        # self.IMPOB                    = tren[75:90]
        # self.IMPOC                    = tren[90:105]
        # self.CANHQ                    = tren[105:109]
        # self.moneda                   = tren[109:111]
        # self.LUNAR                    = tren[111:114]
        # self.CAJA                     = tren[114:116]
        # self.NUMTRCJ                  = tren[116:120]
        # self.HORA14                   = tren[120:123]
        # self.negocio                  = tren[123:163]
        # self.reversar_transaccion     = tren[163:178]
        # self.ATMBCO                   = tren[178:181]
        # self.fecha                    = tren[181:189]
        # self.hora                     = tren[189:195]

    @property
    def armar_tren(self):
        solicitud = self.cuenta_debito +'|'+ self.banco_debito +'|'+ self.cuenta_credito +'|'+ self.banco_credito +'|'+ self.codigo +'|'+ self.extorno +'|'+ self.numero_transaccion_banco +'|'+ self.numero_boleta +'|'+ self.importe +'|'+ self.IMPOB +'|'+ self.IMPOC +'|'+ self.CANHQ +'|'+ self.moneda +'|'+ self.LUNAR +'|'+ self.CAJA +'|'+ self.NUMTRCJ +'|'+ self.HORA14 +'|'+ self.negocio +'|'+ self.reversar_transaccion +'|'+ self.ATMBCO +'|'+ self.fecha +'|'+ self.hora + '|'
        return solicitud

    @property
    def get_tarjeta(self):
        return tctarjeta.objects.get(TCTA_NUCTA= BIN + self.cuenta_debito.rjust(10,'0'), \
                                        TCTA_TIPO__TCTI_TIPO = 'TD1', \
                                        TCTA_DMAVT__gt=date.today(), \
                                        TCTA_DMAET__lte=date.today(), \
                                        TCTA_ESTAD='ACT')

    @property
    def get_importe(self):
        return int(self.importe[:-2])

    @property
    def get_cuenta_debito(self):
        return ahahorro.objects.get(AHAH_NROAH=self.cuenta_debito[4:], AHAH_TIPO=self.cuenta_debito[:4])











class Respuesta(object):
    def __init__(self, arg=None):
        super(Respuesta, self).__init__()
        self.CODRTN = '06'
        self.SALDOS = '000000000000000|+'
        self.SACTU  = '000000000000000|+'
        self.DOCUM  = ''
        self.LOCAL  = ''
        self.CANEXT = '000'
        self.DOCELI = ''
        self.SCRDTA = ''
        self.cuenta_ahorro = None

    def set_CODRTN(self, valor):
        self.CODRTN = valor
    def set_SALDOS(self, valor):
        if valor >= 0:
            self.SALDOS = (str(valor)+'00|+').rjust(16, '0')
        else:
            self.SALDOS = (str(valor)+'00|-').rjust(16, '0')
    def set_SACTU(self, valor):
        if valor >= 0:
            self.SACTU = (str(valor)+'00|+').rjust(16, '0')
        else:
            self.SACTU = (str(valor)+'00|-').rjust(16, '0')
    def set_DOCUM(self, valor):
        self.DOCUM = valor
    def set_LOCAL(self, valor):
        self.LOCAL = valor
    def set_CANEXT(self, valor):
        self.CANEXT = valor
    def set_DOCELI(self, valor):
        self.DOCELI = valor
    def set_SCRDTA(self, valor):
        self.SCRDTA = valor


    def set_cuenta_ahorro(self, valor):
        self.cuenta_ahorro = valor

    @property    
    def set_to_json(self):
        return {
            'CODRTN' : self.CODRTN ,
            'SALDOS' : self.SALDOS ,
            'SACTU' : self.SACTU ,
            'DOCUM' : self.DOCUM ,
            'LOCAL' : self.LOCAL ,
            'CANEXT' : self.CANEXT ,
            'DOCELI' : self.DOCELI ,
            'SCRDTA' : self.SCRDTA 
        }


    @property
    def armar_tren(self):
        respuesta = self.CODRTN +"|"+ self.SALDOS +"|"+ self.SACTU +"|"+ self.DOCUM +"|"+ self.LOCAL +"|"+ self.CANEXT +"|"+ self.DOCELI +"|"+ self.SCRDTA +"|"
        return respuesta





class Transaccion(tctrxbepsa):
    class Meta:
        proxy = True
        app_label = 'coopnet.tarjeta'


    @property
    def get_recargo(self):
        movimiento = ahmovimi.objects.filter(AHMO_TIDOC='CATM', AHMO_NUMCO=self.id, AHMO_AHID=self.get_cuenta_debito.id)
        if movimiento: 
            return movimiento[0] 
        else: return None


    @property
    def get_cuenta_debito(self):
        return ahahorro.objects.get(AHAH_NROAH=self.TCT1_TCTAID.TCTA_NUCTA[-6:], \
                                    AHAH_TIPO=self.TCT1_TCTAID.TCTA_NUCTA[-8:-6])


    @transaction.atomic
    def debitar(self, importe):
        ahorro = self.get_cuenta_debito
        deb=ahmovimi()
        deb.AHMO_TIPO   = ahorro.AHAH_TIPO
        deb.AHMO_SUBTI  = ahorro.AHAH_SUBTI
        deb.AHMO_NROAH  = ahorro.AHAH_NROAH
        deb.AHMO_TIDOC  = TIPO_DOCUMENTO
        deb.AHMO_CODCO  = ahconcep.objects.get(AHCO_CODCO=CONCEPTO_DEBITO) #extraccion
        deb.AHMO_NUMCO  = self.id
        deb.AHMO_DMAMO  = date.today()
        deb.AHMO_IMPOR  = importe
        deb.AHMO_COTIZ  = 100
        deb.AHMO_ESTAD  = 'C'
        deb.AHMO_MOVID  = None
        deb.AHMO_OBS    = "desde Socket BEPSA"
        deb.AHMO_TIMOV  = None
        deb.AHMO_AHID   = ahorro
        deb.AHMO_INTCAL = 0
        deb.AHMO_DMACIN = None
        deb.AHMO_TASA   = 0.0
        deb.save()
        return True


    @transaction.atomic
    def reversar(self, new):
        ahorro = self.get_cuenta_debito
        if self.TCT1_CODOPR in ['00', '02', '05', '10', '72']:
            if self.TCT1_IMPORTE > 0:
                obj = ahmovimi()
                obj.AHMO_TIPO   = ahorro.AHAH_TIPO
                obj.AHMO_SUBTI  = ahorro.AHAH_SUBTI
                obj.AHMO_NROAH  = ahorro.AHAH_NROAH
                obj.AHMO_TIDOC  = TIPO_DOCUMENTO
                obj.AHMO_CODCO  = ahconcep.objects.get(AHCO_CODCO=CONCEPTO_CREDITO) #deposito
                obj.AHMO_NUMCO  = new.id
                obj.AHMO_DMAMO  = date.today()
                obj.AHMO_IMPOR  = int(self.TCT1_IMPORTE)
                obj.AHMO_COTIZ  = 100
                obj.AHMO_ESTAD  = 'C'
                obj.AHMO_MOVID  = None
                obj.AHMO_OBS    = "desde Socket BEPSA"
                obj.AHMO_TIMOV  = None
                obj.AHMO_AHID   = ahorro
                obj.AHMO_INTCAL = 0
                obj.AHMO_DMACIN = None
                obj.AHMO_TASA   = 0.0
                obj.save()
        if self.get_recargo:
            rec=ahmovimi()
            rec.AHMO_TIPO   = ahorro.AHAH_TIPO
            rec.AHMO_SUBTI  = ahorro.AHAH_SUBTI
            rec.AHMO_NROAH  = ahorro.AHAH_NROAH
            rec.AHMO_TIDOC  = 'CATM'
            rec.AHMO_CODCO  = ahconcep.objects.get(AHCO_CODCO=CONCEPTO_CREDITO_RECARGO) #deposito
            rec.AHMO_NUMCO  = new.id
            rec.AHMO_DMAMO  = date.today()
            rec.AHMO_IMPOR  = int(self.get_recargo.AHMO_IMPOR)
            rec.AHMO_COTIZ  = 100
            rec.AHMO_ESTAD  = 'C'
            rec.AHMO_MOVID  = None
            rec.AHMO_OBS    = "desde Socket BEPSA"
            rec.AHMO_TIMOV  = None
            rec.AHMO_AHID   = ahorro
            rec.AHMO_INTCAL = 0
            rec.AHMO_DMACIN = None
            rec.AHMO_TASA   = 0.0
            rec.save()
        return True
    
    @transaction.atomic
    def aplicar_recargo(self, recargo=0):
        ahorro = self.get_cuenta_debito
        obj=ahmovimi()
        obj.AHMO_TIPO   = ahorro.AHAH_TIPO
        obj.AHMO_SUBTI  = ahorro.AHAH_SUBTI
        obj.AHMO_NROAH  = ahorro.AHAH_NROAH
        obj.AHMO_TIDOC  = TIPO_DOCUMENTO_RECARGO
        obj.AHMO_CODCO  = ahconcep.objects.get(AHCO_CODCO=CONCEPTO_DEBITO_RECARGO) #extraccion
        obj.AHMO_NUMCO  = self.id
        obj.AHMO_DMAMO  = date.today()
        obj.AHMO_IMPOR  = recargo
        obj.AHMO_COTIZ  = 100
        obj.AHMO_ESTAD  = 'C'
        obj.AHMO_MOVID  = None
        obj.AHMO_OBS    = "desde Socket BEPSA"
        obj.AHMO_TIMOV  = None
        obj.AHMO_AHID   = ahorro
        obj.AHMO_INTCAL = 0
        obj.AHMO_DMACIN = None
        obj.AHMO_TASA   = 0.0
        obj.save()
        return True







def get_data_log(solicitud=None, respuesta=None, mensaje=None):
    if mensaje:
        men = mensaje 
    else:
        men = CODIGOS_RESPUESTAS[respuesta.CODRTN]
    data = {
        'RRN' : solicitud.numero_transaccion_banco,
        'NROAH' : solicitud.cuenta_debito,
        'CODRTN' : respuesta.CODRTN,
        'FECHA' : datetime.now().strftime("%d/%m/%Y"), 
        'HORA' : datetime.now().strftime("%H:%M:%S"), 
        'TREN_INPUT' : solicitud.armar_tren,
        'TREN_OUTPUT' : respuesta.armar_tren, 
        'INPUT' : solicitud.__dict__, 
        'OUTPUT' : respuesta.set_to_json,
        'IMPORTE': solicitud.get_importe,
        'MENSAJE' : men
    }
    return data