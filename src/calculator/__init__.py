# Se realizan los Imports Mínimos Necesarios para el funcionamiento del módulo
import json
import logging.config


from src.calculator.logging.sheetsLogger import SheetsLoggerHandler


# Le agregamos las Configuraciones de src/calculator/logging/config.json
with open('src/calculator/logging/config.json', 'r') as f:
    config = json.load(f)
    logging.config.dictConfig(config)

sheetsHandler = SheetsLoggerHandler(spreadsheet_id="1sXo9n8l7mLh2j3k9X8v9Z0a1b2c3d4e5f6g7h8i9j0", sheet_name="Logs")

# Definimos nuestro Logger de Debugging
debugLogger = logging.getLogger('calculator_debug')
debugLogger.addHandler(sheetsHandler)