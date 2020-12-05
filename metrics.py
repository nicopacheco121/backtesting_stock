import pandas as pd
import numpy as np

def signalMetrics(df,tipo="both"):
    """Recibe un df y un side con señales y entrega variables estadisticas. Toma tiempos comprados, vendidos
    y sin posicion que hubieran operado según la estrategia. Difiere de la funcion del curso y a que acá tomaría el
    estado real de la posicion, si va both, al principio y final será sin señal y en el medio siempre será comprado
    o vendido ya que una el cierre de un lado es la apertura del otro. En el caso de stop loss difiere en que el cierre
    de una operacion no siempre es la apertura de otro.
    -Volatilidad media
    -Vdariacion media
    -Cantidad total de en cada estado
    -Volumen medio de cada estado
    -Tiempo total en cada estao"""

    df_copia = df.copy()
    df_copia = seteoSignal(df_copia,tipo=tipo)

    #COMIENZO CON LAS METRICAS
    #creo las medias en base a las señales
    medias = df_copia.groupby("Señal").mean()

    #genero un df nuevo que será el de las metricas, en este caso agrego volatilidad media
    res = pd.DataFrame(medias.Volatilidad)
    res.loc["Total"] = df_copia.Volatilidad.mean()

    #variacion
    res["Variacion"] = medias.Variacion
    res.loc["Total","Variacion"] = df_copia.Variacion.mean()

    #cantidad
    res["Cantidad"] = df_copia.groupby("Señal").size()
    res.loc["Total","Cantidad"] = df_copia.Señal.count()

    #volumen
    res["Volumen"] = medias.Volume /1000000
    res.loc["Total","Volumen"] = df_copia.Volume.mean() /1000000

    #tiempo
    res["TiempoIn"] = (df_copia.groupby("Señal").size() / df_copia.Señal.count()) *100
    res.loc["Total", "TiempoIn"] = 1

    #agrupado = metricas.drop(["Close","Volume","Variacion","Volatilidad"],axis=1)
    #agrupado= agrupado.groupby("Señal").size()

    return res

def seteoSignal(df,tipo="both"): # SETEO EL DF_COPIA para poder sacar metricas
    """ Recibe el df y side de signamMetrics y lo setea para colocar el estado que hubiera estado, ya sea
    comprado, vendido o sin posicion"""

    #reviso cuando da la primer señal
    df = df.reset_index()
    for i in range(len(df)):
        senal = df.iloc[i]["Señal"]
        if senal != "sin señal":
            fechaIni = i
            break

    # reviso cuando da la ultima señal
    for x in range(len(df)-1,0,-1):
        senalFin = df.iloc[x]["Señal"]
        if senalFin != "sin señal":
            fechaFin = x
            break
    df = df.set_index("Date").sort_index()

    # interpolo para que quede el "estado"
    df = df.reset_index()
    for z in range(fechaIni,fechaFin):
        if df.loc[z,"Señal"] == "sin señal":
            df.loc[z, "Señal"] = np.nan

    df["Señal"] = df.Señal.fillna(method="ffill")
    df = df.set_index("Date")

    # como tomo precios close y no podría comprar al cierre, tomo las variaciones del dia posterior
    df["Señal"] = df.Señal.shift()

    # seteo si es long o short
    if tipo == "long":
        df["Señal"] = np.where(df.Señal == "venta", "sin señal",
                                     df.Señal)  # saco la posicion vendido
    if tipo == "short":
        df["Señal"] = np.where(df.Señal == "compra", "sin señal", df.Señal)  # saco posicion compra

    # cambio el stop a sin señal
    df["Señal"] = np.where(df.Señal == "stop", "sin señal", df.Señal)  # saco la posicion stop

    return df

def tradesMetrics(df,tipo="both"):
    """ Recibe un df de trades y entrega otro con el Yield, los dias totales y la tir"""
    df["Factor"] = (df.Yield /100)+1
    long = df [df.Side == "long"]
    short = df [df.Side == "short"]
    res = pd.DataFrame(index=["Long","Short","Total"])

    #Yield
    res.loc["Long","Yield %"] = (long.Factor.prod() -1) *100
    res.loc["Short","Yield %"] = (short.Factor.prod() -1) *100
    res.loc["Total", "Yield %"] = (df.Factor.prod() -1) *100

    #Dias
    res.loc["Long","Dias"] = long.Dias.sum()
    res.loc["Short", "Dias"] = short.Dias.sum()
    res.loc["Total", "Dias"] = df.Dias.sum()

    #TIR
    if res.loc["Long","Dias"] > 0:
        res.loc["Long", "TIR"] = ((res.loc["Long","Yield %"] /100 +1) ** (365 / res.loc["Long","Dias"]) -1)*100
    if res.loc["Short","Dias"] > 0:
        res.loc["Short", "TIR"] = ((res.loc["Short","Yield %"] /100 +1) ** (365 / res.loc["Short","Dias"]) -1)*100
    if res.loc["Total","Dias"] > 0:
        res.loc["Total", "TIR"] = ((res.loc["Total","Yield %"] /100 +1) ** (365 / res.loc["Total","Dias"]) -1)*100

    return res.round(2)

