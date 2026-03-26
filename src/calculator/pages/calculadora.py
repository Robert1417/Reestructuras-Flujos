# Librerías Core
import streamlit as st

# Librerias Necesarias
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.helpers import updateSessionState,areSessionStatesValid, loadData, getSessionState
from src.calculator.ui.components import mostrarParametrosEntrada, mostrarFlujo, compararMetricasFlujo
from src.calculator.core import FlujoTotal

# Importamos el Logger
from src.calculator.app import debugLogger

# Configuramos el Nombre de Esta Página a Calculadora
st.set_page_config(page_title="Calculadora", page_icon=":calculator:", layout="wide")

# --- Carga de Datos ---
# Actualizamos el Session State de accion_user a False para Evitar Logs Innecesarios
updateSessionState('accion_user', False)


# --- Configuración de SideBar ---
# Agregamos Título del SideBar
st.sidebar.title("Calculadora de Reestructuras")

# Creamos Variable de anyChange para Detectar Cambios en los Inputs
anyChange = False

# Agreamos un Imput de Número para Obtener la Referencia del Cliente
cliente_ref = st.sidebar.number_input(
    "Ingrese la Referencia del Cliente",
    min_value=0,
    step=1,
    value=0,
    )

# Actualizamos el Session State con la Referencia del Cliente
anyChange = anyChange or updateSessionState('cliente_ref', cliente_ref)

# Creamos un Input de Fecha para Obtener la Fecha Inicial de Pago
fecha_inicio_pago = st.sidebar.date_input(
    "Ingrese la Fecha Inicial de Pago",
    value=pd.to_datetime('today').date()
    )

# Actualizamos el Session State con la Fecha Inicial de Pago
anyChange = anyChange or updateSessionState('fecha_inicio_pago', fecha_inicio_pago)

# Creamos el Input de Nuevo Apartado Mensual para Obtener el Nuevo Monto Mensual
nuevo_apartado_mensual = st.sidebar.number_input(
    "Ingrese el Nuevo Apartado Mensual",
    min_value=0.0,
    step=100.0,
    value=0.0,
    )

# Actualizamos el Session State con el Nuevo Apartado Mensual
anyChange = anyChange or updateSessionState('nuevo_apartado_mensual', nuevo_apartado_mensual)

# Creamos un Input de Nuevo Pago Inicial para Obtener el Nuevo Monto de Pago Inicial
nuevo_pago_inicial = st.sidebar.number_input(
    "Ingrese el Nuevo Pago Inicial",
    min_value=0.0,
    step=100.0,
    value=0.0,
    )

# Actualizamos el Session State con el Nuevo Pago Inicial
anyChange = anyChange or updateSessionState('nuevo_pago_inicial', nuevo_pago_inicial)

# Por Último cambiamos el Session State de accion_user a True si hubo algún cambio en los inputs
if anyChange:
    updateSessionState('accion_user', True)

# --- Carga de Datos ---
# Cargamos los Datos de Moras y Mensualidades utilizando la Función Cargada en helpers.py
dfMoras, dfMensualidades, dfFlujoBerex = loadData() # No es Necesario Realizar Cambios porque ya usa Cache

# Filtramos los Datos según la Referencia del Cliente
dfMoras = dfMoras[dfMoras['cliente_ref'] == cliente_ref]
dfMensualidades = dfMensualidades[dfMensualidades['cliente_ref'] == cliente_ref]
dfFlujoBerex = dfFlujoBerex[dfFlujoBerex['cliente_ref'] == cliente_ref]

# Creamos el Flujo Total si dfMoras tiene datos
if not dfMoras.empty:
    flujo_total = FlujoTotal(dfMoras, dfMensualidades)
else:
    flujo_total = None
    # Mostramos una Advertencia si no hay datos de mora para el cliente
    st.warning("No se encontraron datos de mora para la referencia del cliente ingresada. Por favor, verifica la referencia e intenta nuevamente.")


# --- Configuración de la Página Principal ---
# Agregamos un Título a la Página Principal
st.title("Calculadora de Reestructuras")

# Vamos a Mostrar el Antiguo Flujo de Berex del Cliente
st.header("Flujo Actual de Berex")

# Mostramos los Parámetros de Entrada como Métricas en la Barra Lateral
mostrarParametrosEntrada(cliente_ref, fecha_inicio_pago, nuevo_apartado_mensual, nuevo_pago_inicial)

# Añadimos un Divisor
st.divider()

# Definimos si el Flujo ya esta calculado
flujo_calculado = areSessionStatesValid(['cliente_ref','fecha_inicio_pago','nuevo_apartado_mensual','nuevo_pago_inicial'])

if flujo_calculado and getSessionState('accion_user'):
    st.success("Flujo calculado correctamente. Desplázate hacia abajo para ver el nuevo flujo con la reestructura.")
    # Agregamos otro Título de Nuevo Flujo Calculado
    st.header("Nuevo Flujo Calculado con Reestructura")
    # Agregamos un Divisor
    st.divider()

    # Agregamos un Spinner para mostrar que se está calculando el nuevo flujo
    with st.spinner("Calculando el nuevo flujo con la reestructura..."):
        # Calculamos el Nuevo Flujo con la Reestructura utilizando la Función de FlujoTotal
        dfNuevoFlujo, alertarPaB = flujo_total.calcularNuevoFlujo(
            fecha_inicio_pago=fecha_inicio_pago,
            nuevo_apartado_mensual=nuevo_apartado_mensual,
            nuevo_pago_inicial=nuevo_pago_inicial
        )

    # Verificamos si el nuevo flujo no es vacío antes de mostrarlo, y si se debe alertar sobre el Pago a Banco (PaB)
    if dfNuevoFlujo.empty:
        st.warning("El nuevo flujo calculado está vacío. Por favor, verifica los parámetros de entrada.")
    else:
        # Ponemos la Alerta de PaB en un Warning para que se vea más claro
        if alertarPaB:
            st.sidebar.warning("⚠️ El nuevo flujo calculado tiene un Pago a Banco (PaB) por cumplir.")

        # Ahora mostramos el Nuevo Flujo Calculado utilizando la Función mostrarFlujo del archivo components.py
        mostrarFlujo(dfNuevoFlujo, "Nuevo Flujo de Berex con Reestructura")

        # Agregamos otro Divisor
        st.divider()

        # Ahora Creamos 2 Columnas para Mostrar el Flujo Antiguo y el Nuevo Flujo lado a lado
        col1, col2 = st.columns(2, gap="large", width=[1, 1], vertical_alignment='top')
        with col1:
            mostrarFlujo(dfFlujoBerex, "Flujo Actual de Berex")
        with col2:
            mostrarFlujo(dfNuevoFlujo, "Nuevo Flujo de Berex con Reestructura")
        
        # Agregamos otro Divisor
        st.divider()

        # Comparamos las Métricas Clave entre el Flujo Actual y el Nuevo Flujo utilizando la Función compararMetricasFlujo del archivo components.py
        compararMetricasFlujo(dfFlujoBerex, dfNuevoFlujo, "Métricas del Flujo Actual de Berex", "Métricas del Nuevo Flujo con Reestructura")

else:
    st.warning("Por favor, completa todos los campos con valores válidos en el sidebar para calcular el flujo.")

# Actualizamos de nuevo el Session State de accion_user a False
# Esto se realiza para que solo en los frames que existe una acción se muestren los logs
updateSessionState('accion_user', False)