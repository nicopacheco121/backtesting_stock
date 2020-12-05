import matplotlib.pyplot as plt

def grafico_con_alertas(datos,alerta):
    """Recibe un df y al grafico de precios del papel le agrega los indicadores de entradas y salidas
    Falta SI TIENE STOP, OTRA CONFIGURTAR LA OTRA SALIDA"""

    compra = alerta [alerta.Señal == "compra"]
    compraPos = (compra.Close* 0.9)
    print(compraPos)

    venta = alerta [alerta.Señal == "venta"]
    ventaPos = (venta.Close* 1.1)

    #grafico
    plt.figure(figsize=(20,10))
    f1 = plt.plot(datos.Close, c="k", ls="-", lw=1.5)

    plt.legend(["Precio"], loc="lower right", fontsize=14)
    plt.plot(compraPos.index, compraPos, "^", markersize=10, c="g")
    plt.plot(ventaPos.index, ventaPos, "v", markersize=10, c="r")

    return plt.show()