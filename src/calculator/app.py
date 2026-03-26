import streamlit as st
import logging
import json

# Le agregamos las Configuraciones de core/config/loggerConfig.json
with open('core/config/loggerConfig.json', 'r') as f:
    config = json.load(f)
    logging.config.dictConfig(config)

# Definimos nuestro Logger de Debugging
debugLogger = logging.getLogger('calculator_debug')

