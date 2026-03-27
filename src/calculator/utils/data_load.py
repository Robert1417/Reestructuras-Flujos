# Librerías Core
import streamlit as st
import pandas as pd

# Librerías de Typing
from typing import Tuple

# Librerías de Ayuda
from src.calculator.utils.session_state_managers import updateSessionState
from src.calculator.utils.logger_setup import notInfinteLog


def cleanReferencia(ref) -> str:
    return str(ref).replace('.0','').strip()

# Función Auxiliar para imputar NaNs
def imputeNans(df: pd.DataFrame, col: str, value) -> None:
    # Se define la mascara de valores nulos
    mask = df[col].isna()
    # A los valores nulos se aplica el valor
    df.loc[mask, col] = value

# Función Auxiliar para limpiar los Datos de Moras
def cleanMoras(dfMoras: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos los Datos de Moras para Asegurar que estén en el Formato Correcto
    try:
        dfMoras['Fecha_Pago_Berex'] = pd.to_datetime(dfMoras['Fecha_Pago_Berex'])
        dfMoras['amount'] = dfMoras['amount'].astype(float)
        dfMoras['Referencia'] = dfMoras['Referencia'].apply(cleanReferencia)
        dfMoras['Pago'] = dfMoras['Pago'].astype(float)
        dfMoras.rename(columns={'amount': 'Monto_Berex', 'destination': 'Destino'}, inplace=True)
        # Imputamos NaNs en la columna de Pago con el valor de 0.0
        imputeNans(dfMoras, 'Pago', 0.0)
        notInfinteLog('cleaned_moras', 'Datos de moras limpiados correctamente', method='debug')
        return dfMoras
    except Exception as e:
        notInfinteLog('error_cleaning_moras', f'Error al limpiar los datos de moras: {e}', method='error')
        raise e

# Función Auxiliar para limpiar el Flujo de Berex
def cleanFlujoBerex(dfFlujo: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos los Datos del Flujo de Berex para Asegurar que estén en el Formato Correcto
    try:
        dfFlujo['Fecha_Pago_Berex'] = pd.to_datetime(dfFlujo['Fecha_Pago_Berex'])
        dfFlujo['Monto_Berex'] = dfFlujo['Monto_Berex'].astype(float)
        dfFlujo['Pago'] = dfFlujo['Pago'].astype(float)
        # Se dejan solo Columnas de: Referencia, Fecha_Origen, Fecha_Pago_Berex, Monto_Berex,Destino
        dfFlujo = dfFlujo[['Referencia', 'Fecha_Origen', 'Fecha_Pago_Berex', 'Monto_Berex', 'Destino','Pago']].copy()
        notInfinteLog('cleaned_flujo_berex', 'Datos del flujo de Berex limpiados correctamente', method='debug')
        return dfFlujo
    except Exception as e:
        notInfinteLog('error_cleaning_flujo_berex', f'Error al limpiar los datos del flujo de Berex: {e}', method='error')
        raise e

# Función Auxiliar para limpiar los Datos de Mensualidades
def cleanMensualidades(dfMensualidades: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos los Datos de Mensualidades para Asegurar que estén en el Formato Correcto
    try:
        dfMensualidades['Fecha_Cobro'] = pd.to_datetime(dfMensualidades['Fecha_Cobro'])
        dfMensualidades['Monto'] = dfMensualidades['Monto'].astype(float)
        dfMensualidades['Referencia'] = dfMensualidades['Referencia'].apply(cleanReferencia)
        notInfinteLog('cleaned_mensualidades', 'Datos de mensualidades limpiados correctamente', method='debug')
        return dfMensualidades
    except Exception as e:
        notInfinteLog('error_cleaning_mensualidades', f'Error al limpiar los datos de mensualidades: {e}', method='error')
        raise e


# Función Auxiliar para Cargar los Datos guardados localmente
# Los Datos que carga son: moras.parquet y mensualidades.parquet
@st.cache_data(show_spinner=False)
def loadData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos Datos de Moras y Mensualidades
        moras = pd.read_parquet('data/moras.parquet')
        mensualidades = pd.read_parquet('data/mensualidades.parquet')
        notInfinteLog('loaded_data', 'Datos cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        flujoBerex = cleanFlujoBerex(moras) # El flujo de Berex se obtiene a partir de las moras, por lo que se limpia con la función de limpieza de flujo de Berex
        return moras, mensualidades, flujoBerex
    except Exception as e:
        notInfinteLog('error_loading_data', f'Error al cargar los datos: {e}', method='error')
        raise e

# Función Auxiliar para cargar los datos de prueba de la calculadora
@st.cache_data(show_spinner=False)
def loadTestData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos Datos de Moras y Mensualidades
        moras = pd.read_parquet('data/tests/test_berex.parquet')
        mensualidades = pd.read_parquet('data/tests/test_mensualidades.parquet')
        notInfinteLog('loaded_test_data', 'Datos de prueba cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        flujoBerex = cleanFlujoBerex(moras) # El flujo de Berex se obtiene a partir de las moras, por lo que se limpia con la función de limpieza de flujo de Berex
        return moras, mensualidades, flujoBerex
    except Exception as e:
        notInfinteLog('error_loading_test_data', f'Error al cargar los datos de prueba: {e}', method='error')
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()