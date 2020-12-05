from data_e_indicadores import *
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO,format='{asctime} {levelname} ({threadName:11s}) {message}', style='{')

def getAlertras(df,media=True,mediaTipo="SMA",fast=5,slow=20,buy_cr=0,sell_cr=0,
                rsi=True,rsi_q=14,buy_rsi=50,sell_rsi=35,
                stopActivado=False,porcentaje=1.0,
                tipo="both"):
    """Recibe un df y los parametros y agrega los indicadores y la señal, por ahora solo SMA, EMA, RSI y STOP LOSS
    Tambien agrega volatilidad y variacion"""
    logging.info(f"Creando Alertas")

    df["Variacion"] = df.Close.pct_change()*100
    df["Volatilidad"] = df.Variacion.rolling(250).std() * 250**0.5
    #Medias
    compraMedia=True
    ventaMedia=True
    if media:
        if mediaTipo=="SMA":
            df=cruceSMA(df,fast,slow).copy()
        else:
            df=cruceEMA(df,fast,slow).copy()
        compraMedia= df.cruce > buy_cr
        ventaMedia= df.cruce < sell_cr

    #RSI
    compraRSI=True
    ventaRSI=True
    if rsi:
        df=getRSI(df,rsi_q).copy()
        compraRSI= df.RSI > buy_rsi
        ventaRSI= df.RSI < sell_rsi

    df= getSenales(df,compraMedia,ventaMedia,compraRSI,ventaRSI,stopActivado=stopActivado,porcentaje=porcentaje,tipo=tipo)
    df.set_index("Date",inplace=True)

    return df

def getSenales(df,compraMedia,ventaMedia,compraRSI,ventaRSI,stopActivado,porcentaje,tipo):
    """ Recibe el df y los parametros y agrega señales al df"""
    logging.info(f"Añadiendo las señales")
    copia = df.copy()
    copia = copia.reset_index()

    stop={"porcentaje":porcentaje,"pStop":False,"estado":"sin señal"}
    listaSenal=[]
    for i in range(len(copia)):
        precioActual = copia.loc[i]["Close"]

        if stopActivado: #verifica si se toma o no el stop loss

            if tipo != "short" and stop["estado"] == "compra" and precioActual < stop["pStop"]: #stop si es long o both y está comprado
                listaSenal.append("stop")
                stop["pStop"] = False
                stop["estado"] = "stop"
                continue
            elif tipo != "long" and stop["estado"] == "venta" and precioActual > stop["pStop"]: #stop si es short y está vendido
                listaSenal.append("stop")
                stop["pStop"] = False
                stop["estado"] = "stop"
                continue

        if compraRSI[i] and compraMedia[i]: #señal compra
            if stop["estado"] == "compra": #si ya estoy comprado no pone señal
                listaSenal.append("sin señal")

            elif tipo == "short" and stop["estado"] != "venta": #si voy short y no estoy vendido no puede comprar
                listaSenal.append("sin señal")

            else: #si estoy long/both y no estoy comprado o si estoy short y esta vendido
                listaSenal.append("compra")
                stop["pStop"] = precioActual * stop["porcentaje"] #pone el nuevo stop
                stop["estado"]="compra"

        elif ventaMedia[i] and ventaRSI[i]: #señal venta
            if stop["estado"] == "venta": #si ya estoy vendido no pone señal
                listaSenal.append("sin señal")
            elif tipo == "long" and stop["estado"] != "compra": #si voy long y no estoy comprado no puedo vender
                listaSenal.append("sin señal")
            else: #si voy short/both y no estoy vendido, o si voy long y estoy comprado
                listaSenal.append("venta")
                stop["pStop"] = precioActual * (1 + (1- stop["porcentaje"]))
                stop["estado"] = "venta"

        else: #no es ni stop, ni compra ni venta
            listaSenal.append("sin señal")

    copia["Señal"] = listaSenal


    return copia

