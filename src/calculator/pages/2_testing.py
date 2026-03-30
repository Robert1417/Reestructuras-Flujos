# Librerías Core
import streamlit as st
import pandas as pd
import numpy as np

# Librerías de Ayuda
from src.calculator.utils.data_load import loadTestData, loadTestParams
from src.calculator.utils.session_state_managers import initializeSessionState, getSessionStateWithDefault, updateSessionState
from src.calculator.ui.components import mostrarFlujoBerexYMetricas, mostrarParametrosReestructura, mostrarNuevoFlujo
from src.calculator.core.flujos import FlujoTotal

# Definimos la Función Principal de Ejecución
def main():

    # --- Carga de Datos ---

    # Traemos los Datos de Prueba
    morasDF, berexDF, mensualidadesDF = loadTestData()
    # Traemos los Parámetros de Prueba
    params = loadTestParams()

    # Definimos las Referencias Únicas y las Guardamos en el Session State
    referenciasUnicas = list(morasDF['Referencia'].unique())
    initializeSessionState('referencias_unicas_test', referenciasUnicas)
    # Actualizamos el Session State de accion_user a False para Evitar Logs Innecesarios
    updateSessionState('accion_user', False)

    # --- Configuración de la Página ---
    st.set_page_config(
        page_title="Inicio Calculadora",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Configuración del Sidebar ---

    # Agregamos un Título al Sidebar
    st.sidebar.title("Parámetros de Prueba")

    # Obtenemos las Referencias Únicas del Session State
    referenciasUnicas = getSessionStateWithDefault('referencias_unicas_test', list)
    # Agregamos un Selector de Referencias al Sidebar
    referenciaSeleccionada = st.sidebar.selectbox("Selecciona una Referencia", 
                                                referenciasUnicas,
                                                )

    # Filtrado de DataFrames según la Referencia Seleccionada
    morasFiltradas = morasDF[morasDF['Referencia'] == referenciaSeleccionada]
    berexFiltrado = berexDF[berexDF['Referencia'] == referenciaSeleccionada]
    mensualidadesFiltradas = mensualidadesDF[mensualidadesDF['Referencia'] == referenciaSeleccionada]

    paramsRef = params.get(referenciaSeleccionada, {})

    # --- Vista de la Aplicación ---

    # Ponemos un Título a la Aplicación
    st.title("Inicio de Calculadora de Reestructuras")

    # Añadimos un Divisor
    st.divider()

    # Añadimos un Subtítulo
    st.subheader("Flujo de Berex y Métricas del Cliente (ANTES DE LA REESTRUCTURA)")

    # Mostramos el Flujo de Berex y las Métricas Calculadas en la Aplicación
    mostrarFlujoBerexYMetricas(morasFiltradas, berexFiltrado, mensualidadesFiltradas)

    # Añadimos un Divisor
    st.divider()

    # Mostramos los Parámetros de la Reestructura en la Aplicación
    mostrarParametrosReestructura(paramsRef)

    # Creamos un Divisor
    st.divider()

    # Creamos un Expandidor para Mostrar el Nuevo Flujo
    with st.expander("Datos Después de la Reestructura"):
        # Aquí se mostraría el nuevo flujo de berex y las métricas del cliente después de aplicar la reestructura
        mostrarNuevoFlujo(morasFiltradas, berexFiltrado, mensualidadesFiltradas, paramsRef)

if __name__ == "__main__":
    main()