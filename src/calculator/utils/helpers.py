# Este es un código que contiene las funciones de ayuda que facilitan el uso de la calculadora

# Librerías necesarias
import pandas as pd
import streamlit as st
import numpy as np

# Librerías para Estructura de Código
from typing import Tuple, Any, Callable

# Importamos el Logger de Debugging
from src.calculator.utils.logger_setup import notInfinteLog, logWrapper

# Función Auxiliar para Obtener el Siguiente Día del Mes dado el Número de Día y el Timestamp
@logWrapper(message="Error al Obtener el Siguiente Día del Mes", onErrorValue=pd.Timestamp.today().normalize())
def getNextMonthDay(day: int, currentDate: pd.Timestamp) -> pd.Timestamp:
    """Función Auxiliar para Obtener el Siguiente Día del Mes dado el Número de Día y el Timestamp

    Args:
        day (int): El Número de Día del Mes que se Quiere Obtener
        currentDate (pd.Timestamp): El Timestamp Actual desde el Cual se Quiere Obtener el Siguiente Día del Mes
    Returns:
        pd.Timestamp: El Siguiente Día del Mes dado el Número de Día y el Timestamp
    """
    # Obtenemos el ÚltimoDía del Siguiente Mes
    nextMonthLastDay = (currentDate.replace(day=1) + pd.offsets.MonthEnd(1))
    # Si el Último Día del Siguiente Mes es Mayor o Igual al Día que se Quiere Obtener, se Devuelve el Día del Siguiente Mes, de lo Contrario se Devuelve el Último Día del Siguiente Mes
    if nextMonthLastDay.day >= day:
        nextMonthDay = nextMonthLastDay.replace(day=day)
    else:
        nextMonthDay = nextMonthLastDay
    # Devolvemos el Resultado
    return nextMonthDay