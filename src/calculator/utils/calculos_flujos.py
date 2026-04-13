# Librerías Core
import pandas as pd
import numpy as np

# Librerías de Ayuda
from src.calculator.utils.logger_setup import notInfiniteLog, logWrapper
from src.calculator.utils.data_load import filterDataToToday, filterMensualidadesToOriginalBerex, emptyBerex

# Librerías Adicionales
from typing import Any, Tuple

# Función Auxiliar para Calcular las Facturas Pendientes del Cliente
@logWrapper(message="Calculando Facturas Pendientes del Cliente", onErrorValue=emptyBerex)
def calcularFacturasPendientes(moras: pd.DataFrame, berex: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el número de facturas pendientes del cliente.

    Args:
        moras (pd.DataFrame): DataFrame que contiene las moras.
        berex (pd.DataFrame): DataFrame que contiene los datos de berex.

    Returns:
        pd.DataFrame: El DataFrame con las facturas pendientes del cliente.
    """
    # Primero Obtenemos el Pago Total del Cliente
    pagoTotalCliente = moras['Pago'].sum()
    # Ahora Ordenamos el DF de berex por Fecha_Pago_Berex
    berexOrdenado = berex.sort_values(by='Fecha_Pago_Berex')
    # Ahora Creamos una Columna Acumulada de Monto_Berex en el DF de berex
    berexOrdenado['Monto_Berex_Acumulado'] = berexOrdenado['Monto_Berex'].cumsum()
    # Ahora Filtramos el DF de berex para Obtener Solo las Filas donde el Monto_Berex_Acumulado sea Mayor que el Pago Total del Cliente
    berexPendientes = berexOrdenado[berexOrdenado['Monto_Berex_Acumulado'] > pagoTotalCliente]
    # Finalmente, Devolvemos el DF de berex con las Facturas Pendientes del Cliente
    return berexPendientes

# Función para Calcular Métricas de los Flujos
@logWrapper(message="Calculando Métricas de Flujos", onErrorValue=(0,0,0,0,''))
def calcularMetricasFlujos(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> Tuple[float, float, float, float, str]:
    """
    Calcula las métricas de los flujos: Flujo Total, Flujo Promedio y Flujo Máximo.

    Args:
        moras (pd.DataFrame): DataFrame que contiene las moras.
        berex (pd.DataFrame): DataFrame que contiene los datos de berex.
        mensualidades (pd.DataFrame): DataFrame que contiene las mensualidades.

    Returns:
        Tuple[float, float, float, float, str]: Una tupla con:
        - El Pago Actual del Cliente
        - El Valor Total a Pagar por el Cliente
        - El Número de Cuotas Pendientes por Pagar del Cliente
        - El Porcentaje de Pago del Cliente
        - El Status de Mora del Cliente
    """
    # Filtramos los Datos a Hoy
    morasToday, berexToday, mensualidadesToday = filterDataToToday(moras, berex, mensualidades)

    # 1. Calculamos el Pago Actual del Cliente
    # Definimos el Pago Actual del Cliente como:
    # La Suma de Pago en Moras + la suma de Monto_Mensualidad en Mensualidades si Status_Facturacio != "POR_COBRAR"
    pagoActualMoras = morasToday['Pago'].sum()
    pagoActualMensualidades = mensualidadesToday[mensualidadesToday['Status_Facturacion'] != "POR_COBRAR"]['Monto_Mensualidad'].sum()
    pagoActualCliente = pagoActualMoras + pagoActualMensualidades

    # 2. Calculamos el Valor Total a Pagar por el Cliente
    # Definimos el Valor Total a Pagar por el Cliente como:
    # La Suma de Monto_Berex en Berex + la suma de Monto_Mensualidad en Mensualidades
    # Primero Filtramos las Mensualidades según el Flujo de Berex para Asegurar que solo Contemos las Mensualidades que Corresponden a los Berex Pendientes
    mensualidadesFiltradas = filterMensualidadesToOriginalBerex(mensualidades, berex)
    # Calculamos el Valor Total a Pagar por el Cliente
    valorTotalBerex = berexToday['Monto_Berex'].sum()
    valorTotalMensualidades = mensualidadesFiltradas['Monto_Mensualidad'].sum()
    valorTotalPagarCliente = valorTotalBerex + valorTotalMensualidades

    # 3. Calculamos el Número de Cuotas Pendientes (Facturas Pendientes)
    numCuotasPendientes = len(calcularFacturasPendientes(morasToday, berexToday))

    # 4. Calculamos el Porcentaje de Pago del Cliente
    porcentajePago = round(pagoActualCliente / valorTotalPagarCliente * 100, 2) if valorTotalPagarCliente != 0 else 0

    # 5. Calculamos el Status de Mora del Cliente como el último registro por Fecha
    statusMora = morasToday.sort_values(by='Fecha')['Status_Mora'].iloc[-1] if not morasToday.empty else 'Al día'

    return pagoActualCliente, valorTotalPagarCliente, numCuotasPendientes, porcentajePago, statusMora

# Función Auxiliar para Obtener el Pago Mínimo Inicial del Cliente
@logWrapper(message="Calculando el Pago Mínimo Inicial del Cliente", onErrorValue=(0,0))
def calcularPagoMinimoInicial(mensualidades: pd.DataFrame) -> tuple[int,float]:
    """
    Calcula el pago mínimo inicial del cliente.

    Args:
        mensualidades (pd.DataFrame): DataFrame que contiene las mensualidades.

    Returns:
        tuple:
            int: El número de mensualidades que el cliente tiene pendientes por pagar.
            float: El pago mínimo inicial del cliente.
    """
    # Definimos el Pago Mínimo Inicial del Cliente como el Monto_Mensualidad de la Primera Mensualidad a Pagar del Cliente
    # Primero Filtramos las Mensualidades para Obtener Solo las Mensualidades que el Cliente Aún No ha Pagado (Status_Facturacion != "POR_COBRAR")
    mensualidadesNoPagadas = mensualidades[mensualidades['Status_Facturacion'] != "POR_COBRAR"]
    # Ahora Filtramos los Datos menores a Hoy
    mensualidadesNoPagadasToday = mensualidadesNoPagadas[mensualidadesNoPagadas['Fecha_Mensualidad'] <= pd.Timestamp.today().normalize()]
    # Obtenemos la Suma del Monto
    montoTotalNoPagado = mensualidadesNoPagadasToday['Monto_Mensualidad'].sum()
    # Obtenemos el Número de Mensualidades no Pagadas
    numMensualidadesNoPagadas = len(mensualidadesNoPagadasToday)
    # Finalmente, Devolvemos el Número de Mensualidades y el Monto no Pagado como el Pago Mínimo Inicial del Cliente
    return numMensualidadesNoPagadas, montoTotalNoPagado