# Este Código contiene la lógica del Flujo en Berex de un cliente, es decir todas las Facturas
# Estas Facturas las Manejara como una lista de objetos de la clase FacturaBerex,
# y tendrá funciones para agregar facturas, eliminar facturas, y obtener el flujo total del cliente en Berex

# --- Metodos Especiales ---
# 

import pandas as pd

class FlujoBerex:
    def __init__(self,
                referencia,
                debuggingMode=False,
                ):
        self.facturas = []
        self.referencia = referencia
        self.debuggingMode = debuggingMode

    # Función Auxiliar para Ordenar las Facturas
    def ordenarFacturas(self, verbose=False):
        # Se ordena la lista de facturas por fecha de pago y destinoPago
        self.facturas.sort(key=lambda x: (x.fechaPago, x.destino))
        if verbose:
            print("📊Facturas Ordenadas: {} Facturas".format(len(self.facturas)))

    # Función para agregar una factura al flujo
    def agregarFactura(self, factura, verbose=False):
        # Se agrega la Factura a la lista de facturas del flujo
        self.facturas.append(factura)
        # Ahora se va a ordenar la lista de facturas
        self.ordenarFacturas(verbose=verbose)
        if verbose:
            print("✅Factura agregada: {}, 🚹Facturas Totales: {}".format(
                factura.idFactura, 
                len(self.facturas),
                ))
    
    # Función para eliminar una factura del flujo por su id
    def eliminarFactura(self, idFactura, verbose=False):
        # Se itera por cada una de las Facturas
        for factura in self.facturas:
            # Si el Id coincide se elimina la factura de la lista
            if factura.idFactura == idFactura:
                self.facturas.remove(factura)
                if verbose:
                    print("❌Factura eliminada: {}, 🚹Facturas Totales: {}".format(
                        factura.idFactura, 
                        len(self.facturas),
                        ))
                return
        if verbose:
            print("🚧Factura no encontrada: {}, 🚹Facturas Totales: {}".format(
                idFactura, 
                len(self.facturas),
                ))

    # Función para obtener el flujo total del cliente en Berex como DF
    def obtenerFlujoTotal(self, verbose=False):
        # Se crea una lista vacía para almacenar los datos de las facturas
        dfs = [factura.toDF() for factura in self.facturas]
        df = pd.concat(dfs, ignore_index=True)
        # Agregamos la Referencia
        df['Referencia'] = self.referencia
        if verbose:
            print("📊Flujo Total Obtenido: {} Facturas".format(len(df)))
        return df

    # Función para Obtener el flujo total del cliente en Berex como un número (suma de los montos)
    def obtenerFlujoTotalMonto(self, verbose=False):
        total = sum(factura.monto for factura in self.facturas)
        if verbose:
            print("💰Flujo Total Monto: ${}".format(total))
        return total

    # Función para obtener la última factura no pagada dado el monto de pago realizado
    def obtenerUltimaFacturaNoPagada(self, montoPago, verbose=False):
        # Se crea una variable para almacenar el monto acumulado de las facturas pagadas
        montoAcumulado = 0
        # Se itera por cada una de las facturas en orden de fechaPago
        for factura in self.facturas:
            # Se acumula el monto de la factura al monto acumulado
            montoAcumulado += factura.monto
            # Si el monto de la factura es mayor al monto de pago, se devuelve esa factura
            if montoAcumulado > montoPago:
                if verbose:
                    print("📄Última Factura No Pagada: {}, Monto: ${}".format(
                        factura.idFactura, 
                        factura.monto,
                        ))
                return factura
        if verbose:
            print("✅Todas las facturas están pagadas con el monto de pago: ${}".format(montoPago))
        return None

    # Función Auxiliar para Obtener el monto faltante de la última factura no pagada dado el monto de pago realizado
    def obtenerMontoFaltanteUltimaFacturaNoPagada(self, montoPago, verbose=False):
        ultimaFacturaNoPagada = self.obtenerUltimaFacturaNoPagada(montoPago, verbose=verbose)
        if ultimaFacturaNoPagada is not None:
            montoFaltante = montoPago - sum(factura.monto for factura in self.facturas if factura.fechaPago <= ultimaFacturaNoPagada.fechaPago)
            if verbose:
                print("💰Monto Faltante de la Última Factura No Pagada: ${}".format(montoFaltante))
            return montoFaltante
        if verbose:
            print("✅No hay facturas no pagadas, por lo tanto no hay monto faltante.")
        return 0

    # Función para obtener todo el flujo de facturas no pagadas dado el monto de pago realizado
    def obtenerFlujoNoPagado(self, montoPago, verbose=False):
        # Se crea una variable para almacenar el monto acumulado de las facturas pagadas
        montoAcumulado = 0
        # Se crea una lista para almacenar las facturas no pagadas
        facturasNoPagadas = []
        # Se itera por cada una de las facturas en orden de fechaPago
        for factura in self.facturas:
            # Se acumula el monto de la factura al monto acumulado
            montoAcumulado += factura.monto
            # Si el monto de la factura es mayor al monto de pago, se agrega esa factura a la lista de facturas no pagadas
            if montoAcumulado > montoPago:
                facturasNoPagadas.append(factura)
        if verbose:
            print("📄Flujo No Pagado: {} Facturas, Monto Total No Pagado: ${}".format(
                len(facturasNoPagadas), 
                sum(factura.monto for factura in self.facturas) - montoPago,
                ))
        return facturasNoPagadas

    # Función para Crear un Flujo Berex a partir de: montoPago ,nuevaFechaPago y limiteMaxPago
    def crearFlujoBerexDesdePago(self, montoPago, nuevaFechaPago, limiteMaxPago, verbose=False):
        return 1