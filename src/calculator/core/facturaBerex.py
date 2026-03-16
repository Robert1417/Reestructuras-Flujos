# Esta será la clase que contendrá los datos de la factura en Berex
# Contendrá los siguientes datos:
# - Id de Factura
# - Referencia de Deuda
# - Destino de Pago
# - Monto de Pago
# - Fecha de Pago
# - Fecha de Originación

import pandas as pd

class FacturaBerex:
    def __init__(self, idFactura, 
                idDeuda, 
                destinoPago, 
                monto, 
                fechaPago, 
                fechaOrigen,
                ):
        self.idFactura = idFactura
        self.idDeuda = idDeuda
        self.destino = destinoPago
        self.monto = monto
        self.fechaPago = fechaPago
        self.fechaOrigen = fechaOrigen

    # Función de Comparación Eq
    def __eq__(self, other):
        if isinstance(other, FacturaBerex):
            return self.idFactura == other.idFactura
        return False

    # Función para Actualizar la factura con nuevos datos (excepto el id)
    def actualizar(self, idDeuda=None, destinoPago=None, monto=None, fechaPago=None, fechaOrigen=None):
        if idDeuda is not None:
            self.idDeuda = idDeuda
        if destinoPago is not None:
            self.destino = destinoPago
        if monto is not None:
            self.monto = monto
        if fechaPago is not None:
            self.fechaPago = fechaPago
        if fechaOrigen is not None:
            self.fechaOrigen = fechaOrigen

    # Función para convertir la factura a un dataframe de pandas
    def toDF(self):
        data = {
            'id': [self.idFactura],
            'Id_Deuda': [self.idDeuda],
            'destino': [self.destino],
            'monto': [self.monto],
            'Fecha_Pago': [self.fechaPago],
            'Fecha_Origen': [self.fechaOrigen]
        }
        return pd.DataFrame(data)