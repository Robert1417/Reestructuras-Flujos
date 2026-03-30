# Librerías Core
import streamlit as st
import pandas as pd
import json

# Librerías de Typing
from typing import Tuple

# Librerías de Ayuda
from src.calculator.utils.session_state_managers import updateSessionState
from src.calculator.utils.logger_setup import logWrapper, notInfiniteLog

# Definimos las Columnas Existentes en Cada uno de los DFs
columnasMoras = ['Referencia','Fecha','Fecha_Origen','Por_Cobrar','Pago','Status_Mora']
columnasBerex = ['Referencia','Fecha_Pago_Berex','Monto_Berex','Destino']
columnasMensualidades = ['Referencia','Status_Facturacion','Status_Reparadora','Fecha_Cobro','Monto_Mensualidad']
columnasPagare = ['Referencia','Fecha PaB','Monto PaB','Fecha Comision','Monto Comision','Fecha Mensualidad',
                'Monto Mensualidad','Saldo_Pendiente','Incumplimientos_Pagos']

# Definimos Dfs vacios ante algún error
emptyMoras = pd.DataFrame(columns=columnasMoras)
emptyBerex = pd.DataFrame(columns=columnasBerex)
emptyMensualidades = pd.DataFrame(columns=columnasMensualidades)
emptyPagare = pd.DataFrame(columns=columnasPagare)

# --- Funciones Auxiliares de Limpieza e Imputación ---

# Función Auxiliar para Limpiar las Referencias
def cleanReferencia(ref) -> str:
    return str(ref).replace('.0','').strip()

# Función Auxiliar para imputar NaNs
def imputeNans(df: pd.DataFrame, col: str, value) -> None:
    # Se define la mascara de valores nulos
    mask = df[col].isna()
    # A los valores nulos se aplica el valor
    df.loc[mask, col] = value

# --- Limpieza de Datos ---

# Función Auxiliar para Añadir Columna de Saldo_Pendiente al DF de Berex
@logWrapper(message='Error al añadir la columna de Saldo_Pendiente al flujo de Berex', onErrorValue=emptyBerex)
def addSaldoPendienteToBerex(berex: pd.DataFrame, moras: pd.DataFrame) -> pd.DataFrame:
    # Primero Verificamos que solo exista una Referencia en cada DF
    if berex['Referencia'].nunique() != 1 or moras['Referencia'].nunique() != 1:
        raise ValueError(f'Los DFs de Berex y Moras deben contener solo una Referencia para poder calcular el Saldo Pendiente, \
                        pero el DF de Berex tiene {berex["Referencia"].nunique()} referencias y el DF de Moras tiene {moras["Referencia"].nunique()} referencias')
    # Obtenemos el Pago Total de Moras
    pago_total_moras = moras['Pago'].sum()
    # Creamos Columna Auxiliar de Meses_Totales como Fecha_Pago_Berex.year * 12 + Fecha_Pago_Berex.month para Organizar los Datos por Meses de Menor a Mayor
    berex = berex.assign(Meses_Totales = berex['Fecha_Pago_Berex'].dt.year * 12 + berex['Fecha_Pago_Berex'].dt.month)
    # Ordenamos el DF de Berex por Meses_Totales y Destino de Menor a Mayor
    berex = berex.sort_values(by=['Meses_Totales', 'Destino']).reset_index(drop=True)

    # Creamos Lista para Guardar el Saldo Pendiente Calculado para cada Fila
    saldo_pendiente = []

    # Iteramos sobre las Filas del DF de Berex para Calcular el Saldo Pendiente
    for index, row in berex.iterrows():
        # Obtenemos el Monto a Pagar
        monto_a_pagar = row['Monto_Berex']
        # Calculamos el Maximo Pago referente a ese Monto
        max_pago = min(monto_a_pagar, pago_total_moras)
        # Actualizamos el Pago Total de Moras Restando el Maximo Pago
        pago_total_moras -= max_pago
        # Calculamos el Saldo Pendiente Restando el Maximo Pago al Monto a Pagar
        saldo_pendiente.append(monto_a_pagar - max_pago)
    
    # Añadimos la Columna de Saldo_Pendiente al DF de Berex
    berex = berex.assign(Saldo_Pendiente = saldo_pendiente)

    # Eliminamos la Columna Auxiliar de Meses_Totales
    berex = berex.drop(columns=['Meses_Totales'])

    return berex

