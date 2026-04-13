# Librerías Core
import logging
import logging.config
import streamlit as st
from pathlib import Path

# Librerías Adicionales
from typing import Callable, Any
from functools import wraps
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

def notInfiniteLog(name: str, message: str, method: str = 'info') -> None:
    # 1. Obtener el logger de forma segura
    logger_func = getattr(debugLogger, method, debugLogger.info)
    
    # 2. Variable para decidir si logueamos
    should_log = False

    # Caso A: Primera vez que se ejecuta para este "name"
    if name not in st.session_state:
        st.session_state[name] = True
        should_log = True
    
    # Caso B: El usuario realizó una acción manual
    elif st.session_state.get('accion_user', False):
        should_log = True
        # IMPORTANTE: Resetear el flag para que no loguee infinitamente en el próximo rerun
        st.session_state['accion_user'] = False

    # 3. Ejecución del log
    if should_log:
        logger_func(message)

def logWrapper(message: str, onErrorValue: Any = None) -> Callable:
    def middleWrapper(func: Callable) -> Callable:
        @wraps(func)  # <--- Esto preserva la identidad de la función original
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Usamos el nombre original gracias a @wraps o func.__name__
                notInfiniteLog(f'error_{func.__name__}', f'{message}: {e}', method='error')
                return onErrorValue
        return wrapper
    return middleWrapper

def logClassWrapper(message: str, onErrorValue: Any = None) -> Callable:
    def middleWrapper(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Nombre de la clase para el log y el session_state
                class_name = self.__class__.__name__
                log_key = f'error_{class_name}_{func.__name__}'
                log_msg = f'{message} en {class_name}: {e}'
                
                # Llamada a tu función auxiliar de logs
                notInfiniteLog(log_key, log_msg, method='error')
                
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