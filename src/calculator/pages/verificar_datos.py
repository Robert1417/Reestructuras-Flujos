# Librerías Core
import streamlit as st

# Librerias Necesarias
import pandas as pd

from src.calculator.utils.helpers import loadData, initializeSessionState, updateSessionState

# Configuramos el Nombre de Esta Página a Calculadora
st.set_page_config(page_title="Verificar", page_icon="🤔", layout="wide")

# Primero Obtenemos los Datos
# --- Carga de Datos ---
# Cargamos los Datos de Moras y Mensualidades utilizando la Función Cargada en helpers.py
dfMoras, dfMensualidades, dfFlujoBerex = loadData() # No es Necesario Realizar Cambios porque ya usa Cache

# Actualizamos el Session State de accion_user a False para Evitar Logs Innecesarios
updateSessionState('accion_user', False)

# Inicalizamos Session State de Referencias Únicas
initializeSessionState('refs_unicas',dfMoras['Referencia'].unique().tolist())

# Agreamos un Imput de Número para Obtener la Referencia del Cliente
cliente_ref = st.sidebar.selectbox(
    "Ingrese la Referencia del Cliente",
    ['Seleccionar Referencia'] + st.session_state['refs_unicas']
)

if cliente_ref != 'Seleccionar Referencia':
    # Filtramos los Datos según la Referencia del Cliente
    dfMoras = dfMoras[dfMoras['Referencia'] == cliente_ref]
    dfMensualidades = dfMensualidades[dfMensualidades['Referencia'] == cliente_ref]
    dfFlujoBerex = dfFlujoBerex[dfFlujoBerex['Referencia'] == cliente_ref]

st.title("Página Parcial para Verificar Datos")

st.header('Datos de Moras')
st.dataframe(dfMoras)
st.divider()

st.header('Datos de Flujo')
st.dataframe(dfFlujoBerex)
st.divider()

st.header('Datos de Mensualidades')
st.dataframe(dfMensualidades)