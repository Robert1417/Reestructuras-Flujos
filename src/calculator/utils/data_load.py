# Librerías Core
import streamlit as st
import pandas as pd
import json

# Librerías de Typing
from typing import Tuple

# Librerías de Ayuda
from src.calculator.utils.session_state_managers import updateSessionState
from src.calculator.utils.logger_setup import logWrapper, notInfinteLog

# Definimos las Columnas Existentes en Cada uno de los DFs
columnasMoras = ['Referencia','Fecha','Fecha_Origen','Por_Cobrar','Pago','Status_Mora']
columnasBerex = ['Referencia','Fecha_Pago_Berex','Monto_Berex','Destino']
columnasMensualidades = ['Referencia','Status_Facturacion','Status_Reparadora','Fecha_Cobro','Monto_Mensualidad']

# Definimos Dfs vacios ante algún error
emptyMoras = pd.DataFrame(columns=columnasMoras)
emptyBerex = pd.DataFrame(columns=columnasBerex)
emptyMensualidades = pd.DataFrame(columns=columnasMensualidades)

# --- Funciones Auxiliares de Limpieza e Imputación ---

# Función Auxiliar para Limpiar las Referencias
def cleanReferencia(ref) -> str:
    return str(ref).replace('.0','').strip()

# Función Auxiliar para imputar NaNs
def imputeNans(df: pd.DataFrame, col: str, value) -> None:
    # Se define la mascara de valores nulos
    mask = df[col].isna()
    # A los valores nulos se aplica el valor
    df.loc[mask, col] = value

# --- Limpieza de Datos ---

