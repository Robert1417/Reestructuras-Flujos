# Archivo para Estilizar los DataFrames en la Aplicación

# Librerías Core
import streamlit as st
import pandas as pd

# Librerías de Ayuda
from src.calculator.utils.logger_setup import stWarningLogWrapper
from src.calculator.utils.data_load import emptyBerex, emptyPagare

# Función Auxiliar para Estilizar el DataFrame de Berex
@stWarningLogWrapper(message="Error al estilizar el DataFrame de Berex")
def estilizarBerex(berex: pd.DataFrame):
    """
    Estiliza el DataFrame de Berex para su visualización en la aplicación.

    Args:
        berex (pd.DataFrame): DataFrame que contiene los datos de berex.
    """
    if berex.empty:
        return pd.io.formats.style.Styler(emptyBerex)
    
    # Definimos la Función de Estilo para el DataFrame de Berex
    def styleBerex(row):
        if row['Saldo Pendiente'] > 0:
            # Agregamos Color Rojo para las Filas con Saldo Pendiente Mayor a 0
            return ['background-color: #ffcccc'] * len(row)
        else:
            # Agregamos Color Verde para las Filas con Saldo Pendiente Igual a 0
            return ['background-color: #ccffcc'] * len(row)

    berexStyled =  berex.style.apply(styleBerex, axis=1)
    return berexStyled

# Función Auxiliar para Estilizar el DataFrame de Pagaré
@stWarningLogWrapper(message="Error al estilizar el DataFrame de Pagaré")
def estilizarPagare(pagare: pd.DataFrame):
    """
    Estiliza el DataFrame de Pagaré para su visualización en la aplicación.

    Args:
        pagare (pd.DataFrame): DataFrame que contiene los datos de pagaré.
    """
    if pagare.empty:
        return pd.io.formats.style.Styler(emptyPagare)
    
    # Definimos la Función de Estilo para el DataFrame de Pagaré
    def stylePagare(row):
        # Obtenemos los Incumplimientos de Pagos para la Fila Actual
        incumplimientos = row['Incumplimientos_Pagos'].split(',') if pd.notna(row['Incumplimientos_Pagos']) else []

        # Primero Definimos la Lista de Estilos Vacia
        styles = ['' for _ in range(len(row))]
        # Ahora Aplicamos Estilos Individuales para cada Columna
        # Columna Referencia: Negrita
        styles[pagare.columns.get_loc('Referencia')] = 'font-weight: bold' # type: ignore

        # Formatos Condicionales para Pagos
        # 1. Incumplimiento de Pago a Banco
        if 'Banco' in incumplimientos:
            styles[pagare.columns.get_loc('Monto PaB')] = 'background-color: #ffcccc' # type: ignore
            styles[pagare.columns.get_loc('Fecha PaB')] = 'background-color: #ffcccc' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto PaB')] = 'background-color: #ccffcc' # type: ignore
            styles[pagare.columns.get_loc('Fecha PaB')] = 'background-color: #ccffcc' # type: ignore
        # 2. Incumplimiento de Pago de Comisión
        if 'Comision' in incumplimientos:
            styles[pagare.columns.get_loc('Monto Comision')] = 'background-color: #ffcccc' # type: ignore
            styles[pagare.columns.get_loc('Fecha Comision')] = 'background-color: #ffcccc' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto Comision')] = 'background-color: #ccffcc' # type: ignore
            styles[pagare.columns.get_loc('Fecha Comision')] = 'background-color: #ccffcc' # type: ignore
        # 3. Incumplimiento de Pago de Mensualidad
        if 'Mensualidad' in incumplimientos:
            styles[pagare.columns.get_loc('Monto Mensualidad')] = 'background-color: #ffcccc' # type: ignore
            styles[pagare.columns.get_loc('Fecha Mensualidad')] = 'background-color: #ffcccc' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto Mensualidad')] = 'background-color: #ccffcc' # type: ignore
            styles[pagare.columns.get_loc('Fecha Mensualidad')] = 'background-color: #ccffcc' # type: ignore

        # Estilo de Saldo Pendiente: Si el Saldo Pendiente es Mayor a 0, lo Resaltamos en Rojo, Sino en Verde
        if row['Saldo_Pendiente'] > 0:
            styles[pagare.columns.get_loc('Saldo_Pendiente')] = 'background-color: #ffcccc' # type: ignore
        else:
            styles[pagare.columns.get_loc('Saldo_Pendiente')] = 'background-color: #ccffcc' # type: ignore

        # Estilo de Incumplimientos de Pagos: Si hay Incumplimientos, lo Resaltamos en Rojo, Sino en Verde
        if not 'Ninguno' in incumplimientos:
            styles[pagare.columns.get_loc('Incumplimientos_Pagos')] = 'background-color: #ffcccc' # type: ignore
        else:
            styles[pagare.columns.get_loc('Incumplimientos_Pagos')] = 'background-color: #ccffcc' # type: ignore

        return styles

    pagareStyled = pagare.style.apply(stylePagare, axis=1)
    return pagareStyled