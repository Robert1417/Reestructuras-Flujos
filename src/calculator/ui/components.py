# Librerías Core
import streamlit as st
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.calculos_flujos import calcularMetricasFlujos, calcularPagoMinimoInicial
from src.calculator.utils.logger_setup import stWarningLogWrapper
from src.calculator.ui.df_styling import estilizarBerex, estilizarPagare
from src.calculator.core.flujos import FlujoTotal
from src.calculator.utils.data_load import reorganizeDataAsInPagare

# Función Auxiliar para Mostrar el Pago Mínimo en la Aplicación
@stWarningLogWrapper(message="Error al mostrar el Pago Mínimo en la Aplicación")
def mostrarPagoMinimo(mensualidades: pd.DataFrame) -> None:
    """
    Muestra el pago mínimo en la aplicación.

    Args:
        mensualidades (pd.DataFrame): DataFrame que contiene las mensualidades.
    """
    mensualidadesFaltantes, pagoMinimo = calcularPagoMinimoInicial(mensualidades)
    st.subheader("Pago Mínimo Requerido por Mensualidades Pendientes")

    if mensualidadesFaltantes == 0:
        st.success("No hay Mensualidades Pendientes, el Cliente está al Día con sus Pagos de Mensualidades")
        return

    # Vamos a Dejar la Métrica a la Izquierda y el Valor a la Derecha
    col1, col2 = st.columns([1, 2], vertical_alignment="center", gap="large")
    with col1:
        st.metric(label="Mensualidades Faltantes", value=mensualidadesFaltantes)
    with col2:
        st.metric(label="Pago Mínimo", value=f"${pagoMinimo:,.2f}")

# Función para Mostrar el Flujo de Berex y Métricas en la Aplicación
@stWarningLogWrapper(message="Error al mostrar el Flujo de Berex y Métricas en la Aplicación")
def mostrarFlujoBerexYMetricas(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame, filterToToday: bool = True, berexHeader: str = 'Flujo de Berex') -> None:
    """
    Muestra el flujo de berex y las métricas calculadas en la aplicación.

    Args:
        moras (pd.DataFrame): DataFrame que contiene las moras.
        berex (pd.DataFrame): DataFrame que contiene los datos de berex.
        mensualidades (pd.DataFrame): DataFrame que contiene las mensualidades.
        filterToToday (bool): Indica si se deben filtrar los datos hasta hoy.
        berexHeader (str): Encabezado para el flujo de berex.
    """
    # Calculamos las Métricas de los Flujos
    pagoActualCliente, valorTotalPagar, cuotasPendientes, porcentajePago, statusMora = calcularMetricasFlujos(moras, berex, mensualidades, filterToToday)

    st.header(berexHeader)
    # Mostramos los Datos de Berex
    st.dataframe(estilizarBerex(berex), width='stretch',
                column_config={
                    'Fecha_Pago_Berex': st.column_config.DateColumn(format="YYYY-MM-DD"),
                    'Monto_Berex': st.column_config.NumberColumn(format="$%,.0f"),
                    'Saldo_Pendiente': st.column_config.NumberColumn(format="$%,.0f")
                })


    st.header("Métricas del Cliente", text_alignment="center")
    # Creamos 5 Columnas
    cols = st.columns(2, vertical_alignment="center", gap="medium")
    cols[0].metric(label="Pago Actual del Cliente", value=f"${pagoActualCliente:,.2f}",delta=f"${valorTotalPagar - pagoActualCliente:,.2f}", delta_color="red" if valorTotalPagar - pagoActualCliente > 0 else "green")
    cols[0].metric(label="Valor Total a Pagar por el Cliente",value=f"${valorTotalPagar:,.2f}")
    cols[0].metric(label="Cuotas Pendientes por Pagar",
            value=cuotasPendientes,
            delta_color="red" if cuotasPendientes > 0 else "green",
            delta=f"{cuotasPendientes} Cuotas Pendientes" if cuotasPendientes > 0 else "No hay Cuotas Pendientes")
    cols[1].metric(label="Porcentaje de Pago del Cliente", value=f"{porcentajePago:.2f}%", delta=f"{porcentajePago:.2f}%", delta_color="green" if porcentajePago >= 100 else "red")
    cols[1].metric(label="Status de Mora del Cliente",
            value=statusMora,
            delta_color="green" if statusMora.lower() == "al día" else "red",
            delta="Al día" if statusMora.lower() == "al día" else "En Mora")

