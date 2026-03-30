# Librerías Core
import streamlit as st
from typing import Any, Callable

# Librerías de Ayuda
from src.calculator.utils.logger_setup import notInfinteLog, debugLogger

defaultValues = {
    'cliente_ref': 'Seleccionar Referencia',
    'nuevo_apartado_mensual': 1000,
    'nuevo_pago_inicial': 1000,
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