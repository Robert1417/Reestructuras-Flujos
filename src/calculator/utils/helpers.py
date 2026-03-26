# Este es un código que contiene las funciones de ayuda que facilitan el uso de la calculadora

# Librerías necesarias
import pandas as pd

# Librerías para Estructura de Código
from typing import Tuple

# Importamos el Logger de Debugging
from src.calculator.app import debugLogger

# --------- Obtención y Limpieza de Datos ---------

# Función Auxiliar para limpiar los Datos de Moras
def cleanMoras(dfMoras: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos los Datos de Moras para Asegurar que estén en el Formato Correcto
    try:
        dfMoras['Fecha_Pago_Berex'] = pd.to_datetime(dfMoras['payment_date'])
        dfMoras['amount'] = dfMoras['amount'].astype(float)
        dfMoras['Referencia'] = dfMoras['Referencia'].apply(lambda s: str(s).replace('.0','').strip())
        debugLogger.debug('Datos de moras limpiados correctamente')
        return dfMoras
    except Exception as e:
        debugLogger.error(f'Error al limpiar los datos de moras: {e}')
        raise e

# Función Auxiliar para limpiar los Datos de Mensualidades
def cleanMensualidades(dfMensualidades: pd.DataFrame) -> pd.DataFrame:
    # Limpiamos los Datos de Mensualidades para Asegurar que estén en el Formato Correcto
    try:
        dfMensualidades['Fecha_Cobro'] = pd.to_datetime(dfMensualidades['Fecha_Cobro'])
        dfMensualidades['Monto'] = dfMensualidades['Monto'].astype(float)
        dfMensualidades['Referencia'] = dfMensualidades['Referencia'].apply(lambda s: str(s).replace('.0','').strip())
        debugLogger.debug('Datos de mensualidades limpiados correctamente')
        return dfMensualidades
    except Exception as e:
        debugLogger.error(f'Error al limpiar los datos de mensualidades: {e}')
        raise e


# Función Auxiliar para Cargar los Datos guardados localmente
# Los Datos que carga son: moras.parquet y mensualidades.parquet
def loadData() -> Tuple[pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos Datos de Moras y Mensualidades
        moras = pd.read_parquet('data/moras.parquet')
        mensualidades = pd.read_parquet('data/mensualidades.parquet')
        debugLogger.debug('Datos cargados correctamente')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        return moras, mensualidades
    except Exception as e:
        debugLogger.error(f'Error al cargar los datos: {e}')
        raise e