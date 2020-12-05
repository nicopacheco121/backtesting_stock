import logging
logging.basicConfig(level=logging.INFO,format='{asctime} {levelname} ({threadName:11s}) {message}', style='{')


#funcion para descargar info diaria. Para intra se utilizará alphavange
def getInfoDiaria(ticker, start="2000-01-01",interval="1d",end=None):
    """Recibe un ticker y devuelve la info diaria historica del papel"""
    logging.info(f"importando info de {ticker} ")
    import yfinance as yf
    df=yf.download(ticker,start=start,end=end,interval=interval,auto_adjust=True)
    return df

def getDataExcel(ticker):
    '''
       SOLO SIRVE PARA EXCEL DESCARGADO DEYAHOO FINANCE
       Busca excel de datos y devuelve DF las columnas: 'Open','High','Low','Close','Volume'.
       La columna 'Close' trae el precio ajustado.
       |
       |_ ticker:  El ticker a buscar
       '''
    import pandas as pd
    try:
        data = pd.read_excel(ticker + '.xlsx').set_index('Date').sort_index()
        #data.index.names=["Date"]
        data.columns = ['Open', 'High', 'Low','Close', 'Volume']
    except:
        try:
            data = pd.read_excel('excels_csvs/ADRs/' + ticker + '.xlsx').set_index('timestamp').sort_index()
            data.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']
            data['pctChange'] = data.AdjClose.pct_change()
        except:

            data = 'Sorry man no encontre el archivo en tu directorio'
    #data = data.drop(["Borrar"],axis=1)
    return data


def cruceSMA(df,fast=10,slow=20):
    """Recibe un df y una cantidad de ruedas y devuelve una columna con el SMA_ruedas"""
    logging.info(f"Creando cruce SMA, fast: {fast} slow: {fast} ")
    df["cruce"] = round((df.Close.rolling(fast).mean() / df.Close.rolling(slow).mean() -1) *100,2)
    return df

def cruceEMA(df,fast=10,slow=20): #ewm(span=ruedas)
    """Recibe un df y una cantidad de ruedas y devuelve una columna con el SMA_ruedas"""
    logging.info(f"Creando cruce EMA, fast: {fast} slow: {fast} ")
    df["cruce"] = round((df.Close.ewm(span=fast).mean() / df.Close.ewm(span=slow).mean() - 1) * 100, 2)
    return df

def getRSI(df,ruedas=14):
    """Recibe un df y una cantidad de ruedas (por defecto 14) y devuelve una columna con el RSI"""
    logging.info(f"Creando RSI, ruedas: {ruedas}")
    import numpy as np

    df["diferencia"]=df.Close.diff()
    df["dif_pos"] = np.where(df["diferencia"] > 0,df["diferencia"],0)
    df["dif_neg"] = np.where(df["diferencia"] < 0, df["diferencia"], 0)
    df["media_pos"] = df["dif_pos"].ewm(alpha=1/ruedas).mean()
    df["media_neg"] = df["dif_neg"].ewm(alpha=1/ruedas).mean()
    df["rs"] = df["media_pos"] / abs(df["media_neg"])
    df["RSI"] = round(100 - 100 / (1 + df["rs"]),2)
    df=df.drop(["diferencia","dif_pos","dif_neg","media_pos","media_neg","rs"],axis=1)
    return df

def getMACD(df,fast=12,slow=26,signal=9):
    """Recibe un df y un numero para fast (defecto 12), slow (defecto 26) u signal (defecto 9) devuelve una columna con el MACD"""
    logging.info(f"Creando MACD")
    df["ema_fast"] = df.Close.ewm(span=fast).mean()
    df["ema_slow"] = df.Close.ewm(span=slow).mean()
    df["macd"] = df["ema_fast"] - df["ema_slow"]
    df["signal"] = df["macd"].ewm(span=signal).mean()
    df["histograma"] = df["macd"] - df["signal"]
    df = df.drop(["ema_fast", "ema_slow"], axis=1)
    return df