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

    # Aseguramos la columna requerida por el estilo, incluso en flujos parciales/fallbacks
    if 'Saldo_Pendiente' not in berex.columns:
        berex = berex.copy()
        berex['Saldo_Pendiente'] = 0
    
    # Dejamos Saldo_Pendiente y Monto_Berex redondeados a 2 decimales para una mejor visualización
    berex['Saldo_Pendiente'] = berex['Saldo_Pendiente'].round(2)
    berex['Monto_Berex'] = berex['Monto_Berex'].round(2)

    # Ordenamos el DF por Fecha_Pago_Berex y Destino de menor a mayor
    berex = berex.sort_values(by=['Fecha_Pago_Berex', 'Destino'], ascending=[True, True])
    
    # Definimos la Función de Estilo para el DataFrame de Berex
    def styleBerex(row):
        if row['Fecha_Pago_Berex'].date() >= pd.Timestamp.now().date():
            # Agregamos Color Gris para las Filas con Fecha_Pago_Berex Mayor a la Fecha Actual
            return ['background-color: #c7c8ca; color: #000000'] * len(row)
        if row['Saldo_Pendiente'] == 0:
            # Agregamos Color Verde para las Filas con Saldo_Pendiente Igual a 0
            return ['background-color: #ccffcc; color: #000000'] * len(row)
        if row['Saldo_Pendiente'] < row['Monto_Berex']:
            # Agregamos Color Amarillo para las Filas con Saldo_Pendiente Menor al Monto_Berex
            return ['background-color: #fff2cc; color: #000000'] * len(row)
        if row['Saldo_Pendiente'] > 0:
            # Agregamos Color Rojo para las Filas con Saldo_Pendiente Mayor a 0
            return ['background-color: #ffcccc; color: #000000'] * len(row)


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
            styles[pagare.columns.get_loc('Monto PaB')] = 'background-color: #ffcccc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha PaB')] = 'background-color: #ffcccc; color: #000000' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto PaB')] = 'background-color: #ccffcc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha PaB')] = 'background-color: #ccffcc; color: #000000' # type: ignore
        # 2. Incumplimiento de Pago de Comisión
        if 'Comision' in incumplimientos:
            styles[pagare.columns.get_loc('Monto Comision')] = 'background-color: #ffcccc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha Comision')] = 'background-color: #ffcccc; color: #000000' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto Comision')] = 'background-color: #ccffcc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha Comision')] = 'background-color: #ccffcc; color: #000000' # type: ignore
        # 3. Incumplimiento de Pago de Mensualidad
        if 'Mensualidad' in incumplimientos:
            styles[pagare.columns.get_loc('Monto Mensualidad')] = 'background-color: #ffcccc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha Mensualidad')] = 'background-color: #ffcccc; color: #000000' # type: ignore
        else:
            styles[pagare.columns.get_loc('Monto Mensualidad')] = 'background-color: #ccffcc; color: #000000' # type: ignore
            styles[pagare.columns.get_loc('Fecha Mensualidad')] = 'background-color: #ccffcc; color: #000000' # type: ignore

        # Estilo de Saldo_Pendiente: Si el Saldo_Pendiente es Mayor a 0, lo Resaltamos en Rojo, Sino en Verde
        if row['Saldo_Pendiente'] > 0:
            styles[pagare.columns.get_loc('Saldo_Pendiente')] = 'background-color: #ffcccc; color: #000000' # type: ignore
        else:
            styles[pagare.columns.get_loc('Saldo_Pendiente')] = 'background-color: #ccffcc; color: #000000' # type: ignore

        # Estilo de Incumplimientos de Pagos: Si hay Incumplimientos, lo Resaltamos en Rojo, Sino en Verde
        if not 'Ninguno' in incumplimientos:
            styles[pagare.columns.get_loc('Incumplimientos_Pagos')] = 'background-color: #ffcccc; color: #000000' # type: ignore
        else:
            styles[pagare.columns.get_loc('Incumplimientos_Pagos')] = 'background-color: #ccffcc; color: #000000' # type: ignore

        return styles

    pagareStyled = pagare.style.apply(stylePagare, axis=1)
    return pagareStyled