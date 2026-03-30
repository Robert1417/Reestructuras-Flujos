# Librerías Core
import streamlit as st
import json

# Librerías de Ayuda
from src.calculator.utils.logger_setup import notInfiniteLog

# Librerías de Autennticación de Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Creamos Función para Obtener las Credenciales de Gspread
@st.cache_resource(show_spinner=False)
def getGspreadCredentials():
    # Obtenemos el String de las Credenciales
        creds_info = st.secrets["MI_JSON"]
        # Volvemos las Credenciales en un Diccionario
        creds = json.loads(creds_info.strip())
        # Definimos los scopes
        scopes = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
        # Creamos las Credenciales de Google a Partir del Diccionario
        credentials = Credentials.from_service_account_info(creds, scopes=scopes)
        # Nos Conectamos a Google Sheets usando gspread y las Credenciales
        client = gspread.authorize(credentials)
        # Devolvemos el Cliente de gspread
        return client

# Creamos Función para Obtener una Hoja de Cálculo Específica
@st.cache_resource(show_spinner=False)
def getWorksheet(spreadsheet_id: str, sheet_name: str = "Logs"):
    try:
        client = getGspreadCredentials()
        # Abrimos la Hoja de Cálculo por su ID
        worksheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
        return worksheet
    except Exception as e:
        notInfiniteLog(f'sheets_connection_error_{spreadsheet_id}_{sheet_name}', f'Error al conectar con Google Sheets: {e}', method='error')
        return None

# Creamos Función para Añadir una Fila a la Hoja de Cálculo
def appendRowToSheet(worksheet, row: list):
    if worksheet is not None:
        try:
            worksheet.append_row(row)
        except Exception as e:
            notInfiniteLog(f'sheets_append_error_{worksheet.id}', f'Error al añadir fila a Google Sheets: {e}', method='error')