# Función Auxiliar para limpiar los Datos de Moras
@logWrapper(message='Error al limpiar los datos de moras', onErrorValue=emptyMoras)
def cleanMoras(dfMoras: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfMoras = dfMoras[columnasMoras].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfMoras['Referencia'] = dfMoras['Referencia'].apply(cleanReferencia)
    # Volvemos las Columnas Pago y Por Cobrar a Númerico
    dfMoras['Pago'] = pd.to_numeric(dfMoras['Pago'], errors='coerce')
    dfMoras['Por_Cobrar'] = pd.to_numeric(dfMoras['Por_Cobrar'], errors='coerce')
    # Imputamos los NaNs de Pago y Por Cobrar con 0
    imputeNans(dfMoras, 'Pago', 0)
    imputeNans(dfMoras, 'Por_Cobrar', 0)
    # Volvemos la Columna Fecha a Datetime
    dfMoras['Fecha'] = pd.to_datetime(dfMoras['Fecha'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha
    dfMoras = dfMoras.sort_values(by=['Referencia', 'Fecha']).reset_index(drop=True)
    # Devolvemos el DF Limpio
    notInfinteLog('cleaned_moras', 'Datos de moras limpiados correctamente', method='debug')
    return dfMoras

# Función Auxiliar para limpiar el Flujo de Berex
@logWrapper(message='Error al limpiar los datos del flujo de Berex', onErrorValue=emptyBerex)
def cleanFlujoBerex(dfFlujo: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfFlujo = dfFlujo[columnasBerex].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfFlujo['Referencia'] = dfFlujo['Referencia'].apply(cleanReferencia)
    # Volvemos la Columna Monto_Berex a Númerico
    dfFlujo['Monto_Berex'] = pd.to_numeric(dfFlujo['Monto_Berex'], errors='coerce')
    # Imputamos los NaNs de Monto_Berex con 0
    imputeNans(dfFlujo, 'Monto_Berex', 0)
    # Volvemos la Columna Fecha_Pago_Berex a Datetime
    dfFlujo['Fecha_Pago_Berex'] = pd.to_datetime(dfFlujo['Fecha_Pago_Berex'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha_Pago_Berex
    dfFlujo = dfFlujo.sort_values(by=['Referencia', 'Fecha_Pago_Berex']).reset_index(drop=True)
    # Devolvemos el DF Limpio
    notInfinteLog('cleaned_flujo_berex', 'Datos del flujo de Berex limpiados correctamente', method='debug')
    return dfFlujo

# Función Auxiliar para limpiar los Datos de Mensualidades
@logWrapper(message='Error al limpiar los datos de mensualidades', onErrorValue=emptyMensualidades)
def cleanMensualidades(dfMensualidades: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfMensualidades = dfMensualidades[columnasMensualidades].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfMensualidades['Referencia'] = dfMensualidades['Referencia'].apply(cleanReferencia)
    # Volvemos la Columna Monto_Mensualidad a Númerico
    dfMensualidades['Monto_Mensualidad'] = pd.to_numeric(dfMensualidades['Monto_Mensualidad'], errors='coerce')
    # Imputamos los NaNs de Monto_Mensualidad con 0
    imputeNans(dfMensualidades, 'Monto_Mensualidad', 0)
    # Volvemos la Columna Fecha_Cobro a Datetime
    dfMensualidades['Fecha_Cobro'] = pd.to_datetime(dfMensualidades['Fecha_Cobro'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha_Cobro
    dfMensualidades = dfMensualidades.sort_values(by=['Referencia', 'Fecha_Cobro']).reset_index(drop=True)
    # Devolvemos el DF Limpio
    notInfinteLog('cleaned_mensualidades', 'Datos de mensualidades limpiados correctamente', method='debug')
    return dfMensualidades

# --- Carga General de Datos ---

# Función Auxiliar para Cargar los Datos guardados localmente
# Los Datos que carga son: moras.parquet, cartera.parquet y mensualidades.parquet
@st.cache_data(show_spinner=False)
def loadData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos los Datos
        moras = pd.read_parquet('data/moras.parquet')
        berex = pd.read_parquet('data/cartera.parquet')
        mensualidades = pd.read_parquet('data/mensualidades.parquet')
        notInfinteLog('loaded_data', 'Datos cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        berex = cleanFlujoBerex(berex)
        mensualidades = cleanMensualidades(mensualidades)
        return moras, berex, mensualidades
    except Exception as e:
        notInfinteLog('error_loading_data', f'Error al cargar los datos: {e}', method='error')
        return emptyMoras, emptyBerex, emptyMensualidades

# Función Auxiliar para cargar los datos de prueba de la calculadora
@st.cache_data(show_spinner=False)
def loadTestData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos Datos de Moras y Mensualidades
        moras = pd.read_parquet('data/tests/test_berex.parquet')
        berex = pd.read_parquet('data/tests/test_cartera.parquet')
        mensualidades = pd.read_parquet('data/tests/test_mensualidades.parquet')
        notInfinteLog('loaded_test_data', 'Datos de prueba cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        berex = cleanFlujoBerex(berex)
        return moras, berex, mensualidades
    except Exception as e:
        notInfinteLog('error_loading_test_data', f'Error al cargar los datos de prueba: {e}', method='error')
        return emptyMoras, emptyBerex, emptyMensualidades

# Función Auxiliar para cargar los Parametros de Prueba
@st.cache_data(show_spinner=False)
def loadTestParams() -> dict:
    try:
        # Cargamos los Parámetros de Prueba
        with open('data/tests/test_params.json', 'r') as f:
            params = json.load(f)
        notInfinteLog('loaded_test_params', 'Parámetros de prueba cargados correctamente', method='debug')
        return params
    except Exception as e:
        notInfinteLog('error_loading_test_params', f'Error al cargar los parámetros de prueba: {e}', method='error')
        return {}

# --- Filtrado de Datos ---

# Función Auxiliar para filtrar los DFs con Datos a Día de Hoy
@logWrapper(message='Error al filtrar los datos a día de hoy', onErrorValue=(emptyMoras, emptyBerex, emptyMensualidades))
def filterDataToToday(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Obtenemos la Fecha de Hoy
    today = pd.to_datetime('today').normalize()
    # Filtramos los DFs para quedarnos solo con los Datos a Día de Hoy o Anteriores
    moras = moras[moras['Fecha'] <= today]
    berex = berex[berex['Fecha_Pago_Berex'] <= today]
    # El Filtro por Mensualides es Diferente, ya que se toman menores o iguales a este mes
    # Se realiza el replace por si el día de hoy es el último día del mes, para que tome los datos de este mes completo
    today_month_end = today.replace(day=1) + pd.offsets.MonthEnd(0)
    mensualidades = mensualidades[mensualidades['Fecha_Cobro'] <= today]
    notInfinteLog('filtered_data_to_today', 'Datos filtrados a día de hoy correctamente', method='debug')
    return moras, berex, mensualidades

# Función Auxiliar para filtrar las Mensualidades presentes en el flujo Original de Berex, es decir, solo las mensualidades que no sobrepasenFecha_Pago_Berex.max()
@logWrapper(message='Error al filtrar las mensualidades presentes en el flujo original de Berex', onErrorValue=emptyMensualidades)
def filterMensualidadesToOriginalBerex(mensualidades: pd.DataFrame, berex: pd.DataFrame) -> pd.DataFrame:
    # Obtenemos la Fecha_Pago_Berex máxima del flujo de Berex
    max_fecha_pago_berex = berex['Fecha_Pago_Berex'].max()
    # Ahora Dejamos max_fecha_pago como el dia del siguiente mes
    max_fecha_pago_berex = max_fecha_pago_berex.replace(day=1) + pd.offsets.MonthBegin(0)
    # Filtramos las Mensualidades para quedarnos solo con las que tengan Fecha_Cobro menor a la Fecha_Pago_Berex máxima
    mensualidades_filtradas = mensualidades[mensualidades['Fecha_Cobro'] < max_fecha_pago_berex]
    notInfinteLog('filtered_mensualidades_to_original_berex', 'Mensualidades filtradas al flujo original de Berex correctamente', method='debug')
    return mensualidades_filtradas

# Función Auxiliar para Filtrar Datos de un Mes dado el Timestamp
@logWrapper(message='Error al filtrar los datos por mes', onErrorValue=emptyMensualidades)
def filterDataByMonth(df: pd.DataFrame, dateColumn: str, month: pd.Timestamp) -> pd.DataFrame:
    # Filtramos los DFs para quedarnos solo con los Datos del Mes dado
    df = df[(df[dateColumn].dt.year == month.year) & (df[dateColumn].dt.month == month.month)]
    notInfinteLog('filtered_data_by_month', f'Datos filtrados por mes: {month.strftime("%Y-%m")}', method='debug')
    return df