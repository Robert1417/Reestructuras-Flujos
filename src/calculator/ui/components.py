# Datos de Componentes de la Interfaz de Usuario para el Flujo Berex

# Librearías Core
import streamlit as st

# Librerías de Manipulación de Datos
import pandas as pd

# Librerías de Utilidades
from src.calculator.utils.helpers import notInfinteLog, calcMetricasFlujo, calcCompleteFlujo

# Función Auxiliar para Mostrar los Párametros de Entrada en la Barra Lateral como Métricas
def mostrarParametrosEntrada(cliente_ref, fecha_inicio_pago, nuevo_apartado_mensual, nuevo_pago_inicial):

    st.subheader("Métricas de la Reestructura")

    # Se van a mostrar cada uno en una columna
    col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment='center')

    col1.metric("Referencia del Cliente", cliente_ref)
    col2.metric("Fecha Inicio de Pago", fecha_inicio_pago.strftime("%Y-%m-%d"))
    col3.metric("Nuevo Apartado Mensual", f"${nuevo_apartado_mensual:,.2f}")
    col4.metric("Nuevo Pago Inicial", f"${nuevo_pago_inicial:,.2f}")

# Función Auxiliar para mostrar el Pago Mínimo Inicial
def mostrarPagoMinimoInicial(mensualidadesDF):

    st.subheader("Pago Mínimo Inicial Requerido")

    if mensualidadesDF.empty:
        st.warning("No hay datos de mensualidades para calcular el pago mínimo inicial.")
        return

    # Calculamos el Pago Mínimo Inicial como la suma del Monto de las Mensualidades hasta hoy
    # Con Status_Facturacion POR_COBRAR, porque solo esas mensualidades se consideran para el pago mínimo inicial
    hoy = pd.Timestamp.now().normalize()
    mensualidadesVigentes = mensualidadesDF[(mensualidadesDF['Fecha_Facturacion'] <= hoy) & (mensualidadesDF['Status_Facturacion'] == 'POR_COBRAR')]
    pago_minimo_inicial = mensualidadesVigentes['Monto'].sum()

    # Mostramos el Pago Mínimo Inicial como una Métrica Destacada en el centro
    with st.container(horizontal_alignment='center'):
        st.metric("Pago Mínimo Inicial Requerido", f"${pago_minimo_inicial:,.2f}")

# Función Auxiliar para Comparar Métricas entre 2 Flujos
def compararMetricasFlujo(dfFlujo1: pd.DataFrame, dfFlujo2: pd.DataFrame, subheader1: str, subheader2: str):
    col1, col2 = st.columns(2, gap="large", vertical_alignment='center')

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
    col1, col2 = st.columns([5, 3], gap="large", vertical_alignment='center')

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


# Función Auxiliar para mostrar un Flujo Completo
def mostrarFlujoCompleto(flujoMoras: pd.DataFrame, flujoMensualidades: pd.DataFrame):

    # Primero calculamos el Flujo Completo utilizando la Función calcularFlujoCompleto del archivo helpers.py
    dfCompleteFlow = calcCompleteFlujo(flujoMoras, flujoMensualidades)

    # Ahora vamos a Aplicarle Estilos y Orden a las Columnas

    # 1. Aplicamos estilos para resaltar Columnas Montos basados en si esta pagado o no
    def highlight_pagado(row):
        if row['Pagado PaB']:
            return ['background-color: lightgreen' if col == 'Monto PaB' else '' for col in row.index]
        elif row['Pagado Comision']:
            return ['background-color: lightblue' if col == 'Monto Comision' else '' for col in row.index]
        elif row['Pagado Mensualidad']:
            return ['background-color: lightyellow' if col == 'Monto Mensualidad' else '' for col in row.index]
        else:
            return ['' for _ in row.index]
    
    dfCompleteFlowStyled = dfCompleteFlow.style.apply(highlight_pagado, axis=1)

    # Ahora creamo Columna de Pagado Total como la suma de Monto PaB y Monto Comision teniendo en cuenta si estan pagados
    dfCompleteFlow['Monto Total Pagado'] = (
        dfCompleteFlow['Monto PaB'] * dfCompleteFlow['Pagado PaB'].astype(int) + 
        dfCompleteFlow['Monto Comision'] * dfCompleteFlow['Pagado Comision'].astype(int) +
        dfCompleteFlow['Monto Mensualidad'] * dfCompleteFlow['Pagado Mensualidad'].astype(int)
    )

    # Volvemos las Columnas Númericas a String con Formato de Moneda para que se vean mejor
    dfCompleteFlow['Monto PaB'] = dfCompleteFlow['Monto PaB'].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    dfCompleteFlow['Monto Comision'] = dfCompleteFlow['Monto Comision'].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    dfCompleteFlow['Monto Mensualidad'] = dfCompleteFlow['Monto Mensualidad'].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")
    dfCompleteFlow['Monto Total Pagado'] = dfCompleteFlow['Monto Total Pagado'].apply(lambda x: f"${x:,.2f}" if x > 0 else "$0.00")

    # Reordenamos las Columnas para que tengan un Orden Lógico
    dfCompleteFlow = dfCompleteFlow[
        ['Fecha PaB', 'Monto PaB', 'Fecha Comision', 'Monto Comision', 'Fecha Mensualidad', 'Monto Mensualidad', 'Monto Total Pagado']
    ]

    # Agregamos un subheader
    st.subheader("Flujo Completo de Berex con Mensualidades")

    # Finalmente Mostramos el Flujo Completo con Estilos
    st.dataframe(dfCompleteFlow, use_container_width=True)