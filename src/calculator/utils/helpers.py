# Este es un código que contiene las funciones de ayuda que facilitan el uso de la calculadora

# Librerías necesarias
import pandas as pd
import streamlit as st

# Librerías para Estructura de Código
from typing import Tuple, Any, Callable

# Importamos el Logger de Debugging
from src.calculator import debugLogger

# --- Manejo de Logs ---

# Función Auxiliar para Evitar Logs por cada Ejecución de la Calculadora, Solo se Logueará la Primera Ejecución o 
# Si existe un cambio en Acción del cliente (el session_state de accion_user cambia a True)
def notInfinteLog(name: str, message: str, method: str = 'info') -> None:
    # Primera Verificación: El Session state de name no existe, lo que indica que es la primera ejecución de la calculadora, por lo que se loguea el mensaje
    if name not in st.session_state:
        debugLogger.log(getattr(debugLogger, method), message)
        st.session_state[name] = True  # Se establece el session state para evitar logs futuros
        return # Para Finalizar la Ejecución de la Función
    # Segunda Verificación: El Session state de name existe y el session_state de accion_user es True, lo que indica que el cliente ha realizado una acción, por lo que se loguea el mensaje
    if st.session_state.get('accion_user', False):
        debugLogger.log(getattr(debugLogger, method), message)
        return # Para Finalizar la Ejecución de la Función
    # Si ninguna de las condiciones anteriores se cumple, no se loguea el mensaje para evitar logs infinitos por cada ejecución de la calculadora sin acciones del cliente
    notInfinteLog(f'ignored_{name}', f'Mensaje ignorado: {message}', method='debug')
# --- Manejo de Session States ---

defaultValues = {
    'cliente_ref': 0,
    'nuevo_apartado_mensual': 0.0,
    'nuevo_pago_inicial': 0.0,
}

# Función Auxiliar para Inicializar in Session State
def initializeSessionState(key: str, value) -> None:
    if key not in st.session_state:
        st.session_state[key] = value
        notInfinteLog(f'initialized_{key}', f'Session state inicializado: {key} = {value}', method='debug')

# Función Auxiliar para saber si un Session State está definido
def isSessionStateDefined(key: str) -> bool:
    return key in st.session_state

# Función Auxiliar para Actualizar un Session State
def updateSessionState(key: str, value: Any) -> bool:
    try:
        originalValue = st.session_state.get(key, None)
        st.session_state[key] = value
        return originalValue != value  # Retorna True si el valor fue actualizado, False si el valor no cambió
    except Exception as e:
        notInfinteLog('error_updating_session_state', f'Error al actualizar session state: {e}', method='error')
        raise e

# Función Auxiliar para Obtener un Session State con un Valor por Defecto si no está definido
def getSessionStateWithDefault(key: str, default_value_fun: Callable[[], Any]) -> Any:
    return st.session_state.get(key, default_value_fun())

# Función Auxiliar para Obtener un Session State
def getSessionState(key: str) -> Any:
    try:
        value = st.session_state.get(key, None)
        return value
    except Exception as e:
        notInfinteLog('error_getting_session_state', f'Error al obtener session state: {e}', method='error')
        raise e

# Función Auxiliar para saber si todos los Session States necesarios están definidos
def areSessionStatesDefined(keys: list) -> bool:
    try:
        for key in keys:
            if key not in st.session_state:
                notInfinteLog(f'missing_{key}', f'Session state no definido: {key}', method='warning')
                return False
        keys_str = ', '.join(keys)
        notInfinteLog(f'defined_{keys_str}', 'Todos los session states necesarios están definidos', method='debug')
        return True
    except Exception as e:
        notInfinteLog('error_verifying_session_states', f'Error al verificar session states: {e}', method='error')
        raise e

# Función Auxiliar para saber si todos los Session States estan definidos y no por los valores por defecto
def areSessionStatesValid(keys: list) -> bool:
    try:
        for key in keys:
            if key not in st.session_state or (key in defaultValues and st.session_state[key] == defaultValues[key]):
                notInfinteLog(f'invalid_{key}', f'Session state no válido: {key} = {st.session_state.get(key, None)}', method='warning')
                return False
        keys_str = ', '.join(keys)
        notInfinteLog(f'valid_{keys_str}', 'Todos los session states necesarios son válidos', method='debug')
        return True
    except Exception as e:
        notInfinteLog('error_verifying_session_states', f'Error al verificar session states: {e}', method='error')
        raise e

# --------- Obtención y Limpieza de Datos ---------

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
        dfMoras['Fecha_Pago_Berex'] = pd.to_datetime(dfMoras['payment_date'])
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
        # Se dejan solo Columnas de: Referencia, Fecha_Origen, Fecha_Pago_Berex, Monto_Berex,Destination
        dfFlujo = dfFlujo[['Referencia', 'Fecha_Origen', 'Fecha_Pago_Berex', 'Monto_Berex', 'Destino']].copy()
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
        moras = pd.read_parquet('src/calculator/data/moras.parquet')
        mensualidades = pd.read_parquet('src/calculator/data/mensualidades.parquet')
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
        moras = pd.read_parquet('src/calculator/data/tests/test_berex.parquet')
        mensualidades = pd.read_parquet('src/calculator/data/tests/test_mensualidades.parquet')
        notInfinteLog('loaded_test_data', 'Datos de prueba cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        flujoBerex = cleanFlujoBerex(moras) # El flujo de Berex se obtiene a partir de las moras, por lo que se limpia con la función de limpieza de flujo de Berex
        return moras, mensualidades, flujoBerex
    except Exception as e:
        notInfinteLog('error_loading_test_data', f'Error al cargar los datos de prueba: {e}', method='error')
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- Métricas y Cálculos ---

# Función Auxiliar para Calcular Métricas Clave del Flujo de Berex: Total Pagado, Total Monto Berex y Porcentaje Pagado
def calcMetricasFlujo(dfFlujo: pd.DataFrame) -> Tuple[float, float, float]:
    try:
        # Calculamos el Total Pagado en el Flujo de Berex
        totalPagado = dfFlujo['Pago'].sum()
        # Calculamos el Total del Monto de Berex en el Flujo de Berex
        totalMontoBerex = dfFlujo['Monto_Berex'].sum()
        # Calculamos el Porcentaje Pagado del Monto de Berex en el Flujo de Berex
        porcentajePagado = (totalPagado / totalMontoBerex) * 100 if totalMontoBerex > 0 else 0.0
        notInfinteLog('calculated_flujo_metrics', f'Métricas del flujo calculadas correctamente: Total Pagado = {totalPagado}, Total Monto Berex = {totalMontoBerex}, Porcentaje Pagado = {porcentajePagado:.2f}%', method='debug')
        return totalPagado, totalMontoBerex, porcentajePagado
    except Exception as e:
        notInfinteLog('error_calculating_flujo_metrics', f'Error al calcular las métricas del flujo: {e}', method='error')
        raise e