# Función Auxiliar para Añadir la Columna de Saldo_Pendiente de Forma Masiva
@logWrapper(message='Error al añadir la columna de Saldo_Pendiente de forma masiva al flujo de Berex', onErrorValue=emptyBerex)
def addSaldoPendienteToBerexMassive(berex: pd.DataFrame, moras: pd.DataFrame) -> pd.DataFrame:
    # Verificamos que ambos DFs no esten Vacios
    if berex.empty or moras.empty:
        raise ValueError('Los DFs de Berex y Moras no pueden estar vacíos para calcular el Saldo Pendiente')
    
    # Vamos a Agregar el Saldo Pendiente Agrupando por Referencia
    berexPendientes = [addSaldoPendienteToBerex(berex[berex['Referencia'] == ref], moras[moras['Referencia'] == ref]) for ref in berex['Referencia'].unique()]
    # Concatenamos los DFs de Berex con el Saldo Pendiente
    berex = pd.concat(berexPendientes, ignore_index=True)

    return berex

# Función Auxiliar para limpiar los Datos de Moras
@logWrapper(message='Error al limpiar los datos de moras', onErrorValue=emptyMoras)
def cleanMoras(dfMoras: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfMoras = dfMoras[columnasMoras].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfMoras['Referencia'] = dfMoras['Referencia'].apply(cleanReferencia)
    # Volvemos las Columnas Pago y Por Cobrar a Númerico
    dfMoras['Pago'] = pd.to_numeric(dfMoras['Pago'], errors='coerce')
    dfMoras['Por_Cobrar'] = pd.to_numeric(dfMoras['Por_Cobrar'], errors='coerce')
    # Imputamos los NaNs de Pago y Por Cobrar con 0
    imputeNans(dfMoras, 'Pago', 0)
    imputeNans(dfMoras, 'Por_Cobrar', 0)
    # Volvemos la Columna Fecha a Datetime
    dfMoras['Fecha'] = pd.to_datetime(dfMoras['Fecha'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha
    dfMoras = dfMoras.sort_values(by=['Referencia', 'Fecha']).reset_index(drop=True)
    # Devolvemos el DF Limpio
    notInfiniteLog('cleaned_moras', 'Datos de moras limpiados correctamente', method='debug')
    return dfMoras

# Función Auxiliar para limpiar el Flujo de Berex
@logWrapper(message='Error al limpiar los datos del flujo de Berex', onErrorValue=emptyBerex)
def cleanFlujoBerex(dfFlujo: pd.DataFrame, moras: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfFlujo = dfFlujo[columnasBerex].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfFlujo['Referencia'] = dfFlujo['Referencia'].apply(cleanReferencia)
    # Volvemos la Columna Monto_Berex a Númerico
    dfFlujo['Monto_Berex'] = pd.to_numeric(dfFlujo['Monto_Berex'], errors='coerce')
    # Imputamos los NaNs de Monto_Berex con 0
    imputeNans(dfFlujo, 'Monto_Berex', 0)
    # Volvemos la Columna Fecha_Pago_Berex a Datetime
    dfFlujo['Fecha_Pago_Berex'] = pd.to_datetime(dfFlujo['Fecha_Pago_Berex'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha_Pago_Berex
    dfFlujo = dfFlujo.sort_values(by=['Referencia', 'Fecha_Pago_Berex']).reset_index(drop=True)
    # Añadimos la Columna de Saldo_Pendiente al Flujo de Berex
    dfFlujo = addSaldoPendienteToBerexMassive(dfFlujo, moras)
    # Devolvemos el DF Limpio
    notInfiniteLog('cleaned_flujo_berex', 'Datos del flujo de Berex limpiados correctamente', method='debug')
    return dfFlujo

# Función Auxiliar para limpiar los Datos de Mensualidades
@logWrapper(message='Error al limpiar los datos de mensualidades', onErrorValue=emptyMensualidades)
def cleanMensualidades(dfMensualidades: pd.DataFrame) -> pd.DataFrame:
    # Primero dejamos solo las Columnas Requeridas
    dfMensualidades = dfMensualidades[columnasMensualidades].copy()
    # Limpiamos la Referencia para Asegurar que esté en el Formato Correcto
    dfMensualidades['Referencia'] = dfMensualidades['Referencia'].apply(cleanReferencia)
    # Volvemos la Columna Monto_Mensualidad a Númerico
    dfMensualidades['Monto_Mensualidad'] = pd.to_numeric(dfMensualidades['Monto_Mensualidad'], errors='coerce')
    # Imputamos los NaNs de Monto_Mensualidad con 0
    imputeNans(dfMensualidades, 'Monto_Mensualidad', 0)
    # Volvemos la Columna Fecha_Cobro a Datetime
    dfMensualidades['Fecha_Cobro'] = pd.to_datetime(dfMensualidades['Fecha_Cobro'], errors='coerce')
    # Organizamos el DF por Referencia y Fecha_Cobro
    dfMensualidades = dfMensualidades.sort_values(by=['Referencia', 'Fecha_Cobro']).reset_index(drop=True)
    # Devolvemos el DF Limpio
    notInfiniteLog('cleaned_mensualidades', 'Datos de mensualidades limpiados correctamente', method='debug')
    return dfMensualidades

# --- Carga General de Datos ---

# Función Auxiliar para Cargar los Datos guardados localmente
# Los Datos que carga son: moras.parquet, cartera.parquet y mensualidades.parquet
@st.cache_data(show_spinner=False)
def loadData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos los Datos
        moras = pd.read_parquet('data/moras.parquet')
        berex = pd.read_parquet('data/cartera.parquet')
        mensualidades = pd.read_parquet('data/mensualidades.parquet')
        notInfiniteLog('loaded_data', 'Datos cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        berex = cleanFlujoBerex(berex, moras)
        mensualidades = cleanMensualidades(mensualidades)
        return moras, berex, mensualidades
    except Exception as e:
        notInfiniteLog('error_loading_data', f'Error al cargar los datos: {e}', method='error')
        return emptyMoras, emptyBerex, emptyMensualidades

# Función Auxiliar para cargar los datos de prueba de la calculadora
@st.cache_data(show_spinner=False)
def loadTestData() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        # Cargamos Datos de Moras y Mensualidades
        moras = pd.read_parquet('data/tests/test_berex.parquet')
        berex = pd.read_parquet('data/tests/test_cartera.parquet')
        mensualidades = pd.read_parquet('data/tests/test_mensualidades.parquet')
        notInfiniteLog('loaded_test_data', 'Datos de prueba cargados correctamente', method='debug')
        # Limpiamos los DFs
        moras = cleanMoras(moras)
        mensualidades = cleanMensualidades(mensualidades)
        berex = cleanFlujoBerex(berex, moras)
        return moras, berex, mensualidades
    except Exception as e:
        notInfiniteLog('error_loading_test_data', f'Error al cargar los datos de prueba: {e}', method='error')
        return emptyMoras, emptyBerex, emptyMensualidades

# Función Auxiliar para cargar los Parametros de Prueba
@st.cache_data(show_spinner=False)
def loadTestParams() -> dict:
    try:
        # Cargamos los Parámetros de Prueba
        with open('data/tests/test_params.json', 'r') as f:
            params = json.load(f)
        notInfiniteLog('loaded_test_params', 'Parámetros de prueba cargados correctamente', method='debug')
        return params
    except Exception as e:
        notInfiniteLog('error_loading_test_params', f'Error al cargar los parámetros de prueba: {e}', method='error')
        return {}

# --- Filtrado de Datos ---

# Función Auxiliar para filtrar los DFs con Datos a Día de Hoy
@logWrapper(message='Error al filtrar los datos a día de hoy', onErrorValue=(emptyMoras, emptyBerex, emptyMensualidades))
def filterDataToToday(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Obtenemos la Fecha de Hoy
    today = pd.to_datetime('today').normalize()
    # Filtramos los DFs para quedarnos solo con los Datos a Día de Hoy o Anteriores
    moras = moras[moras['Fecha'] <= today]
    berex = berex[berex['Fecha_Pago_Berex'] <= today]
    # El Filtro por Mensualides es Diferente, ya que se toman menores o iguales a este mes
    # Se realiza el replace por si el día de hoy es el último día del mes, para que tome los datos de este mes completo
    today_month_end = today.replace(day=1) + pd.offsets.MonthEnd(0)
    mensualidades = mensualidades[mensualidades['Fecha_Cobro'] <= today]
    notInfiniteLog('filtered_data_to_today', 'Datos filtrados a día de hoy correctamente', method='debug')
    return moras, berex, mensualidades

# Función Auxiliar para filtrar las Mensualidades presentes en el flujo Original de Berex, es decir, solo las mensualidades que no sobrepasenFecha_Pago_Berex.max()
@logWrapper(message='Error al filtrar las mensualidades presentes en el flujo original de Berex', onErrorValue=emptyMensualidades)
def filterMensualidadesToOriginalBerex(mensualidades: pd.DataFrame, berex: pd.DataFrame) -> pd.DataFrame:
    # Obtenemos la Fecha_Pago_Berex máxima del flujo de Berex
    max_fecha_pago_berex = berex['Fecha_Pago_Berex'].max()
    # Ahora Dejamos max_fecha_pago como el dia del siguiente mes
    max_fecha_pago_berex = max_fecha_pago_berex.replace(day=1) + pd.offsets.MonthBegin(0)
    # Filtramos las Mensualidades para quedarnos solo con las que tengan Fecha_Cobro menor a la Fecha_Pago_Berex máxima
    mensualidades_filtradas = mensualidades[mensualidades['Fecha_Cobro'] < max_fecha_pago_berex]
    notInfiniteLog('filtered_mensualidades_to_original_berex', 'Mensualidades filtradas al flujo original de Berex correctamente', method='debug')
    return mensualidades_filtradas

# Función Auxiliar para Filtrar Datos de un Mes dado el Timestamp
@logWrapper(message='Error al filtrar los datos por mes', onErrorValue=emptyMensualidades)
def filterDataByMonth(df: pd.DataFrame, dateColumn: str, month: pd.Timestamp) -> pd.DataFrame:
    # Filtramos los DFs para quedarnos solo con los Datos del Mes dado
    df = df[(df[dateColumn].dt.year == month.year) & (df[dateColumn].dt.month == month.month)]
    notInfiniteLog(f'filtered_data_by_month_{dateColumn}', f'Datos filtrados por mes: {month.strftime("%Y-%m")}', method='debug')
    return df

# --- Reorganización de Datos ---

# Función Auxiliar para Reorganizar los Datos de un Mes como son en el Pagaré
@logWrapper(message='Error al reorganizar los datos de un mes como en el pagaré', onErrorValue={col: '' for col in columnasPagare})
def reorganizeDataAsInPagareForMonth(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> dict:
    # Creamos el Diccionario del Pagaré para el Mes dado
    pagareDict = {}
    # Añadimos la Referencia
    pagareDict['Referencia'] = berex['Referencia'].iloc[0] if not berex.empty else (moras['Referencia'].iloc[0] if not moras.empty else (mensualidades['Referencia'].iloc[0] if not mensualidades.empty else ''))
    # Añadimos los Datos de PaB
    berexPaB = berex[berex['Destino'] == 'Banco'].copy()
    pagareDict['Fecha PaB'] = berexPaB['Fecha_Pago_Berex'].min() if not berexPaB.empty else pd.NaT
    pagareDict['Monto PaB'] = berexPaB['Monto_Berex'].sum() if not berexPaB.empty else 0
    # Añadimos los Datos de Comisión
    berexComision = berex[berex['Destino'] == 'Comisión'].copy()
    pagareDict['Fecha Comision'] = berexComision['Fecha_Pago_Berex'].min() if not berexComision.empty else pd.NaT
    pagareDict['Monto Comision'] = berexComision['Monto_Berex'].sum() if not berexComision.empty else 0
    # Añadimos los Datos de Mensualidades
    pagareDict['Fecha Mensualidad'] = mensualidades['Fecha_Cobro'].min() if not mensualidades.empty else pd.NaT
    pagareDict['Monto Mensualidad'] = mensualidades['Monto_Mensualidad'].sum() if not mensualidades.empty else 0

    # El Saldo Pendiente se Inicializa como 0
    pagareDict['Saldo_Pendiente'] = 0
    # Se le Añade el Saldo pendiente de Berex
    pagareDict['Saldo_Pendiente'] += berex['Saldo_Pendiente'].sum() if not berex.empty else 0
    # Se le Añade el Monto_Mensualidad donde Status_Facturacion == 'POR_COBRAR'
    pagareDict['Saldo_Pendiente'] += mensualidades[mensualidades['Status_Facturacion'] == 'POR_COBRAR']['Monto_Mensualidad'].sum() if not mensualidades.empty else 0

    # Inicializamos Incumplimientos_Pagos con una lista Vacía
    pagareDict['Incumplimientos_Pagos'] = []
    # Añádimos Banco si berexPaB tiene Saldo_Pendiente > 0
    if berexPaB['Saldo_Pendiente'].sum() > 0:
        pagareDict['Incumplimientos_Pagos'].append('Banco')
    # Añádimos Comisión si berexComision tiene Saldo_Pendiente > 0
    if berexComision['Saldo_Pendiente'].sum() > 0:
        pagareDict['Incumplimientos_Pagos'].append('Comision')
    # Añádimos Mensualidad si mensualidades con Status_Facturacion == 'POR_COBRAR' tiene Monto_Mensualidad > 0
    if mensualidades[mensualidades['Status_Facturacion'] == 'POR_COBRAR']['Monto_Mensualidad'].sum() > 0:
        pagareDict['Incumplimientos_Pagos'].append('Mensualidad')
    
    # Unimos los Incumplimientos_Pagos en una Cadena Separada por Comas
    pagareDict['Incumplimientos_Pagos'] = ', '.join(pagareDict['Incumplimientos_Pagos']) if pagareDict['Incumplimientos_Pagos'] else 'Ninguno'

    # Devolvemos el Diccionario del Pagaré para el Mes dado
    return pagareDict

# Función Auxiliar para Reorganizar los Datos como son en el Pagaré 
@logWrapper(message='Error al reorganizar los datos como en el pagaré', onErrorValue=emptyPagare)
def reorganizeDataAsInPagare(moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame) -> pd.DataFrame:
    # Primero Creamos el Diccionario donde se va a guardar la Información Reorganizada
    pagareDict = {col: [] for col in columnasPagare}

    # Ahora Obtenemos la Fecha Minima y Maxima de Pago del Flujo de Berex para Filtrar las Moras y Mensualidades a esa Fecha
    min_fecha_pago_berex = berex['Fecha_Pago_Berex'].min()
    max_fecha_pago_berex = berex['Fecha_Pago_Berex'].max()

    # Ahora Vamos a Iterar en Ventanas de 1 Mes desde la Fecha Minima hasta la Fecha Maxima del Flujo de Berex
    current_month = min_fecha_pago_berex.replace(day=1)

    while current_month <= max_fecha_pago_berex:
        # Filtramos las Moras, Berex y Mensualidades por el Mes Actual
        moras_mes = filterDataByMonth(moras, 'Fecha', current_month)
        berex_mes = filterDataByMonth(berex, 'Fecha_Pago_Berex', current_month)
        mensualidades_mes = filterDataByMonth(mensualidades, 'Fecha_Cobro', current_month)

        # Ahora Reorganizamos los Datos del Mes Actual como en el Pagaré
        pagare_mes = reorganizeDataAsInPagareForMonth(moras_mes, berex_mes, mensualidades_mes)

        # Añadimos los Datos Reorganizados del Mes Actual al Diccionario del Pagaré
        for col in columnasPagare:
            pagareDict[col].extend(pagare_mes[col].tolist())
        
        # Avanzamos al Siguiente Mes
        current_month += pd.offsets.MonthBegin(1)

    # Una vez que se ha Reorganizado toda la Información, se Crea el DF del Pagaré a Partir del Diccionario del Pagaré
    pagare = pd.DataFrame(pagareDict)
    # Devolvemos el DF del Pagaré Reorganizado
    notInfiniteLog('reorganized_data_as_in_pagare', 'Datos reorganizados como en el pagaré correctamente', method='debug')
    return pagare