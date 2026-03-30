# Librerías Core
import streamlit as st
from datetime import datetime

# Librerías de Ayuda
from src.calculator.utils.logger_setup import debugLogger

def main():
    """Función Principal de Ejecución de la Calculadora, creando la Navegación entre Páginas y Mostrando la Página de Inicio
    """
    # 1. Definición de las Páginas de la Aplicación
    calculator_page = st.Page(
        "pages/1_calculadora.py",
        title="Calculadora",
        icon="🧮",
        default=True
    )
    testing_page = st.Page(
        "pages/2_testing.py",
        title="Testing",
        icon="🧪"
    )
    verification_page = st.Page(
        "pages/3_verificar_datos.py",
        title="Verificación",
        icon="✅"
    )

    # 2. Creación de la Navegación entre Páginas
    pg = st.navigation({
        "Calculadora": [calculator_page],
        "Testing": [testing_page],
        "Verificación": [verification_page]
    })

    # 3. Ejecución de la Página Seleccionada
    pg.run()

if __name__ == "__main__":
    debugLogger.info("Iniciando la aplicación de la Calculadora de Reestructuras - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    main()