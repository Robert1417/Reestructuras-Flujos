# Esta será una clase para guardar toda la Información relacionada con el Flujo
# de Berex (pagos del cliente sostenidos en el tiempo)

# Librerías Neceasarias
import pandas as pd

# Importamos el Logger
from calculator.app import debugLogger

# Se crea la clase de FlujoBerex
class FlujoBerex:
    # Clase Auxiliar para Guardar cada Factura Individual
    class Factura:
        def __init__(self, fecha: pd.Timestamp, monto: float, destino: str):
            self.fecha = fecha
            self.monto = monto
            self.destino = destino
    
    # La Clase se inicializa con un DataFrame de Facturas, el cual se convierte en una lista de Objetos Factura para facilitar su manejo
    def __init__(self,ref: str, dfFacturas: pd.DataFrame):
        self.ref = ref
        self.facturas = []
        # Ordenamos el DataFrame por Fecha para asegurar que el Flujo se maneje en orden cronológico
        dfFacturas = dfFacturas.sort_values(by='Fecha_Pago_Berex')

        for index, row in dfFacturas.iterrows():
            factura = self.Factura(row['Fecha_Pago_Berex'], row['amount'], row['destination'])
            self.facturas.append(factura)
        
        # Hacemos Registro de Log
        debugLogger.info(f"FlujoBerex inicializado con {len(self.facturas)} facturas para la referencia {self.ref}.")

    # Método para obtener todas las Facturas como un DataFrame
    def getFacturasDF(self) -> pd.DataFrame:
        data = {
            'Fecha_Pago_Berex': [factura.fecha for factura in self.facturas],
            'amount': [factura.monto for factura in self.facturas],
            'destination': [factura.destino for factura in self.facturas]
        }
        debugLogger.info(f"DataFrame de facturas generado con {len(data['Fecha_Pago_Berex'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener las Facturas no Pagadas dado un Monto Pagado
    def getFacturasNoPagadas(self, montoPagado: float) -> pd.DataFrame:
        montoAcumulado = 0.0
        facturasNoPagadas = []

        for factura in self.facturas:
            montoAcumulado += factura.monto
            if montoAcumulado > montoPagado:
                facturasNoPagadas.append(factura)

        data = {
            'Fecha_Pago_Berex': [factura.fecha for factura in facturasNoPagadas],
            'amount': [factura.monto for factura in facturasNoPagadas],
            'destination': [factura.destino for factura in facturasNoPagadas]
        }
        debugLogger.info(f"DataFrame de facturas no pagadas generado con {len(data['Fecha_Pago_Berex'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener el Monto Total de las Facturas
    def getMontoTotal(self) -> float:
        montoTotal = sum(factura.monto for factura in self.facturas)
        debugLogger.info(f"Monto total de facturas calculado: {montoTotal} para la referencia {self.ref}.")
        return montoTotal

    # Método para Obtener la Última Factura sin Pagar dado un Monto Pagado
    def getUltimaFacturaNoPagada(self, montoPagado: float):
        montoAcumulado = 0.0
        ultimaFacturaNoPagada = None

        for factura in self.facturas:
            montoAcumulado += factura.monto
            if montoAcumulado > montoPagado:
                ultimaFacturaNoPagada = factura
                break

        if ultimaFacturaNoPagada:
            debugLogger.info(f"Última factura no pagada encontrada: Fecha {ultimaFacturaNoPagada.fecha}, Monto {ultimaFacturaNoPagada.monto}, Destino {ultimaFacturaNoPagada.destino} para la referencia {self.ref}.")
        else:
            debugLogger.info(f"No se encontraron facturas no pagadas para la referencia {self.ref} con el monto pagado de {montoPagado}.")

        return ultimaFacturaNoPagada