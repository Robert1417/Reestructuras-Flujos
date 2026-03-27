# Clase para Controlar los Diferentes Flujos de las Mensualidades

# Librerias Necesarias
import pandas as pd

# Importamos el Logger
from src.calculator.utils.logger_setup import debugLogger

# Creamos la Clase de FlujoMensualidades
class FlujoMensualidades:
    # Clase Auxiliar para Guardar cada Mensualidad Individual
    class Mensualidad:
        def __init__(self, fecha: pd.Timestamp, monto: float):
            self.fecha = fecha
            self.monto = monto
    
    # La Clase se inicializa con un DataFrame de Mensualidades, el cual se convierte en una lista de Objetos Mensualidad para facilitar su manejo
    def __init__(self,ref: str, dfMensualidades: pd.DataFrame):
        self.ref = ref
        self.mensualidades = []
        # Ordenamos el DataFrame por Fecha para asegurar que el Flujo se maneje en orden cronológico
        dfMensualidades = dfMensualidades.sort_values(by='Fecha_Mensualidad')

        for index, row in dfMensualidades.iterrows():
            # Si la Mensualidad la Columna Status_Facturacion no es POR_COBRAR se ignora
            if row['Status_Facturacion'] != 'POR_COBRAR':
                continue
            mensualidad = self.Mensualidad(row['Fecha_Mensualidad'], row['Monto_Mensualidad'])
            self.mensualidades.append(mensualidad)
        
        # Hacemos Registro de Log
        debugLogger.info(f"FlujoMensualidades inicializado con {len(self.mensualidades)} mensualidades para la referencia {self.ref}.")

    # Método para Obtener todas las Mensualidades como un DataFrame
    def getMensualidadesDF(self) -> pd.DataFrame:
        data = {
            'Fecha_Mensualidad': [mensualidad.fecha for mensualidad in self.mensualidades],
            'Monto_Mensualidad': [mensualidad.monto for mensualidad in self.mensualidades]
        }
        debugLogger.info(f"DataFrame de mensualidades generado con {len(data['Fecha_Mensualidad'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener las Mensualidades menores a una Fecha dada
    def getMensualidadesMenoresFecha(self, fechaLimite: pd.Timestamp) -> pd.DataFrame:
        mensualidadesFiltradas = [mensualidad for mensualidad in self.mensualidades if mensualidad.fecha < fechaLimite]

        data = {
            'Fecha_Mensualidad': [mensualidad.fecha for mensualidad in mensualidadesFiltradas],
            'Monto_Mensualidad': [mensualidad.monto for mensualidad in mensualidadesFiltradas]
        }
        debugLogger.info(f"DataFrame de mensualidades menores a {fechaLimite} generado con {len(data['Fecha_Mensualidad'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)
    
    # Método para Obtener las Mensualidades mayores o iguales a una Fecha dada
    def getMensualidadesMayoresIgualesFecha(self, fechaLimite: pd.Timestamp) -> pd.DataFrame:
        mensualidadesFiltradas = [mensualidad for mensualidad in self.mensualidades if mensualidad.fecha >= fechaLimite]

        data = {
            'Fecha_Mensualidad': [mensualidad.fecha for mensualidad in mensualidadesFiltradas],
            'Monto_Mensualidad': [mensualidad.monto for mensualidad in mensualidadesFiltradas]
        }
        debugLogger.info(f"DataFrame de mensualidades mayores o iguales a {fechaLimite} generado con {len(data['Fecha_Mensualidad'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener el Monto Total de las Mensualidades
    def getMontoTotal(self) -> float:
        montoTotal = sum(mensualidad.monto for mensualidad in self.mensualidades)
        debugLogger.info(f"Monto total de mensualidades calculado: {montoTotal} para la referencia {self.ref}.")
        return montoTotal

    # Método para Obtener las Mensualidades de un Mes y Año Específicos
    def getMensualidadesMesAno(self, mes: int, ano: int) -> pd.DataFrame:
        mensualidadesFiltradas = [mensualidad for mensualidad in self.mensualidades if mensualidad.fecha.month == mes and mensualidad.fecha.year == ano]

        data = {
            'Fecha_Mensualidad': [mensualidad.fecha for mensualidad in mensualidadesFiltradas],
            'Monto_Mensualidad': [mensualidad.monto for mensualidad in mensualidadesFiltradas]
        }
        debugLogger.info(f"DataFrame de mensualidades para el mes {mes} y año {ano} generado con {len(data['Fecha_Mensualidad'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener el Monto de las Mensualidades de un Mes y Año Específicos
    def getMontoMensualidadesMesAno(self, mes: int, ano: int) -> float:
        montoMensualidades = sum(mensualidad.monto for mensualidad in self.mensualidades if mensualidad.fecha.month == mes and mensualidad.fecha.year == ano)
        debugLogger.info(f"Monto total de mensualidades para el mes {mes} y año {ano} calculado: {montoMensualidades} para la referencia {self.ref}.")
        return montoMensualidades

    # Método para Obtener el Monto de las Mensualidades Menores a un Mes y Año Específicos
    def getMontoMensualidadesMenoresMesAno(self, mes: int, ano: int) -> float:
        montoMensualidades = sum(mensualidad.monto for mensualidad in self.mensualidades if (mensualidad.fecha.year < ano) or (mensualidad.fecha.year == ano and mensualidad.fecha.month <= mes))
        debugLogger.info(f"Monto total de mensualidades menores al mes {mes} y año {ano} calculado: {montoMensualidades} para la referencia {self.ref}.")
        return montoMensualidades