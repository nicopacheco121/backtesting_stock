from alertas_trades import *
from data_e_indicadores import *
from metrics import *
from graficos import *

from sqlalchemy import create_engine
import keys
import api_finviz

import pandas as pd
pd.options.display.max_rows=50
pd.options.display.max_columns=10

""" / / /  CONEXION DB  / / / """
sql_engine = create_engine(keys.DB_STOCKS)
sql_conn = sql_engine.connect()

""" / / / OBTENGO LA DATA / / / """

# PRIMERO VOY A HACER UN SCRAPPING DE FINVIZ PARA TENER ALGUNOS DATOS QUE PUEDEN SERVIR PARA FILTRAR
tabla_finviz = api_finviz.crearTablaFinviz(nombre='finviz',pags=range(400))

"""PONGO EN MARCHA LA ESTRATEGIA"""

# data=getDataExcel("pruebaY")
# #data=getInfoDiaria("AAPL")
# data.to_excel("pruebaY.xlsx")
# side = "both"

#Medias
media=True
fast=50
slow=200
mediaTipo="SMA"
buy_cr=0
sell_cr=0

#RSI
rsi=True
rsi_q=14
buy_rsi=50
sell_rsi=35

#STOPLOSS
stopActivar=False
porcen=0.9


# data=data.drop(["Open","High","Low"],axis=1)
# data=getAlertras(data,media=media,fast=fast, slow=slow, buy_cr=buy_cr, sell_cr=sell_cr,mediaTipo=mediaTipo,
#                  rsi_q=rsi_q, buy_rsi=buy_rsi, sell_rsi=sell_rsi,rsi=rsi,
#                  stopActivado=stopActivar,porcentaje=porcen,tipo=side)

# print("  /  /  /  ALERTAS  /  /  / ")
# print(data.head(200))
#
# acciones=getActions(data,side)
# print("  /  /  /  ACCIONES  /  /  /  ")
# print(acciones.head(200))
# trades=getTrades(acciones,side)
#
# print("  /  /  /  TRADES  /  /  / ")
# print(trades)
# metricasSenal = signalMetrics(data,side)
#
# print(" /  /  /  METRICAS SEÑALES  /  /  / ")
# print(metricasSenal)
#
# metricasTrades = tradesMetrics(trades,side)
# print(" /  /  /  METRICAS TRADES  /  /  / ")
# print(metricasTrades)

#grafico_con_alertas(data,acciones)


""" Terminé de setear las metricas de señales, habia un problema con el stop loss que lo cambiaba a sin señal y 
luego los borraba, no debería ser asi ya que el stop deberia poner sin señal pero no interpolar con la señal de 
compra o venta"""

"""falta hacer las metricas de trades"""