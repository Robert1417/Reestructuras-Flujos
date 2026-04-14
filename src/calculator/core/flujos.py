# Este Archivo Contendrá toda la Información Relacionada con cada uno de los Flujos 
# En Especial para calcular el Nuevo Flujo según la Reestructura

# Librerías Core
import pandas as pd
import numpy as np

# Librería de Typing
from typing import Tuple

# Librerías de Ayuda
from src.calculator.utils.logger_setup import notInfiniteLog, logClassWrapper
from src.calculator.utils.data_load import addSaldoPendienteToBerex, emptyBerex, filterDataByMonth
from src.calculator.utils.helpers import getNextMonthDay

# Creamos Clase de FlujoTotal, que contiene Información de:
# - El Flujo de las Moras
# - El Flujo de las Mensualidades
# - El Flujo de Berex
class FlujoTotal:
    def __init__(self,ref: str, moras: pd.DataFrame, berex: pd.DataFrame, mensualidades: pd.DataFrame):
        self.ref = ref
        self.moras = moras
        self.berex = berex
        self.mensualidades = mensualidades

        self.nuevoFlujo = None # Inicializamos el Nuevo Flujo como None, ya que aún no se ha calculado
        self.motivoNoViable = None # Inicializamos el Motivo de No Viabilidad como None, ya que aún no se ha evaluado la viabilidad de la reestructura

        # Método para Calcular el Valor Total Pagado por el Cliente
    @logClassWrapper(message="Error al Calcular el Monto Pagado por el Cliente", onErrorValue=0.0)
    def calcularTotalPagado(self) -> float:
        """Método para Calcular el Valor Total Pagado por el Cliente

        Returns:
            float: El Valor Total Pagado por el Cliente
        """        
        montoPagado = self.moras['Pago'].sum()
        notInfiniteLog(f"Monto_Pagado_{self.ref}", f"El Monto Pagado por el Cliente es: {montoPagado}")
        return montoPagado

    # Método para Obtener el Flujo de Berex
    @logClassWrapper(message="Error al Obtener el Flujo de Berex", onErrorValue=emptyBerex)
    def obtenerFlujoBerex(self) -> pd.DataFrame:
        """Método para Obtener el Flujo de Berex

        Returns:
            pd.DataFrame: El Flujo de Berex del Cliente
        """
        return self.berex.copy()

    # Método para Calcular si el Nuevo Flujo ya se calculó
    def isNuevoFlujoCalculated(self) -> bool:
        """Método para Calcular si el Nuevo Flujo ya se calculó

        Returns:
            bool: True si el Nuevo Flujo ya se calculó, False en caso contrario
        """
        return not(self.nuevoFlujo is None)

    # Método para Obtener el Motivo del Error en caso de que el Nuevo Flujo no se haya Calculado Correctamente
    def getErrorMessage(self) -> str:
        """Método para Obtener el Motivo del Error en caso de que el Nuevo Flujo no se haya Calculado Correctamente

        Returns:
            str: El Motivo del Error en caso de que el Nuevo Flujo no se haya Calculado Correctamente
        """
        if self.isNuevoFlujoCalculated():
            return "No se ha Encontrado un Error, el Nuevo Flujo se ha Calculado Correctamente"
        if self.motivoNoViable is not None:
            return self.motivoNoViable
        return "No se ha Encontrado un Motivo Específico para el Error, verificar los Parámetros de la Reestructura y los Datos del Cliente"
    
    # Método para saber si el Nuevo Flujo es Viable o No Viable
    def isNuevoFlujoViable(self) -> bool:
        """Método para saber si el Nuevo Flujo es Viable o No Viable

        Returns:
            bool: True si el Nuevo Flujo es Viable, False en caso contrario
        """
        # Falta Implementación, por el Momento se Define que el Nuevo Flujo es Viable si se ha Calculado Correctamente, y No Viable si no se ha Calculado Correctamente, pero esto se puede Mejorar Agregando Criterios Específicos para Determinar la Viabilidad del Nuevo Flujo
        return self.isNuevoFlujoCalculated()

    # Método para Calcular el Valor Total Por Cobrar al Cliente
    @logClassWrapper(message="Error al Calcular el Monto Por Cobrar al Cliente", onErrorValue=0.0)
    def calcularTotalPorCobrar(self) -> float:
        """Método para Calcular el Valor Total Por Cobrar al Cliente

        Returns:
            float: El Valor Total Por Cobrar al Cliente
        """
        montoPorCobrar = self.berex['Monto_Berex'].sum()
        notInfiniteLog(f"Monto_Por_Cobrar_{self.ref}", f"El Monto Por Cobrar al Cliente es: {montoPorCobrar}")
        return montoPorCobrar

    # Método para Calcular el Monto_Mensualidad no Pagada por el Cliente
    @logClassWrapper(message="Error al Calcular el Monto No Pagado por el Cliente", onErrorValue=0.0)
    def calcularMensualidadesNoPagadas(self, fechaCorte: pd.Timestamp) -> float:
        """Método para Calcular el Monto_Mensualidad no Pagada por el Cliente

        Args:
            fechaCorte (pd.Timestamp): La Fecha de Corte para Considerar las Mensualidades No Pagadas

        Returns:
            float: El Monto Total de Mensualidades No Pagadas por el Cliente
        """
        # Primero Dejamos fechaCorte como el Último Día del Mes para Evitar Problemas con las Mensualidades que Tienen Fecha de Cobro a Final de Mes
        fechaCorte = fechaCorte.replace(day=1) + pd.offsets.MonthEnd(0)
        # Filtramos las Mensualidades que Tienen Fecha de Cobro Menor o Igual a la Fecha de Corte, lo que Indica que el Cliente No las ha Pagado, y Sumamos el Monto_Mensualidad de esas Mensualidades No Pagadas para Obtener el Monto Total No Pagado por el Cliente
        mensualidadesNoPagadas = self.mensualidades[self.mensualidades['Fecha_Cobro'].dt.date() <= fechaCorte.date()]
        # Ahora Filtramos las Mensualidades que Status_Facturacion == "POR_COBRAR"
        mensualidadesNoPagadas = mensualidadesNoPagadas[mensualidadesNoPagadas['Status_Facturacion'] == "POR_COBRAR"]
        montoNoPagado = mensualidadesNoPagadas['Monto_Mensualidad'].sum()
        notInfiniteLog(f"Monto_No_Pagado_{self.ref}", f"El Monto No Pagado por el Cliente es: {montoNoPagado}")
        return montoNoPagado

    # Método para Obtener las Facturas No Pagadas por el Cliente
    @logClassWrapper(message="Error al Obtener las Facturas No Pagadas por el Cliente", onErrorValue=emptyBerex)
    def obtenerFacturasNoPagadas(self) -> pd.DataFrame:
        """Método para Obtener las Facturas No Pagadas por el Cliente

        Returns:
            pd.DataFrame: Un DataFrame con las Facturas No Pagadas por el Cliente
        """
        # Solo tenemos que Filtrar el Flujo de Berex por las Facturas que Tienen Saldo_Pendiente Mayor a 0, lo que Indica que el Cliente No las ha Pagado
        facturasNoPagadas = self.berex[self.berex['Saldo_Pendiente'] > 0].copy()
        return facturasNoPagadas

    # Método para Obtener las Facturas Pagadas
    @logClassWrapper(message="Error al Obtener las Facturas Pagadas por el Cliente", onErrorValue=emptyBerex)
    def obtenerFacturasPagadas(self) -> pd.DataFrame:
        """Método para Obtener las Facturas Pagadas por el Cliente

        Returns:
            pd.DataFrame: Un DataFrame con las Facturas Pagadas por el Cliente
        """
        # Filtramos los Datos donde el Saldo_Pendiente sea menor al Monto_Berex, lo cual Indicaria un Pago
        facturasPagadas = self.berex[self.berex['Saldo_Pendiente'] < self.berex['Monto_Berex']].copy()
        # Ahora para las Facturas donde Saldo_Pendiente sea diferente a 0, se asigna:
        # Monto_Berex = Monto_Berex - Saldo_Pendiente, lo que Indica el Monto que el Cliente ha Pagado de esa Factura
        # Saldo_Pendiente = 0, lo que Indica que el Cliente ha Pagado esa Factura
        maskPagoIncompleto = facturasPagadas['Saldo_Pendiente'] > 0
        facturasPagadas.loc[maskPagoIncompleto, 'Monto_Berex'] = facturasPagadas.loc[maskPagoIncompleto, 'Monto_Berex'] - facturasPagadas.loc[maskPagoIncompleto, 'Saldo_Pendiente']
        facturasPagadas.loc[maskPagoIncompleto, 'Saldo_Pendiente'] = 0

        # Ahora Vamos a Agrupar las Facturas Pagadas por Destino, dejando la Última Fecha_Pago_Berex, y la suma del resto
        facturasPagadas = facturasPagadas.groupby('Destino').agg({
            'Referencia': 'first',
            'Fecha_Pago_Berex': 'max',
            'Monto_Berex': 'sum',
            'Saldo_Pendiente': 'sum'
        }).reset_index()

        return facturasPagadas

    # Método para Obtener el Monto de Berex de las Facturas No Pagadas con Destino Banco
    @logClassWrapper(message="Error al Obtener el Monto de Berex de las Facturas No Pagadas con Destino Banco", onErrorValue=0.0)
    def obtenerMontoBancoFacturasNoPagadas(self) -> float:
        """Método para Obtener el Monto de Berex de las Facturas No Pagadas con Destino Banco

        Returns:
            float: El Monto de Berex de las Facturas No Pagadas con Destino Banco
        """
        facturasNoPagadas = self.obtenerFacturasNoPagadas()
        montoBanco = facturasNoPagadas[facturasNoPagadas['Destino'] == 'Banco']['Saldo_Pendiente'].sum()
        notInfiniteLog(f"Monto_Banco_Facturas_No_Pagadas_{self.ref}", f"El Monto de Berex de las Facturas No Pagadas con Destino Banco es: {montoBanco}", method='debug')
        return montoBanco
    
    # Método para Obtener el Monto de Berex de las Facturas No Pagadas con Destino Comision
    @logClassWrapper(message="Error al Obtener el Monto de Berex de las Facturas No Pagadas con Destino Comision", onErrorValue=0.0)
    def obtenerMontoComisionFacturasNoPagadas(self) -> float:
        """Método para Obtener el Monto de Berex de las Facturas No Pagadas con Destino Comision

        Returns:
            float: El Monto de Berex de las Facturas No Pagadas con Destino Comision
        """
        facturasNoPagadas = self.obtenerFacturasNoPagadas()
        montoComision = facturasNoPagadas[facturasNoPagadas['Destino'] == 'Comision']['Saldo_Pendiente'].sum()
        notInfiniteLog(f"Monto_Comision_Facturas_No_Pagadas_{self.ref}", f"El Monto de Berex de las Facturas No Pagadas con Destino Comision es: {montoComision}", method='debug')
        return montoComision

    # Método para Obtener la Última Fecha de Pago del Cliente
    @logClassWrapper(message="Error al Obtener la Última Fecha de Pago del Cliente", onErrorValue=pd.Timestamp.today().normalize())
    def obtenerUltimaFechaPago(self) -> pd.Timestamp:
        """Método para Obtener la Última Fecha de Pago del Cliente

        Returns:
            pd.Timestamp: La Última Fecha de Pago del Cliente
        """
        if self.moras.empty:
            notInfiniteLog(f"Ultima_Fecha_Pago_{self.ref}", f"No se han Encontrado Pagos por el Cliente, se Devuelve la Fecha Actual", method='debug')
            return pd.Timestamp.today().normalize()
        # Obtenemos las Facturas No Pagadas
        facturasNoPagadas = self.obtenerFacturasNoPagadas()
        if not facturasNoPagadas.empty:
            # Dejamos la Ultima Fecha de Pago como la Primera Factura sin Pagar, ya que eso Indica que el Cliente No ha Pagado esa Factura, por lo que la Última Fecha de Pago del Cliente sería la Fecha de Pago de esa Factura
            ultimaFechaPago = facturasNoPagadas['Fecha_Pago_Berex'].min()
            notInfiniteLog(f"Ultima_Fecha_Pago_{self.ref}", f"La Última Fecha de Pago del Cliente es: {ultimaFechaPago}", method='debug')
            return ultimaFechaPago
        return pd.Timestamp.today().normalize()

    # Método para Calcular el Nuevo Flujo de Berex según la Reestructura
    @logClassWrapper(message="Error al Calcular el Nuevo Flujo de Berex", onErrorValue=emptyBerex)
    def calcularNuevoFlujoBerex(self, paramsReestructura: dict) -> pd.DataFrame:
        """Método para Calcular el Nuevo Flujo de Berex según la Reestructura

        Args:
            paramsReestructura (dict): Un Diccionario con los Parámetros de la Reestructura

        Returns:
            pd.DataFrame: Un DataFrame con el Nuevo Flujo de Berex según la Reestructura
        """
        notInfiniteLog(f"calculating_nuevo_flujo_berex_{self.ref}", f"Calculando el Nuevo Flujo de Berex para la Referencia {self.ref} con los Parámetros: {paramsReestructura}")

        # Guardamos los Párametros de la Reestructura
        self.paramsReestructura = paramsReestructura

        # Se dividen los Parámetros Individualmente
        montoInicalReestructura = paramsReestructura.get('Monto_Inicial_Reestructura', 0)
        nuevoApartadoMensualidad = paramsReestructura.get('Nuevo_Apartado_Mensual', 0)
        fechaInicioReestructura = paramsReestructura.get('Fecha_Inicio_Reestructura', pd.Timestamp.today().normalize())

        # Se crea un Diccionario para Guardar la Información del Nuevo Flujo de Berex
        nuevoFlujoDict = {col: [] for col in self.berex.columns}

        # Se crean variables Auxiliares
        primeraFactura = True
        numeroFactura = 1

        # Se Obtienen las Facturas No Pagadas por el Cliente
        facturasNoPagadas = self.obtenerFacturasNoPagadas()
        if facturasNoPagadas.empty:
            notInfiniteLog(f"nuevo_flujo_berex_{self.ref}", f"No se han Encontrado Facturas No Pagadas por el Cliente, el Nuevo Flujo de Berex será Igual al Flujo de Berex Original", method='debug')
            self.nuevoFlujo = self.berex.copy()
            # Actualizamos el Motivo de No Viabilidad
            self.motivoNoViable = "No se han Encontrado Facturas No Pagadas por el Cliente, por lo que no se puede Realizar la Reestructura"
            notInfiniteLog(f"motivo_no_viable_{self.ref}", f"{self.motivoNoViable}", method='debug')
            return self.nuevoFlujo
        
        # Se Obtienen los Saldos Pendientes de Comision y Banco de las Facturas No Pagadas por el Cliente
        montoBancoFacturasNoPagadas = self.obtenerMontoBancoFacturasNoPagadas()
        montoComisionFacturasNoPagadas = self.obtenerMontoComisionFacturasNoPagadas()
        # Se Calcula el Monto Pendiente Total de las Facturas No Pagadas por el Cliente, lo que Indica el Monto Total que el Cliente Aún No ha Pagado
        montoPendiente = montoBancoFacturasNoPagadas + montoComisionFacturasNoPagadas

        # Se crea una Ventana por Mes Empezando por la Fecha de Inicio de la Reestructura
        startWindowDate = fechaInicioReestructura
        currWindow = startWindowDate

        # Empezamos con la Iteración por la Ventana por Mes
        while montoPendiente > 0:
            # Se Define el Monto del Mes que el Cliente Puede Gastar
            saldoMes = nuevoApartadoMensualidad

            # --- Manejo de Mensualidades y Primer Mes de la Reestructura ---
            # Si es Primera Iteración se realiza un Procedimiento Diferente, ya que:
            # - Se tiene en Cuenta el Nuevo monto inicial
            # - Se tiene en Cuenta las Mensualidades Pasadas no pagadas
            if primeraFactura:
                # Se actualiza la variable de Primera Factura
                primeraFactura = False
                # Se Calcula el Monto de Mensualidades Pendientes a la Fecha de Inicio de la Reestructura, lo que Indica el Monto que se Debe Agregar a la Primera Factura para Obtener el Nuevo Monto de la Primera Factura
                montoMensualidadesPendientes = self.calcularMensualidadesNoPagadas(currWindow)
                # Si el Monto de las Mensualidades Pendientes supera el Monto de Pago Inicial, significa que no es Viable
                if montoMensualidadesPendientes > montoInicalReestructura:
                    notInfiniteLog(f"nuevo_flujo_berex_{self.ref}", f"El Monto de Mensualidades Pendientes ({montoMensualidadesPendientes}) supera el Monto Inicial de la Reestructura ({montoInicalReestructura}), por lo que no es viable realizar la reestructura", method='debug')
                    self.nuevoFlujo = emptyBerex
                    # Actualizamos el Motivo de No Viabilidad
                    self.motivoNoViable = f"El Monto de Mensualidades Pendientes ({montoMensualidadesPendientes}) supera el Monto Inicial de la Reestructura ({montoInicalReestructura}), por lo que no es viable realizar la reestructura"
                    notInfiniteLog(f"motivo_no_viable_{self.ref}", f"{self.motivoNoViable}", method='debug')
                    return self.nuevoFlujo
                # Como es la Primera Factura, el Saldo del Mes se Define como el Monto Inicial de la Reestructura más el Monto de las Mensualidades Pendientes, lo que Indica el Monto Total que el Cliente Puede Pagar en la Primera Factura
                saldoMes = montoInicalReestructura

                # Al Saldo del Mes se le quita el Monto Pendiente de las Mensualidades Pendientes
                saldoMes -= montoMensualidadesPendientes
            else:
                # Obtenemos los Datos de las Mensualidades de el mes
                mensualidadesMes = filterDataByMonth(self.mensualidades, 'Fecha_Cobro', currWindow)
                # Se Calcula el Monto de Mensualidades del Mes dejando solo datos POR_COBRAR
                montoMensualidadesMes = mensualidadesMes[mensualidadesMes['Status_Facturacion'] == "POR_COBRAR"]['Monto_Mensualidad'].sum()
                # Si el Monto de Mensualidades del Mes supera el Saldo del Mes, significa que no es Viable
                if montoMensualidadesMes > saldoMes:
                    notInfiniteLog(f"nuevo_flujo_berex_{self.ref}", f"El Monto de Mensualidades del Mes ({montoMensualidadesMes}) supera el Saldo del Mes ({saldoMes}), por lo que no es viable realizar la reestructura", method='debug')
                    self.nuevoFlujo = emptyBerex
                    # Actualizamos el Motivo de No Viabilidad
                    self.motivoNoViable = f"El Monto de Mensualidades del Mes ({montoMensualidadesMes}) supera el Saldo del Mes ({saldoMes}), por lo que no es viable realizar la reestructura"
                    notInfiniteLog(f"motivo_no_viable_{self.ref}", f"{self.motivoNoViable}", method='debug')
                    return self.nuevoFlujo
                # Al Saldo del Mes se le quita el Monto Pendiente de las Mensualidades del Mes
                saldoMes -= montoMensualidadesMes
            
            # Manejo de Saldo de Banco
            # Primero Obtenemos el Valor Máximo a Pagar para el Mes de Banco
            maxBancoPayment = min(saldoMes, montoBancoFacturasNoPagadas)
            # Se Resta el Valor Máximo a Pagar para el Mes de Banco al Saldo del Mes y al Monto Pendiente de Banco
            saldoMes -= maxBancoPayment
            montoBancoFacturasNoPagadas -= maxBancoPayment
            # Se agrega el Pago de Banco al Nuevo Flujo de Berex
            if maxBancoPayment > 0:
                nuevoFlujoDict['Referencia'].append(self.ref)
                nuevoFlujoDict['Fecha_Pago_Berex'].append(currWindow)
                nuevoFlujoDict['Monto_Berex'].append(maxBancoPayment)
                nuevoFlujoDict['Destino'].append('Banco')
                nuevoFlujoDict['Saldo_Pendiente'].append(0) # El Saldo_Pendiente se Define como 0, ya que el Cliente Está Pagando el Monto Pendiente de Banco en este Mes
                notInfiniteLog(f"nuevo_flujo_berex_{self.ref}_Factura_{numeroFactura}", f"Se ha Agregado un Pago de Banco al Nuevo Flujo de Berex por un Monto de {maxBancoPayment} en la Fecha {currWindow}", method='debug')
                numeroFactura += 1
            
            # Manejo de Saldo de Comision
            # Primero Obtenemos el Valor Máximo a Pagar para el Mes de Comision
            maxComisionPayment = min(saldoMes, montoComisionFacturasNoPagadas)
            # Se Resta el Valor Máximo a Pagar para el Mes de Comision al Saldo del Mes y al Monto Pendiente de Comision
            saldoMes -= maxComisionPayment
            montoComisionFacturasNoPagadas -= maxComisionPayment
            # Se agrega el Pago de Comision al Nuevo Flujo de Berex
            if maxComisionPayment > 0:
                nuevoFlujoDict['Referencia'].append(self.ref)
                nuevoFlujoDict['Fecha_Pago_Berex'].append(currWindow)
                nuevoFlujoDict['Monto_Berex'].append(maxComisionPayment)
                nuevoFlujoDict['Destino'].append('Comision')
                nuevoFlujoDict['Saldo_Pendiente'].append(0) # El Saldo_Pendiente se Define como 0, ya que el Cliente Está Pagando el Monto Pendiente de Comision en este Mes
                notInfiniteLog(f"nuevo_flujo_berex_{self.ref}_Factura_{numeroFactura}", f"Se ha Agregado un Pago de Comision al Nuevo Flujo de Berex por un Monto de {maxComisionPayment} en la Fecha {currWindow}", method='debug')
                numeroFactura += 1

            # Se Actualiza el Monto Pendiente Restando el Pago Total del Mes (Banco + Comision)
            montoPendiente -= (maxBancoPayment + maxComisionPayment)

            # Se Actualiza la Ventana Sumando un Mes
            currWindow = getNextMonthDay(fechaInicioReestructura.day, currWindow + pd.DateOffset(months=1))
        
        # Una vez que se ha Salido del Ciclo, se Crea el Nuevo Flujo de Berex a Partir del Diccionario del Nuevo Flujo de Berex
        nuevoFlujo = pd.DataFrame(nuevoFlujoDict)
        # Asignamos el Saldo_Pendiente del Nuevo Flujo como el Monto_Berex
        nuevoFlujo['Saldo_Pendiente'] = nuevoFlujo['Monto_Berex']
        # El Flujo Nuevo en Sí seran las Facturas Pagadas + el Nuevo Flujo de Berex
        self.nuevoFlujo = pd.concat([self.obtenerFacturasPagadas(), nuevoFlujo], ignore_index=True).sort_values(by='Fecha_Pago_Berex').reset_index(drop=True)

        notInfiniteLog(f"nuevo_flujo_berex_{self.ref}", f"Se ha Calculado el Nuevo Flujo de Berex para la Referencia {self.ref}", method='debug')
        return self.nuevoFlujo