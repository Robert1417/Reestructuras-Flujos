# Librerías Core
import streamlit as st

# Librerias Necesarias
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.helpers import updateSessionState,areSessionStatesValid

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

# Agreamos un Imput de Número para Obtener la Referencia del Cliente
cliente_ref = st.sidebar.number_input(
    "Ingrese la Referencia del Cliente",
    min_value=0,
    step=1,
    value=0,
    )

# Actualizamos el Session State con la Referencia del Cliente
updateSessionState('cliente_ref', cliente_ref)

# Creamos un Input de Fecha para Obtener la Fecha Inicial de Pago
fecha_inicio_pago = st.sidebar.date_input(
    "Ingrese la Fecha Inicial de Pago",
    value=pd.to_datetime('today').date()
    )

# Actualizamos el Session State con la Fecha Inicial de Pago
updateSessionState('fecha_inicio_pago', fecha_inicio_pago)

# Creamos el Input de Nuevo Apartado Mensual para Obtener el Nuevo Monto Mensual
nuevo_apartado_mensual = st.sidebar.number_input(
    "Ingrese el Nuevo Apartado Mensual",
    min_value=0.0,
    step=100.0,
    value=0.0,
    )

# Actualizamos el Session State con el Nuevo Apartado Mensual
updateSessionState('nuevo_apartado_mensual', nuevo_apartado_mensual)

# Creamos un Input de Nuevo Pago Inicial para Obtener el Nuevo Monto de Pago Inicial
nuevo_pago_inicial = st.sidebar.number_input(
    "Ingrese el Nuevo Pago Inicial",
    min_value=0.0,
    step=100.0,
    value=0.0,
    )

# Actualizamos el Session State con el Nuevo Pago Inicial
updateSessionState('nuevo_pago_inicial', nuevo_pago_inicial)

# --- Configuración de la Página Principal ---
# Agregamos un Título a la Página Principal
st.title("Calculadora de Reestructuras")

# Vamos a Mostrar el Antiguo Flujo de Berex del Cliente
st.header("Flujo Actual de Berex")

# Añadimos un Divisor
st.divider()

# Definimos si el Flujo ya esta calculado
flujo_calculado = areSessionStatesValid(['cliente_ref','fecha_inicio_pago','nuevo_apartado_mensual','nuevo_pago_inicial'])

if flujo_calculado:
    st.success("Flujo calculado correctamente. Desplázate hacia abajo para ver el nuevo flujo con la reestructura.")
    # Agregamos otro Título de Nuevo Flujo Calculado
    st.header("Nuevo Flujo Calculado con Reestructura")
else:
    st.warning("Por favor, completa todos los campos en el sidebar para calcular el flujo.")

# Actualizamos de nuevo el Session State de accion_user a False
# Esto se realiza para que solo en los frames que existe una acción se muestren los logs
updateSessionState('accion_user', False)