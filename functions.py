# -*- coding: utf-8 -*-
#!/usr/bin/env python
from constant import os
from core.ahorro.models import ahahorro, ahmovimi, ahconcep


def get_cantidad_veces(nro_tarjeta, cod_transaccion):
    from django.db import connection
    cantidad_veces = ("""SELECT count(*)
                    from tctrxbepsa
                    join tccodopr on tccodopr.id = tctrxbepsa."TCT1_TCOSID"
                    join tctarjeta on tctarjeta."TCTA_NUCTA" = tctrxbepsa."TCT1_TCTAID"
                    where "TCT1_ESTADO"='ACE' 
                    and tccodopr."TCOS_PROCESO" = 'BEP'
                    and tccodopr."TCOS_CODIGO" = %s
                    and tctarjeta."TCTA_NUCTA" = \'%s\'
                    and "TCT1_NOW" BETWEEN  to_char(date_trunc('month', now()::date), 'yyyy-MM-dd HH24:MI:ss')
                    and to_char(date_trunc('month', now()::date) +'1month' ::interval -'1sec' ::interval, 'yyyy-MM-dd HH24:MI:ss')""" % (cod_transaccion, nro_tarjeta))  
    cursor = connection.cursor()
    cursor.execute(cantidad_veces)
    cantidad = cursor.fetchall()
    #logger.info('nro de uso de tarjeta para %s : %s' % (nro_tarjeta, cantidad[0][0]))
    return cantidad[0][0]
