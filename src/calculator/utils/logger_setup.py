import os
import json
import logging
import logging.config
import streamlit as st
from pathlib import Path

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

# Función Auxiliar para Evitar Logs por cada Ejecución de la Calculadora, Solo se Logueará la Primera Ejecución o 
# Si existe un cambio en Acción del cliente (el session_state de accion_user cambia a True)
def notInfinteLog(name: str, message: str, method: str = 'info') -> None:
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
    notInfinteLog(f'ignored_{name}', f'Mensaje ignorado: {message}', method='debug')

# Create a global instance that can be imported elsewhere
debugLogger = setup_logging()