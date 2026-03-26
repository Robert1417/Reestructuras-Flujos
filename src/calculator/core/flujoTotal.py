# Esta será una clase que manejará el Flujo Total del Cliente, es decir, el Flujo Actual de Berex y el Nuevo Flujo con la Reestructura

# Imports Necesarios
import pandas as pd

# Imports Adicionales
from src.calculator.core import FlujoMensualidades, FlujoBerex

# Importamos el Logger para Mostrar los Logs de la Clase
from src.calculator.app import debugLogger

# Creamos la Clase FlujoTotal
class FlujoTotal:
    # La clase se inicializa con los DataFrames de Moras y Mensualidades
    def __init__(self, ref: str, dfMoras: pd.DataFrame, dfMensualidades: pd.DataFrame):
        self.newFlowCalculated = False # Este atributo se usará para Saber si el Nuevo Flujo ya ha sido Calculado o no
        self.ref = ref
        self.dfMoras = dfMoras
        self.dfMensualidades = dfMensualidades
        debugLogger.debug('FlujoTotal inicializado con mensualidades y moras para la referencia {}'.format(ref))

        # Ahora que tenemos los DFs, inicializamos el Flujo de Mensualidades y el Flujo de Berex
        self.flujoMensualidades = FlujoMensualidades(ref, dfMensualidades)
        self.flujoBerex = FlujoBerex(ref, dfMoras)
        debugLogger.debug('FlujoMensualidades y FlujoBerex inicializados dentro de FlujoTotal para la referencia {}'.format(ref))

    # Método para Obtener el Flujo Total de un Mes
    def getFlujoTotalMes(self, mes: pd.Timestamp) -> float:
        # Aquí se implementará la lógica para obtener el flujo total de un mes específico, sumando el flujo de mensualidades y el flujo de Berex para ese mes
        debugLogger.debug('Obteniendo flujo total para el mes {} de la referencia {}'.format(mes.strftime('%m/%Y'), self.ref))
        # Por ahora, solo devolvemos 0.0 como placeholder
        return 0.0

    # Método para calcular el Nuevo Flujo Total con la Reestructura
    def calcularNuevoFlujo(self, nuevo_apartado_mensual: float, nuevo_pago_inicial: float, fecha_inicio_pago: pd.Timestamp) -> pd.DataFrame:
        # Aquí se implementará la lógica para calcular el nuevo flujo total con la reestructura
        # Esto incluirá ajustar las mensualidades y los pagos del flujo de Berex según los nuevos parámetros
        # El resultado será un DataFrame que combine el nuevo flujo de mensualidades y el flujo de Berex ajustado
        debugLogger.debug('Calculando nuevo flujo total para la referencia {}'.format(self.ref))
        # Por ahora, solo devolvemos un DataFrame vacío como placeholder
        return pd.DataFrame()