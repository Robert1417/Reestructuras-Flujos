# Librerías Core
import streamlit as st
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.calculos_flujos import calcularMetricasFlujos, calcularFacturasPendientes
from src.calculator.utils.logger_setup import logWrapper,stWarningLogWrapper
from src.calculator.utils.data_load import columnasBerex

# Función para Mostrar el Flujo de Berex y Métricas en la Aplicación
@stWarningLogWrapper(message="Error al mostrar el Flujo de Berex y Métricas en la Aplicación")
def mostrarFlujoBerexYMetricas(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> None:
    """
    Muestra el flujo de berex y las métricas calculadas en la aplicación.

    Args:
        moras (pd.DataFrame): DataFrame que contiene las moras.
        berex (pd.DataFrame): DataFrame que contiene los datos de berex.
        mensualidades (pd.DataFrame): DataFrame que contiene las mensualidades.
    """
    # Calculamos las Métricas de los Flujos
    pagoActualCliente, valorTotalPagar, cuotasPendientes, porcentajePago, statusMora = calcularMetricasFlujos(moras, berex, mensualidades)

    # Creamos 2 Columnas: 1 para mostrar el Flujo de Berex y otra para mostrar las Métricas
    col1, col2 = st.columns([3, 1])

    # En la Columna 1, Mostramos el Flujo de Berex
    with col1:
        st.subheader("Flujo de Berex")
        # Mostramos los Datos de Berex
        st.dataframe(berex[columnasBerex])

    # En la Columna 2, Mostramos las Métricas Calculadas
    with col2:
        st.subheader("Métricas del Cliente")
        st.metric(label="Pago Actual del Cliente", value=f"${pagoActualCliente:,.2f}")
        st.metric(label="Valor Total a Pagar por el Cliente",
                value=f"${valorTotalPagar:,.2f}",
                delta=f"${valorTotalPagar - pagoActualCliente:,.2f}", delta_color="inverse")
        st.metric(label="Número de Cuotas Pendientes por Pagar del Cliente",
                value=cuotasPendientes,
                delta_color="green" if cuotasPendientes > 0 else "red")
        st.metric(label="Porcentaje de Pago del Cliente", value=f"{porcentajePago:.2f}%", delta="100.00%")
        st.metric(label="Status de Mora del Cliente",
                value=statusMora,
                delta_color="green" if statusMora.lower() == "al día" else "red")

# Función Auxiliar para Mostrar los Párametros de la Reestructura
@stWarningLogWrapper(message="Error al mostrar los Parámetros de la Reestructura")
def mostrarParametrosReestructura(params: dict) -> None:
    """
    Muestra los parámetros de la reestructura en la aplicación.

    Args:
        params (dict): Diccionario que contiene los parámetros de la reestructura.
    """
    st.subheader("Parámetros de la Reestructura")

    # Creamos las Columnas Necesarias para Mostrar los Parámetros de la Reestructura
    cols = st.columns(len(params), vertical_alignment="center")
    for i, (parametro, valor) in enumerate(params.items()):
        with cols[i]:
            st.metric(label=parametro, value=valor)