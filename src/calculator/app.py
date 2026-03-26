import streamlit as st
import logging
import logging.config
import json

# Le agregamos las Configuraciones de src/calculator/logging/config.json
with open('src/calculator/logging/config.json', 'r') as f:
    config = json.load(f)
    logging.config.dictConfig(config)

# Definimos nuestro Logger de Debugging
debugLogger = logging.getLogger('calculator_debug')

