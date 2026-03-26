# Esta será una clase para guardar toda la Información relacionada con el Flujo
# de Berex (pagos del cliente sostenidos en el tiempo)

# Librerías Neceasarias
from typing import Tuple
import pandas as pd

# Importamos el Logger
from calculator.app import debugLogger

# Se crea la clase de FlujoBerex
class FlujoBerex:
    # Clase Auxiliar para Guardar cada Factura Individual
    class Factura:
        def __init__(self, fecha: pd.Timestamp, monto: float, destino: str, pago: float = 0.0):
            self.fecha = fecha
            self.monto = monto
            self.destino = destino
            self.pago = pago

        # Método para Representar la Factura como String (para facilitar su visualización en los logs)
        def __str__(self):
            return f"Factura(Fecha: {self.fecha}, Monto: {self.monto}, Destino: {self.destino}, Pago: {self.pago})"

        # Método para Devolver la Factura como un Diccionario (para facilitar su conversión a DataFrame)
        def to_dict(self):
            return {
                'Fecha_Pago_Berex': self.fecha,
                'Monto_Berex': self.monto,
                'Destino': self.destino,
                'Pago': self.pago,
            }

        # Método para Devolver la Factura como un DataFrame de una sola fila
        def to_dataframe(self):
            return pd.DataFrame([self.to_dict()])
    
    # La Clase se inicializa con un DataFrame de Facturas, el cual se convierte en una lista de Objetos Factura para facilitar su manejo
    def __init__(self,ref: str, dfFacturas: pd.DataFrame|None):
        self.ref = ref
        self.facturas = []
        # Ordenamos el DataFrame por Fecha y Destino para asegurar que el Flujo se maneje en orden cronológico
        if dfFacturas is not None:
            dfFacturas = dfFacturas.sort_values(by=['Fecha_Pago_Berex','Destination'])

            for index, row in dfFacturas.iterrows():
                factura = self.Factura(row['Fecha_Pago_Berex'], row['Monto_Berex'], row['Destino'], row['Pago'])
                self.facturas.append(factura)
            
            # Hacemos Registro de Log
            debugLogger.info(f"FlujoBerex inicializado con {len(self.facturas)} facturas para la referencia {self.ref}.")
        else:
            debugLogger.warning(f"FlujoBerex inicializado sin facturas para la referencia {self.ref}.")

    # Método para Agregar una Nueva Factura al Flujo de Berex
    def agregarFactura(self, fecha: pd.Timestamp, monto: float, destino: str, pago: float = 0.0) -> None:
        nuevaFactura = self.Factura(fecha, monto, destino, pago)
        self.facturas.append(nuevaFactura)
        # Ordenamos la lista de facturas por fecha y destino para mantener el orden cronológico del flujo
        self.facturas.sort(key=lambda x: (x.fecha, x.destino))
        debugLogger.info(f"Nueva factura agregada al flujo de Berex para la referencia {self.ref}: {nuevaFactura}")

    # Método para obtener todas las Facturas como un DataFrame
    def getFacturasDF(self) -> pd.DataFrame:
        data = {
            'Fecha_Pago_Berex': [factura.fecha for factura in self.facturas],
            'Monto_Berex': [factura.monto for factura in self.facturas],
            'Destino': [factura.destino for factura in self.facturas],
            'Pago': [factura.pago for factura in self.facturas],
        }
        debugLogger.info(f"DataFrame de facturas generado con {len(data['Fecha_Pago_Berex'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener el Monto Total de las Facturas
    def getMontoTotal(self) -> float:
        montoTotal = sum(factura.monto for factura in self.facturas)
        debugLogger.info(f"Monto total de facturas calculado: {montoTotal} para la referencia {self.ref}.")
        return montoTotal

    # Método para Obtener el Monto Total Pagado
    def getMontoPagado(self) -> float:
        montoPagado = sum(factura.pago for factura in self.facturas)
        debugLogger.info(f"Monto total pagado calculado: {montoPagado} para la referencia {self.ref}.")
        return montoPagado

    # Método para Obtener el Monto Total Pendiente
    def getMontoPendiente(self) -> float:
        montoPendiente = self.getMontoTotal() - self.getMontoPagado()
        debugLogger.info(f"Monto pendiente calculado: {montoPendiente} para la referencia {self.ref}.")
        return montoPendiente

    # Método para Obtener las Facturas de un Mes Específico
    def getFacturasMes(self, mes: pd.Timestamp):
        facturas_del_mes = []
        for factura in self.facturas:
            if factura.fecha.month == mes.month and factura.fecha.year == mes.year:
                facturas_del_mes.append(factura)
        debugLogger.info(f"Facturas encontradas para el mes {mes.month}/{mes.year}: {len(facturas_del_mes)} para la referencia {self.ref}.")
        return facturas_del_mes

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
            'Monto_Berex': [factura.monto for factura in facturasNoPagadas],
            'Destino': [factura.destino for factura in facturasNoPagadas],
            'Pago': [factura.pago for factura in facturasNoPagadas],
        }
        debugLogger.info(f"DataFrame de facturas no pagadas generado con {len(data['Fecha_Pago_Berex'])} filas para la referencia {self.ref}.")
        return pd.DataFrame(data)

    # Método para Obtener la Última Factura sin Pagar dado un Monto Pagado
    def getUltimaFacturaNoPagada(self, montoPagado: float) -> Tuple[Factura,float]:
        montoAcumulado = 0.0
        ultimaFacturaNoPagada = None

        for factura in self.facturas:
            montoAcumulado += factura.monto
            if montoAcumulado > montoPagado:
                ultimaFacturaNoPagada = factura
                ultimoValorNoPago = montoAcumulado - montoPagado
                break

        if ultimaFacturaNoPagada:
            debugLogger.info(f"Última factura no pagada encontrada: Fecha {ultimaFacturaNoPagada.fecha}, Monto {ultimaFacturaNoPagada.monto}, Destino {ultimaFacturaNoPagada.destino} para la referencia {self.ref}.")
        else:
            debugLogger.info(f"No se encontraron facturas no pagadas para la referencia {self.ref} con el monto pagado de {montoPagado}.")

        return ultimaFacturaNoPagada, ultimoValorNoPago

    # Método para Obtener el Monto Total No Pagado con Destino == 'bank'
    def getMontoNoPagadoBanco(self) -> float:
        montoAcumulado = 0
        montoNoPagadoBanco = 0
        montoPagado = self.getMontoPagado()
        for factura in self.facturas:
            montoAcumulado += factura.monto
            if montoAcumulado > montoPagado and factura.destino == 'bank':
                montoNoPagadoBanco += factura.monto

        debugLogger.info(f"Monto no pagado con destino a banco calculado: {montoNoPagadoBanco} para la referencia {self.ref}.")
        return montoNoPagadoBanco

    # Método para Obtener el Monto Total No Pagado con Destino == 'commission'
    def getMontoNoPagadoCommission(self) -> float:
        montoAcumulado = 0
        montoNoPagadoCommission = 0
        montoPagado = self.getMontoPagado()
        for factura in self.facturas:
            montoAcumulado += factura.monto
            if montoAcumulado > montoPagado and factura.destino == 'commission':
                montoNoPagadoCommission += factura.monto

        debugLogger.info(f"Monto no pagado con destino a comisión calculado: {montoNoPagadoCommission} para la referencia {self.ref}.")
        return montoNoPagadoCommission