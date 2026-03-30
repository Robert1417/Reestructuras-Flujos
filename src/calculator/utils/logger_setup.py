# Librerías Core
import logging
import logging.config
import streamlit as st
from pathlib import Path

# Librerías Adicionales
from typing import Callable, Any
import json

@st.cache_resource
def setup_logging():
    """
    Configures logging once and returns the debug logger.
    Streamlit will skip this function on every rerun after the first.
    """
    # 1. Locate the config file relative to this file
    current_dir = Path(__file__).parent.parent # Goes up to calculator/
    config_path = current_dir / "logs" / "config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    # 2. Apply the configuration
    logging.config.dictConfig(config)
    
    # 3. Get the specific logger
    logger = logging.getLogger('calculator_debug')
    
    logger.info("Logger initialized for the first time.")
    return logger

# Create a global instance that can be imported elsewhere
debugLogger = setup_logging()
debugLogger.info("Logger Inicializado y Listo para Usar en la Calculadora.")

# Función Auxiliar para Evitar Logs por cada Ejecución de la Calculadora, Solo se Logueará la Primera Ejecución o 
# Si existe un cambio en Acción del cliente (el session_state de accion_user cambia a True)
def notInfiniteLog(name: str, message: str, method: str = 'info') -> None:
    # Primera Verificación: El Session state de name no existe, lo que indica que es la primera ejecución de la calculadora, por lo que se loguea el mensaje
    if name not in st.session_state:
        getattr(debugLogger, method)(message)  # Se loguea el mensaje utilizando el método especificado (info, debug, warning, error)
        st.session_state[name] = True  # Se establece el session state para evitar logs futuros
        return # Para Finalizar la Ejecución de la Función
    # Segunda Verificación: El Session state de name existe y el session_state de accion_user es True, lo que indica que el cliente ha realizado una acción, por lo que se loguea el mensaje
    if st.session_state.get('accion_user', False):
        getattr(debugLogger, method)(message)  # Se loguea el mensaje utilizando el método especificado (info, debug, warning, error)
        return # Para Finalizar la Ejecución de la Función
    # Si ninguna de las condiciones anteriores se cumple, no se loguea el mensaje para evitar logs infinitos por cada ejecución de la calculadora sin acciones del cliente
    notInfiniteLog(f'ignored_{name}', f'Mensaje ignorado: {message}', method='debug')

# Ahora Creamos una Función que sirva como Decorator de Errores
def logWrapper(message: str, onErrorValue: Any = None) -> Callable:
    def middleWrapper(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                notInfiniteLog(f'error_{func.__name__}', f'{message}: {e}', method='error')
                return onErrorValue
        return wrapper
    return middleWrapper

# Función Decoradora Auxiliar para manejar Errores de Funciones de Clases
def logClassWrapper(message: str, onErrorValue: Any = None) -> Callable:
    def middleWrapper(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                notInfiniteLog(f'error_{self.__class__.__name__}_{func.__name__}', f'{message} en {self.__class__.__name__}: {e}', method='error')
                return onErrorValue
        return wrapper
    return middleWrapper


# Creamos un Decorador para Mostrar una Warning de Streamlit ante algún error en la función decorada, además de loguear el error utilizando el logWrapper
def stWarningLogWrapper(message: str) -> Callable:
    def middleWrapper(func: Callable) -> Callable:
        @logWrapper(message=message, onErrorValue=None)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"{message}: {e}")
        return wrapper
    return middleWrapper