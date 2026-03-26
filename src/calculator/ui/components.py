# Datos de Componentes de la Interfaz de Usuario para el Flujo Berex

# Librearías Core
import streamlit as st

# Librerías de Manipulación de Datos
import pandas as pd

# Librerías de Utilidades
from src.calculator.utils.helpers import notInfinteLog, calcMetricasFlujo

# Función Auxiliar para Mostrar los Párametros de Entrada en la Barra Lateral como Métricas
def mostrarParametrosEntrada(cliente_ref, fecha_inicio_pago, nuevo_apartado_mensual, nuevo_pago_inicial):

    # Se van a mostrar cada uno en una columna
    col1, col2, col3, col4 = st.sidebar.columns(4, gap="small", vertical_alignment='center')

    col1.metric("Referencia del Cliente", cliente_ref)
    col2.metric("Fecha Inicio de Pago", fecha_inicio_pago.strftime("%Y-%m-%d"))
    col3.metric("Nuevo Apartado Mensual", f"${nuevo_apartado_mensual:,.2f}")
    col4.metric("Nuevo Pago Inicial", f"${nuevo_pago_inicial:,.2f}")

# Función Auxiliar para Comparar Métricas entre 2 Flujos
def compararMetricasFlujo(dfFlujo1: pd.DataFrame, dfFlujo2: pd.DataFrame, subheader1: str, subheader2: str):
    col1, col2 = st.columns(2, gap="large", width=[1, 1], vertical_alignment='center')

    with col1:
        st.subheader(subheader1)
        totalPagado1, totalMontoBerex1, porcentajePagado1 = calcMetricasFlujo(dfFlujo1)
        st.metric("Total Pagado", f"${totalPagado1:,.2f}")
        st.metric("Total Monto Berex", f"${totalMontoBerex1:,.2f}")
        st.metric("Porcentaje Pagado", f"{porcentajePagado1:.2f}%")

    with col2:
        st.subheader(subheader2)
        totalPagado2, totalMontoBerex2, porcentajePagado2 = calcMetricasFlujo(dfFlujo2)
        st.metric("Total Pagado", f"${totalPagado2:,.2f}")
        st.metric("Total Monto Berex", f"${totalMontoBerex2:,.2f}")
        st.metric("Porcentaje Pagado", f"{porcentajePagado2:.2f}%")

# Función Auxiliar para Mostrar Flujo de Berex con Estadísticas
def mostrarFlujo(dfFlujo: pd.DataFrame, subheader: str):
    if dfFlujo.empty:
        st.warning("No hay datos de flujo para mostrar.")
        return

    # Agregamos el Subheader Dado
    st.subheader(subheader)

    # Creamos 2 Columnas: 1 Para mostrar el DataFrame y otra para Mostrar Métricas
    # Vamos a dejar la Columna del DataFrame con un Ancho Mayor para que se vea mejor, y la Columna de Métricas con un Ancho Menor
    col1, col2 = st.columns(2, gap="large", width=[3, 1], vertical_alignment='center')

    # En la Primera Columna Mostramos el DataFrame del Flujo
    with col1:
        st.dataframe(dfFlujo, use_container_width=True)

    # En la Columna 2 Mostramos Métricas Clave del Flujo
    with col2:
        # Creamos un Contenedor para que las Métricas se Muestren en Vertical distribuídas uniformemente
        with st.container(vertical_alignment='distribute'):
            totalPagado, totalMontoBerex, porcentajePagado = calcMetricasFlujo(dfFlujo)
            st.metric("Total Pagado", f"${totalPagado:,.2f}")
            st.metric("Total Monto Berex", f"${totalMontoBerex:,.2f}")
            st.metric("Porcentaje Pagado", f"{porcentajePagado:.2f}%")