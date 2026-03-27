# Imports Core
import streamlit as st
import json
import pandas as pd

# Imports Adicionales
from src.calculator.utils.helpers import loadTestData, getSessionStateWithDefault,isSessionStateDefined, getSessionState
from src.calculator.ui.components import mostrarFlujo, mostrarParametrosEntrada, compararMetricasFlujo
from src.calculator.core import FlujoTotal

# Configuramos el Título de la Aplicación
st.set_page_config(page_title="Inicio",page_icon='🤖', layout="wide")

# --- Carga de Datos de Prueba ---
# No es Necesario Realizar Cambios en la Carga de Datos de Prueba porque ya usa Cache, pero lo dejamos aquí para Mejorar la Visualización del Código
moras, mensualidades, flujo = loadTestData()

# Ahora Cargamos los Datos de Configuracion de los Clientes Test
with open('data/tests/parametros.json', 'r') as f:
    clientesConfig = json.load(f)

# --- Agregación de Datos de Sidebar

# Agregamos un Control de Referencias únicas en la barra lateral
uniqueRefs = moras['Referencia'].unique().tolist()
cliente_ref = st.sidebar.selectbox("Selecciona la Referencia del Cliente", uniqueRefs,
                                    index=0, help="Selecciona la Referencia del Cliente para mostrar sus datos y métricas asociadas.")

# Creamos los DFs filtrados por esa referencia
moraCliente = moras[moras['Referencia'] == cliente_ref]
mensualidadCliente = mensualidades[mensualidades['Referencia'] == cliente_ref]
flujoCliente = flujo[flujo['Referencia'] == cliente_ref]

# Dejamos las Configuraciones del Cliente 
clientConfigs = clientesConfig.get(cliente_ref, {})

# Volvemos fecha_inicio_pago un datetime para mostrarlo como métrica
fecha_inicio_pago = pd.to_datetime(clientConfigs.get('fecha_inicio_pago', pd.Timestamp.now()), errors='coerce')
# Volvemos los otros parámetros numéricos para mostrarlos como métricas
nuevo_apartado_mensual = float(clientConfigs.get('nuevo_apartado_mensual', 0))
nuevo_pago_inicial = float(clientConfigs.get('nuevo_pago_inicial', 0))

# --- Visualización de la Página

# Mostramos un Título Principal para la Aplicación
st.title("Bienvenido a la Calculadora de Berex")
# Ponemos un Separador para Mejorar la Visualización
st.divider()

# Mostramos el Flujo de Prueba utilizando el componente personalizado
mostrarFlujo(flujoCliente,"Flujo de Prueba de Berex")

# Ponemos otro Separador para Mejorar la Visualización
st.divider()

# Mostramos los Parámetros de Entrada del Cliente utilizando el componente personalizado
mostrarParametrosEntrada(cliente_ref, fecha_inicio_pago, nuevo_apartado_mensual, nuevo_pago_inicial)

# Ponemos otro Separador para Mejorar la Visualización
st.divider()