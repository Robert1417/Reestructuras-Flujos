# Librerías Core
import streamlit as st

# Librerias Necesarias
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.session_state_managers import updateSessionState, initializeSessionState, areSessionStatesValid, initializeRequiredSessionStates
from src.calculator.utils.data_load import loadData
from src.calculator.utils.logger_setup import notInfiniteLog
from src.calculator.ui.components import mostrarFlujoBerexYMetricas, mostrarParametrosReestructura, mostrarNuevoFlujo

# Definimos la Ejecución Inicial de la Aplicación
def main():

    # --- Carga de Datos ---
    # Actualizamos el Session State de accion_user a False para Evitar Logs Innecesarios
    updateSessionState('accion_user', False)

    # --- Carga de Datos ---
    # Cargamos los Datos de Moras y Mensualidades utilizando la Función Cargada en helpers.py
    dfMoras, dfFlujoBerex, dfMensualidades = loadData() # No es Necesario Realizar Cambios porque ya usa Cache

    # Inicalizamos Session State de Referencias Únicas
    initializeSessionState('refs_unicas',dfMoras['Referencia'].unique().tolist())

    # --- Configuración de SideBar ---
    # Agregamos Título del SideBar
    st.sidebar.title("Calculadora de Reestructuras")

    # Creamos Variable de anyChange para Detectar Cambios en los Inputs
    anyChange = False

    # Agreamos un Imput de Número para Obtener la Referencia del Cliente
    cliente_ref = st.sidebar.selectbox(
        "Ingrese la Referencia del Cliente",
        ['Seleccionar Referencia'] + st.session_state['refs_unicas'],
        )

    # Actualizamos el Session State con la Referencia del Cliente
    anyChange = anyChange or updateSessionState('cliente_ref', cliente_ref)

    # Creamos un Input de Fecha para Obtener la Fecha Inicial de Pago
    fecha_inicio_pago = pd.Timestamp(st.sidebar.date_input(
        "Ingrese la Fecha Inicial de Pago",
        value=pd.Timestamp.now().date(),
        )
    )
    # Actualizamos el Session State con la Fecha Inicial de Pago
    anyChange = anyChange or updateSessionState('fecha_inicio_pago', fecha_inicio_pago)

    # Creamos el Input de Nuevo Apartado Mensual para Obtener el Nuevo Monto Mensual
    nuevo_apartado_mensual = st.sidebar.number_input(
        "Ingrese el Nuevo Apartado Mensual",
        min_value=0,
        step=100,
        value=1000,
        )

    # Actualizamos el Session State con el Nuevo Apartado Mensual
    anyChange = anyChange or updateSessionState('nuevo_apartado_mensual', nuevo_apartado_mensual)

    # Creamos un Input de Nuevo Pago Inicial para Obtener el Nuevo Monto de Pago Inicial
    nuevo_pago_inicial = st.sidebar.number_input(
        "Ingrese el Nuevo Pago Inicial",
        min_value=0,
        step=100,
        value=1000,
        )

    # Actualizamos el Session State con el Nuevo Pago Inicial
    anyChange = anyChange or updateSessionState('nuevo_pago_inicial', nuevo_pago_inicial)

    # Por Último cambiamos el Session State de accion_user a True si hubo algún cambio en los inputs
    if anyChange:
        updateSessionState('accion_user', True)

    # Ahora Creamos el Diccionario de Párametros de la Reestructura con los Valores del Session State
    params = {
        "Nuevo_Apartado_Mensual": st.session_state['nuevo_apartado_mensual'],
        "Monto_Inicial_Reestructura": st.session_state['nuevo_pago_inicial'],
        "Fecha_Inicio_Reestructura": st.session_state['fecha_inicio_pago'],
    }

    # Filtramos los Datos según la Referencia del Cliente
    dfMoras = dfMoras[dfMoras['Referencia'] == cliente_ref]
    dfMensualidades = dfMensualidades[dfMensualidades['Referencia'] == cliente_ref]
    dfFlujoBerex = dfFlujoBerex[dfFlujoBerex['Referencia'] == cliente_ref]

    # --- Configuración de la Página Principal ---
    # Agregamos un Título a la Página Principal
    st.title("Calculadora de Reestructuras")

    # Verificamos que dfMoras y dfFlujoBerex no estén vacíos antes de Mostrar el Flujo de Berex y las Métricas
    if not dfMoras.empty and not dfFlujoBerex.empty:
        # Mostramos el Flujo de Berex y las Métricas Calculadas en la Aplicación
        mostrarFlujoBerexYMetricas(dfMoras, dfFlujoBerex, dfMensualidades)

        # Añadimos un Divisor
        st.divider()

        # Mostramos los Parámetros de la Reestructura en la Aplicación
        mostrarParametrosReestructura(params)

        # Añadimos un Divisor
        st.divider()

        # Verificamos que los Session States necesarios para el Cálculo del Nuevo Flujo estén definidos y sean válidos
        if areSessionStatesValid(['cliente_ref', 'nuevo_apartado_mensual', 'nuevo_pago_inicial', 'fecha_inicio_pago']):
            # Mostramos el Nuevo Flujo Calculado con los Parámetros de la Reestructura
            mostrarNuevoFlujo(dfMoras, dfFlujoBerex, dfMensualidades, params)
        else:
            st.warning("Algunos Parámetros estan sin Definir, por favor Definir dichos parámetros para Mostrar el Nuevo Flujo Calculado.")

    else:
        if cliente_ref != 'Seleccionar Referencia':
            st.warning("No se encontraron datos de Moras o Flujo de Berex para la Referencia del Cliente seleccionada. Por favor, seleccione una referencia válida.")
        else:
            st.info("Por favor, seleccione una Referencia de Cliente para Mostrar el Flujo de Berex, las Métricas y el Nuevo Flujo Calculado.")

    # Actualizamos de nuevo el Session State de accion_user a False
    # Esto se realiza para que solo en los frames que existe una acción se muestren los logs
    updateSessionState('accion_user', False)

if __name__ == "__main__":
    notInfiniteLog('user_enter_calculadora', 'La página de la calculadora ha sido abierta por el usuario') # Logueamos la Primera Ejecución de la Página Principal de la Calculadora
    initializeRequiredSessionStates()
    main()