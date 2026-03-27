# Esta es una Clase para Definir un Logger Personalizado para Guardar los Logs en Sheets

# Librerías Core
import logging
from streamlit import secrets

# Librerías Adicionales
from datetime import datetime
import threading
import queue
from time import sleep
import json

# Librerías de Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Se Crea la Clase SheetsLoggerHandler que Hereda de logging.Handler
class SheetsLoggerHandler(logging.Handler):
    def __init__(self,spreadsheet_id: str, sheet_name: str = "Logs", level: int = 0):
        super().__init__(level)

        # Obtenemos el String de las Credenciales
        creds_info = secrets["MI_JSON"]
        # Volvemos las Credenciales en un Diccionario
        creds = json.loads(creds_info)
        # Creamos las Credenciales de Google a Partir del Diccionario
        credentials = Credentials.from_service_account_info(creds)

        # Iniciamos una Cola para Almacenar los Logs que se Quieren Enviar a Sheets
        self.log_queue = queue.Queue()
        # Definimos los Colores para Cada Nivel de Log (Opcional, para Mejorar la Visualización en Sheets)
        self.levelColors = {
            "DEBUG":    {"red": 0.9, "green": 0.9, "blue": 0.9}, # Light Grey
            "INFO":     {"red": 0.8, "green": 1.0, "blue": 0.8}, # Light Green
            "WARNING":  {"red": 1.0, "green": 0.9, "blue": 0.6}, # Orange/Yellow
            "ERROR":    {"red": 1.0, "green": 0.7, "blue": 0.7}, # Light Red
            "CRITICAL": {"red": 1.0, "green": 0.0, "blue": 0.0}, # Bright Red
        }

        # 2. Start the background worker thread
        self.worker_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()

        try:
            # Nos Conectamos a Google Sheets usando gspread y las Credenciales
            client = gspread.authorize(credentials)
            # Abrimos la Hoja de Cálculo por su ID
            self.worksheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
            print(f"Conectado a Google Sheets: {sheet_name} en {spreadsheet_id}")
        except Exception as e:
            print(f"Error al conectar con Google Sheets: {e}")
            self.worksheet = None
    
    def format(self, record):
        # Se crea la Fila para Subir a Sheets con la Información del Log
        row = [
            datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            record.levelname,
            record.name,
            record.getMessage()
        ]
        return row

    def emit(self, record):
        """Standard logging method: just drops the record into the queue."""
        if self.worksheet:
            self.log_queue.put(record)
    
    def _process_logs(self):
        """The background worker that talks to Google Sheets."""
        while True:
            try:
                # Wait for a log to appear in the queue
                record = self.log_queue.get()
                if record is None: break # Shutdown signal
                
                self._send_to_sheets(record)
                
                self.log_queue.task_done()
                # Optional: slight sleep to avoid hitting Google API rate limits
                sleep(0.5) 
            except Exception as e:
                print(f"Error in Logging Worker: {e}")

    def _send_to_sheets(self, record):
        """Sends a single log record to Google Sheets."""
        try:
            rowVals = self.format(record)
            # Append the log entry as a new row in the sheet
            self.worksheet.append_row(rowVals, value_input_option='USER_ENTERED')
            # Get the index of the newly added row (assuming it was added at the end)
            last_row_index = len(self.worksheet.get_all_values())
            # Apply color formatting based on log level
            self._apply_color_formatting(last_row_index, record.levelname)
        except Exception as e:
            print(f"Error sending log to Sheets: {e}")

    def _apply_color_formatting(self, row_index, levelname):
        """Dedicated method for cell styling."""
        color = self.levelColors.get(levelname, {"red": 1, "green": 1, "blue": 1})
        
        # Target Column B (where the level name is)
        self.worksheet.format(f"B{row_index}", {
            "backgroundColor": color,
            "textFormat": {"bold": True, "foregroundColor": {"red": 0, "green": 0, "blue": 0}}
        })