# Función Auxiliar para Mostrar el Pagaré en la Aplicación
@stWarningLogWrapper(message="Error al mostrar el Pagaré en la Aplicación")
def mostrarPagare(pagare: pd.DataFrame, subheader: str = "Pagaré") -> None:
    """
    Muestra el pagaré en la aplicación.

    Args:
        pagare (pd.DataFrame): DataFrame que contiene los datos del pagaré.
    """
    st.subheader(subheader)
    st.dataframe(estilizarPagare(pagare), width='stretch')

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
            if isinstance(valor, (int, float)):
                st.metric(label=parametro, value=f"${valor:,.2f}")
            elif isinstance(valor, pd.Timestamp):
                st.metric(label=parametro, value=valor.strftime("%Y-%m-%d"))
            else:
                st.metric(label=parametro, value=valor)

# Función Auxiliar para Mostrar el Nuevo Flujo después de la Reestructura
@stWarningLogWrapper(message="Error al mostrar el Nuevo Flujo después de la Reestructura")
def mostrarNuevoFlujo(moras, berex, mensualidades, params):
    # Obtenemos la Referencia del Cliente
    referencia = moras['Referencia'].iloc[0]
    # Primero Creamos el FlujoTotal
    flujoTotal = FlujoTotal(referencia,moras, berex, mensualidades)
    # Aplicamos la Reestructura al FlujoTotal
    nuevoBerex = flujoTotal.calcularNuevoFlujoBerex(params)

    # Verificamos si el Nuevo Flujo de Berex se ha Calculado Correctamente
    if flujoTotal.isNuevoFlujoCalculated():
        st.success("El Nuevo Flujo de Berex se ha Calculado Correctamente, Deslizar para Ver")
    else:
        # Obtenemos el Motivo del Error
        errorMessage = flujoTotal.getErrorMessage()
        st.error("Error al Calcular el Nuevo Flujo de Berex después de la Reestructura: ")
        st.markdown(f"<span style='color:red;font-weight:bold;'>{errorMessage}</span>", unsafe_allow_html=True)
        return # Para Evitar que se Intente Mostrar un Flujo de Berex que no se ha Calculado Correctamente
    
    # mostrarParametrosReestructura(params) # Ya incluye el Subheader

    # Creamos 2 Tabs para realizar Comparación entre el Flujo de Berex Actual y el Nuevo Flujo de Berex después de la Reestructura
    tab1, tab2 = st.tabs(["Flujo de Berex Actual", "Nuevo Flujo de Berex Después de la Reestructura"])
    with tab1:
        mostrarFlujoBerexYMetricas(moras, berex, mensualidades, filterToToday=False, berexHeader='Flujo Antiguo del Cliente')
    with tab2:
        mostrarFlujoBerexYMetricas(moras, nuevoBerex, mensualidades, filterToToday=False, berexHeader='Nuevo Flujo Después de la Reestructura') # No Filtramos a Hoy para Mostrar el Flujo Completo después de la Reestructura

    # Agregamos un Divisor
    st.divider()

    # Añadimos Subheader para Comparación de Pagarés
    st.subheader("Comparación de Pagarés")
    mostrarPagare(reorganizeDataAsInPagare(moras, berex, mensualidades), subheader="Pagaré Actual")
    mostrarPagare(reorganizeDataAsInPagare(moras, nuevoBerex, mensualidades), subheader="Nuevo Pagaré Después de la Reestructura")

    # Agregamos un Divisor
    st.divider()

    # Agregamos Subheader para mostrar la Viabilidad de la Reestructura
    st.subheader("Viabilidad de la Reestructura")
    if flujoTotal.isNuevoFlujoViable():
        st.success("La Reestructura es Viable para el Cliente")
    else:
        st.error("La Reestructura No es Viable para el Cliente")
        # Obtenemos el Motivo de No Viabilidad
        motivoNoViable = flujoTotal.getErrorMessage()
        st.markdown(f"<span style='color:red;font-weight:bold;'>{motivoNoViable}</span>", unsafe_allow_html=True)