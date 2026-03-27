# Librerías Core
import streamlit as st
import pandas as pd
import numpy as np

# Librerías de Typing
from typing import Tuple

# Librerías de Ayuda
from src.calculator.utils.logger_setup import notInfinteLog

# Función Auxiliar para Calcular el Flujo Completo como DataFrame como Wrapper
def calcCompleteFlujo(flujoBerex: pd.DataFrame, flujoMensualidades: pd.DataFrame) -> pd.DataFrame:
    try:
        _calcCompleteFlujo(flujoBerex, flujoMensualidades)
        notInfinteLog('calculated_complete_flujo', 'Flujo completo calculado correctamente', method='debug')
    except Exception as e:
        notInfinteLog('calculated_complete_flujo', f'Error al calcular el flujo completo: {str(e)}', method='error')
        return pd.DataFrame()

# Función Auxiliar para Calcular el Flujo Completo como DataFrame
def _calcCompleteFlujo(flujoBerex: pd.DataFrame, flujoMensualidades: pd.DataFrame) -> pd.DataFrame:
    # El Flujo Completo Comprende los Datos de : Pagos de Comisiones, Pagos de PaB y pagos de Mensualidades,
    # cada uno con su respectiva fecha y si ya esta pagado o no

    # 1. Creamos el Diccionario donde se va a guardar la Información del Flujo Completo
    completeFlow = {
        'Fecha PaB': [],
        'Fecha Comision': [],
        'Fecha Mensualidad': [],
        'Monto PaB': [],
        'Monto Comision': [],
        'Monto Mensualidad': [],
        'Pagado PaB': [],
        'Pagado Comision': [],
        'Pagado Mensualidad': [],
    }

    # 2. Vamos a Iterar mes a mes y a ir añadiendo los datos respectivos
    startWindow = flujoBerex['Fecha_Pago_Berex'].min()
    endWindow = flujoBerex['Fecha_Pago_Berex'].max()

    currentDate = startWindow
    while currentDate <= endWindow:


        stopDate = currentDate.replace(day=1) + pd.offsets.MonthEnd()  # Fin del mes actual
        # Agregamos los Datos de PaB y Comisiones del Flujo de Berex
        flujoBerexCurrent = flujoBerex[flujoBerex['Fecha_Pago_Berex'].between(currentDate, stopDate)]

        # Calculamos el Pago Total del Mes
        pagoMes = flujoBerexCurrent['Pago'].sum()

        montoPaB = flujoBerexCurrent[flujoBerexCurrent['Destino'] == 'Banco']['Monto_Berex'].sum()
        montoComision = flujoBerexCurrent[flujoBerexCurrent['Destino'] == 'Comision']['Monto_Berex'].sum()
        pagadoPaB = montoPaB >= pagoMes
        pagadoComision = montoComision + montoPaB >= pagoMes
        fechaPaB = flujoBerexCurrent[flujoBerexCurrent['Destino'] == 'Banco']['Fecha_Pago_Berex'].min() if montoPaB > 0 else pd.NaT
        fechaComision = flujoBerexCurrent[flujoBerexCurrent['Destino'] == 'Comision']['Fecha_Pago_Berex'].min() if montoComision > 0 else pd.NaT

        # Agregamos los Datos de Mensualidades del Flujo de Mensualidades
        flujoMensualidadesCurrent = flujoMensualidades[flujoMensualidades['Fecha_Facturacion'].between(currentDate, stopDate)]
        montoMensualidad = flujoMensualidadesCurrent['Monto'].sum()
        pagadoMensualidad = np.all(flujoMensualidadesCurrent['Status_Facturacion'] != "POR_COBRAR") or flujoMensualidadesCurrent.empty
        fechaMensualidad = flujoMensualidadesCurrent[flujoMensualidadesCurrent['Status_Facturacion'] != "POR_COBRAR"]['Fecha_Facturacion'].min() if montoMensualidad > 0 else pd.NaT

        # Verificamos que exista alguna fecha si no continuamos
        if (pd.isna(fechaPaB) and pd.isna(fechaComision) and pd.isna(fechaMensualidad)):
            # Avanzamos al Siguiente Mes
            currentDate += pd.DateOffset(months=1)
            continue

        # Agregamos la Información al Flujo Completo
        completeFlow['Monto PaB'].append(montoPaB)
        completeFlow['Monto Comision'].append(montoComision)
        completeFlow['Monto Mensualidad'].append(montoMensualidad)
        completeFlow['Pagado PaB'].append(pagadoPaB)
        completeFlow['Pagado Comision'].append(pagadoComision)
        completeFlow['Pagado Mensualidad'].append(pagadoMensualidad)
        completeFlow['Fecha PaB'].append(fechaPaB)
        completeFlow['Fecha Comision'].append(fechaComision)
        completeFlow['Fecha Mensualidad'].append(fechaMensualidad)


        # Avanzamos al Siguiente Mes
        currentDate += pd.DateOffset(months=1)

    # Convertimos el Diccionario del Flujo Completo a un DataFrame
    dfCompleteFlow = pd.DataFrame(completeFlow)

    return dfCompleteFlow

# --- Métricas y Cálculos ---
# Función Auxiliar para Calcular Métricas Clave como Wrapper de la Función real
def calcMetricasFlujo(flujoBerex: pd.DataFrame) -> Tuple[float, float, float]:
    try:
        metricas = _calcMetricasFlujo(flujoBerex)
        notInfinteLog('calculated_flujo_metrics', f'Métricas del flujo calculadas correctamente: Total Pagado = {metricas[0]}, Total Monto Berex = {metricas[1]}, Porcentaje Pagado = {metricas[2]:.2f}%', method='debug')
        return metricas
    except Exception as e:
        notInfinteLog('error_calculating_flujo_metrics', f'Error al calcular las métricas del flujo: {e}', method='error')
        return 0.0, 0.0, 0.0

# Función Auxiliar para Calcular Métricas Clave del Flujo de Berex: Total Pagado, Total Monto Berex y Porcentaje Pagado
def _calcMetricasFlujo(dfFlujo: pd.DataFrame) -> Tuple[float, float, float]:
    try:
        # Calculamos el Total Pagado en el Flujo de Berex
        totalPagado = dfFlujo['Pago'].sum()
        # Calculamos el Total del Monto de Berex en el Flujo de Berex
        totalMontoBerex = dfFlujo['Monto_Berex'].sum()
        # Calculamos el Porcentaje Pagado del Monto de Berex en el Flujo de Berex
        porcentajePagado = (totalPagado / totalMontoBerex) * 100 if totalMontoBerex > 0 else 0.0
        notInfinteLog('calculated_flujo_metrics', f'Métricas del flujo calculadas correctamente: Total Pagado = {totalPagado}, Total Monto Berex = {totalMontoBerex}, Porcentaje Pagado = {porcentajePagado:.2f}%', method='debug')
        return totalPagado, totalMontoBerex, porcentajePagado
    except Exception as e:
        notInfinteLog('error_calculating_flujo_metrics', f'Error al calcular las métricas del flujo: {e}', method='error')
        raise e