def getActions(df,tipo="both"):
    """Recibe el df, saca los sin señal y setea si es compra o venta para los primeros y ultimos trades"""
    logging.info(f"Seteando el data frame ")
    actions = df.loc [ df.Señal != "sin señal"] . copy()
    actions = actions.reset_index()

    primera = actions.iloc[0]["Señal"]
    ultima = actions.iloc[-1]["Señal"]

    #Elimina aperturas y cierres que no tienen sentido
    if tipo == "long":
        if primera == "venta":
            actions = actions.iloc[1:]
        if ultima == "compra":
            actions = actions.iloc[:-1]

    if tipo == "short":
        if primera == "compra":
            actions = actions.iloc[1:]
        if ultima == "venta":
            actions = actions.iloc[:-1]

    actions = actions.set_index("Date")
    return actions

def getTrades(df,tipo="both"): #estoy n esto

    """toma las acciones y me arma un libro con cada trade"""
    logging.info(f"Creando libro de trades")
    trades={}
    f_ini=[]
    f_fin=[]
    p_ini=[]
    p_fin=[]
    listaSide=[]
    df=df.reset_index()
    abierto = False

    for i in range(len(df)):

        if tipo != "both": #si es diferente de both, funciona la regla de que los pares abren operacion
            # tomo los pares para empezar por el primero ya que viene seteado desde antes

            if i % 2 == 0 and i != (len(df) - 1):
                f_ini.append(df.iloc[i]["Date"])
                p_ini.append(df.iloc[i]["Close"])
                listaSide.append(tipo) #cuando abre tambien pone el side
            elif i % 2 != 0:
                f_fin.append(df.iloc[i]["Date"])
                p_fin.append(df.iloc[i]["Close"])

        else:
            senal = df.iloc[i]["Señal"] #le agrego el side
            if senal == "compra":
                direccion = "long"
            elif senal == "venta":
                direccion = "short"

            if i == 0:
                #abro el primer trade
                f_ini.append(df.iloc[i]["Date"])
                p_ini.append(df.iloc[i]["Close"])
                abierto = True
                listaSide.append(direccion)

            elif i == (len(df) - 1): #si es el ultimo, lo cierro
                f_fin.append(df.iloc[i]["Date"])
                p_fin.append(df.iloc[i]["Close"])
                break

            elif senal == "stop":
                f_fin.append(df.iloc[i]["Date"])
                p_fin.append(df.iloc[i]["Close"])
                abierto = False

            elif i>0 and senal != "stop":
                if abierto == True: #si viene un trade abierto, lo cierro y abro otro
                    f_fin.append(df.iloc[i]["Date"])
                    p_fin.append(df.iloc[i]["Close"])

                    f_ini.append(df.iloc[i]["Date"])
                    p_ini.append(df.iloc[i]["Close"])
                    listaSide.append(direccion)

                else: #si vengo de un trade cerrado, solo lo abro
                    f_ini.append(df.iloc[i]["Date"])
                    p_ini.append(df.iloc[i]["Close"])
                    abierto=True
                    listaSide.append(direccion)

    trades["Fecha_ini"]=f_ini
    trades["Precio_ini"]=p_ini
    trades["Side"] = listaSide
    trades["Fecha_fin"]=f_fin
    trades["Precio_fin"]=p_fin


    trades=pd.DataFrame(trades) #creo el data frame con el diccionario

    df = df.set_index("Date") #pongo el indice como estaba
    trades = getResult(trades)

    return trades


def getResult(df):
    """Recibe un df con acciones de compra venta y stop y le agrega el Yield y la cantidad de Dias"""
    logging.info(f"Calculando Yield y Dias")
    df["Yield"] = np.where(df["Side"] == "long",(df["Precio_fin"] / df["Precio_ini"] -1)*100,(df["Precio_ini"] / df["Precio_fin"] -1)*100)
    df["Dias"] = (df.Fecha_fin - df.Fecha_ini).dt.days

    return df



#EN PROCESO
"""def tradesMetric(df):
    df_copia = df.copy()
    df_copia["factor"] = (df_copia["Yield"] /100)+1
    media = df_copia.groupby("Side").mean()

    resultado= pd.DataFrame(media.Yield)
    resultado["Total","Yield"] =  media.Yield.sum()
    return resultado"""


