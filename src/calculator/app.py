# Imports Core
import streamlit as st
import logging
import logging.config
import json

# Imports Adicionales
from src.calculator.utils.helpers import loadTestData, getSessionStateWithDefault,isSessionStateDefined, getSessionState
from src.calculator.ui.components import mostrarFlujo
from src.calculator.core import FlujoTotal

# Le agregamos las Configuraciones de src/calculator/logging/config.json
with open('src/calculator/logging/config.json', 'r') as f:
    config = json.load(f)
    logging.config.dictConfig(config)

# Definimos nuestro Logger de Debugging
debugLogger = logging.getLogger('calculator_debug')

# Configuramos el Título de la Aplicación
st.set_page_config(page_title="Inicio",page_icon='🤖', layout="wide")

# --- Carga de Datos de Prueba ---
# Primero Verificamos si ya están cargados en el Session State para evitar recargas innecesarias
if not isSessionStateDefined('mora_test') or not isSessionStateDefined('mensualidades_test') or not isSessionStateDefined('flujo_test'):
    moras, mensualidades, clientes = loadTestData()
    st.session_state['mora_test'] = moras
    st.session_state['mensualidades_test'] = mensualidades
    st.session_state['flujo_test'] = clientes
    debugLogger.debug('Datos de prueba cargados y almacenados en Session State')

# Obtenemos el flujo de prueba desde el Session State
flujo_test = getSessionState('flujo_test')
berex_test = getSessionState('mora_test')
mensualidades_test = getSessionState('mensualidades_test')

# Creamos la Función para crear el Flujo Total de Prueba
crearFlujoTotalTest = lambda: FlujoTotal(berex_test, mensualidades_test)

# --- Visualización de la Página

# Mostramos un Título Principal para la Aplicación
st.title("Bienvenido a la Calculadora de Berex")
# Ponemos un Separador para Mejorar la Visualización
st.divider()

# Mostramos el Flujo de Prueba utilizando el componente personalizado
mostrarFlujo(flujo_test,"Flujo de Prueba de Berex")

# Ponemos otro Separador para Mejorar la Visualización
st.divider()