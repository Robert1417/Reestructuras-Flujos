# Esta será una clase que manejará el Flujo Total del Cliente, es decir, el Flujo Actual de Berex y el Nuevo Flujo con la Reestructura

# Imports Necesarios
import pandas as pd

# Imports Adicionales
from src.calculator.core import FlujoMensualidades, FlujoBerex
from typing import Tuple

# Importamos el Logger para Mostrar los Logs de la Clase
from src.calculator.app import debugLogger
from src.calculator.utils.helpers import notInfinteLog

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

    # Método Oculto para Calcular el Nuevo Flujo Total con la Reestructura, el cual se llamará desde la Página Principal de la Calculadora
    def _calcularNuevoFlujoTotal(self, nuevo_apartado_mensual: float,
                                nuevo_pago_inicial: float,
                                fecha_inicio_pago: pd.Timestamp,
                                ) -> Tuple[pd.DataFrame, bool]:
        """Esta Función es la que si cálcula la nueva reestructura

        Args:
            nuevo_apartado_mensual (float): El Nuevo apartado mensual del cliente
            nuevo_pago_inicial (float): El Nuevo Pago Inicial del Cliente
            fecha_inicio_pago (pd.Timestamp): El Inicio de Pagos del Cliente

        Returns:
            Tuple[pd.DataFrame, bool]: Un Tuple con el DataFrame del nuevo flujo total y un booleano indicando si existe un pago con destino a banco
        """
        # Paso 1: Crear un Contador de Meses (Por Defecto será los meses totales: año * 12 + mes actual)
        contador_meses = fecha_inicio_pago.year * 12 + fecha_inicio_pago.month
        # Paso 2: Obtener el Valor No Pagado de Comision y de Banco
        monto_total_no_pagado_comision = self.flujoBerex.getMontoNoPagadoCommission()
        monto_total_no_pagado_banco = self.flujoBerex.getMontoNoPagadoBanco()

        # Creamos Variable Auxiliar de Primera Iteración
        primeraIteracion = True

        # Creamos Variable Auxiliar de Fecha Actual, la cual se irá actualizando en cada iteración para obtener el monto de la mensualidad correspondiente a ese mes
        fecha_actual = fecha_inicio_pago

        # Paso 3: Comenzar la Iteración para crear el Nuevo Flujo Total con la Reestructura
        while monto_total_no_pagado_comision > 0 or monto_total_no_pagado_banco > 0:
            apartadoEsteMes = nuevo_apartado_mensual
            # La Iteración Consiste en:
            # 1. Verificar que el Valor de la Mensualidad no sea mayor al Nuevo Apartado Mensual (No puede pasar)
            # 2. Priorizar el Monto No Pagado por Banco si hay, si no, dejar el resto como Comisión
            # 3. Crear la Factura dejando el máximo monto posible

            # Definimos el Año y el Mes Actual a partir del Contador de Meses
            año_actual = contador_meses // 12
            mes_actual = contador_meses % 12 + 1

            # Paso 1: Obtener el Monto de la Mensualidad, Primera Iteracion será el Monto hasta Hoy, luego será el monto del mes
            if primeraIteracion:
                # Obtenemos el Monto Total de las Mensualidades Menores al Mes y Año Actual
                monto_mensualidad = self.flujoMensualidades.getMontoMensualidadesMenoresMesAno(mes_actual, año_actual)
                primeraIteracion = False
                # Ponemos que el Apartado de este mes es el Nuevo Pago Inicial, ya que se supone que el cliente pagará ese monto este mes
                apartadoEsteMes = nuevo_pago_inicial
            else:
                monto_mensualidad = self.flujoMensualidades.getMontoMensualidadesMesAno(mes_actual, año_actual)

            # Verificamos que el Monto de la Mensualidad no sea mayor al Nuevo Apartado Mensual, Devolvemos Nulo
            if monto_mensualidad > nuevo_apartado_mensual:
                debugLogger.error('El monto de la mensualidad {} es mayor al nuevo apartado mensual {} para la referencia {}. No se puede calcular un nuevo flujo viable.'.format(monto_mensualidad, nuevo_apartado_mensual, self.ref))
                self.newFlowCalculated = True
                return pd.DataFrame(), False # Realizamos un Return Vació para Finalizar la Ejecución

            # Ahora Actualizamos el apartado este mes quitando el valor de la mensualidad
            apartadoEsteMes -= monto_mensualidad

            # Paso 2: Priorizar el Monto No Pagado por Banco, si hay, si no, dejar el resto como Comisión
            monto_a_pagar_banco = min(monto_total_no_pagado_banco,0)
            # Si existe un monto a pagar por Banco, creamos la factura con destino a banco
            if monto_a_pagar_banco > 0:
                # Obtenemos el Valor Máximo de Pago a banco de este mes
                monto_pago_banco = min(monto_a_pagar_banco, apartadoEsteMes)
                # Agregamos la Factura al Nuevo Flujo de Berex con destino a Banco
                self.nuevoFlujoBerex.agregarFactura(fecha_actual, monto_pago_banco, 'bank', pago=0.0)
                debugLogger.debug('Agregada factura con destino a Banco por un monto de {} al nuevo flujo de Berex para la referencia {}'.format(monto_a_pagar_banco, self.ref))
                # Actualizamos el Monto No Pagado por Banco
                monto_total_no_pagado_banco -= monto_pago_banco

            # Actualizamos el apartado este mes quitando el monto pagado a banco
            apartadoEsteMes -= monto_a_pagar_banco

            # Ahora el resto del apartado este mes se va a comisión, pero solo si el monto no pagado por comisión es mayor a 0
            if monto_total_no_pagado_comision > 0 and apartadoEsteMes > 0:
                monto_pago_comision = min(monto_total_no_pagado_comision, apartadoEsteMes)
                # Agregamos la Factura al Nuevo Flujo de Berex con destino a Comisión
                self.nuevoFlujoBerex.agregarFactura(fecha_actual, monto_pago_comision, 'commission', pago=0.0)
                debugLogger.debug('Agregada factura con destino a Comisión por un monto de {} al nuevo flujo de Berex para la referencia {}'.format(monto_pago_comision, self.ref))
                # Actualizamos el Monto No Pagado por Comisión
                monto_total_no_pagado_comision -= monto_pago_comision

            # Actualizamos el contador de meses y la fecha actual para la siguiente iteración
            contador_meses += 1
            # La Fecha actual se actualizara así:
            # Si el Dia es mayor al último día del próximo mes, se colocará el último día del próximo mes, si no, se colocará el mismo día del próximo mes
            # Primero obtenemos el último día del próximo mes
            lastDayNextMonth = pd.Timestamp(year=año_actual, month=mes_actual, day=1) + pd.offsets.MonthEnd(1)
            # Luego actualizamos la fecha actual al Mínimo entre el mismo día del próximo mes y el último día del próximo mes
            nuevoDia = min(fecha_actual.day, lastDayNextMonth.day)
            fecha_actual = pd.Timestamp(year=contador_meses // 12, month=contador_meses % 12 + 1, day=nuevoDia)
            debugLogger.debug('Fecha actualizada para la siguiente iteración: {}'.format(fecha_actual))

        # Finalmente, se actualiza el atributo de Nuevo Flujo Calculado a True
        self.newFlowCalculated = True
        debugLogger.debug('Nuevo flujo total calculado exitosamente para la referencia {}'.format(self.ref))
        return (self.nuevoFlujoBerex.getFacturasDF(), monto_total_no_pagado_banco > 0)

    # Método para calcular el Nuevo Flujo Total con la Reestructura
    def calcularNuevoFlujo(self, nuevo_apartado_mensual: float,
                        nuevo_pago_inicial: float,
                        fecha_inicio_pago: pd.Timestamp,
                        ) -> Tuple[pd.DataFrame, bool]:
        """Cálcula el nuevo Flujo de la Estructuracón

        Args:
            nuevo_apartado_mensual (float): El Nuevo Apartado Mensual del Cliente
            nuevo_pago_inicial (float): El Nuevo Pago Inicial del Cliente
            fecha_inicio_pago (pd.Timestamp): El Inicio de Pagos del Cliente

        Returns:
            Tuple[pd.DataFrame, bool]: El DataFrame con el nuevo flujo y 
            un booleano indicando si existe un pago con destino a banco
        """        
        debugLogger.debug('Calculando nuevo flujo total para la referencia {}'.format(self.ref))
        # Paso 1: Obtener la Última Factura no Pagada del Flujo de Berex para Saber desde qué Fecha se Reestructurará el Flujo
        ultima_factura, _ = self.flujoBerex.getUltimaFacturaNoPagada(self.flujoBerex.getMontoPagado())

        # Paso 2: Obtener el Monto Total no Pagado y el Monto Pagado
        monto_total_no_pagado = self.flujoBerex.getMontoPendiente()
        monto_total_pagado = self.flujoBerex.getMontoPagado()
        debugLogger.debug('Monto total no pagado: {}, Monto total pagado: {} para la referencia {}'.format(monto_total_no_pagado, monto_total_pagado, self.ref))

        # Paso 3: Crear un Nuevo Flujo Berex
        self.nuevoFlujoBerex = FlujoBerex(self.ref, None)

        # Paso 4: Agregamos una Primera Factura que sea la Última Factura quitando el Pago
        if ultima_factura is not None:
            self.nuevoFlujoBerex.agregarFactura(ultima_factura.fecha, monto_total_pagado, ultima_factura.destino, pago=0.0)
            debugLogger.debug('Agregada primera factura al nuevo flujo de Berex para la referencia {}: {}'.format(self.ref, ultima_factura))
        else:
            debugLogger.warning('No se encontró una factura no pagada en el flujo de Berex para la referencia {}. El nuevo flujo de Berex será Nulo.'.format(self.ref))
            self.newFlowCalculated = True
            return pd.DataFrame(), False # Realizamos un Return Vació para Finalizar la Ejecución

        # Paso 5: Cálcular el Nuevo Flujo ahorá si
        resultDF, anyPagoBanco = self._calcularNuevoFlujoTotal(nuevo_apartado_mensual, nuevo_pago_inicial, fecha_inicio_pago)
        debugLogger.debug('Nuevo flujo total calculado para la referencia {}'.format(self.ref))
        return resultDF, anyPagoBanco

    # Método para saber si el Nuevo Flujo es Viable, es decir, la cantidad de facturas es menor a 9
    def isNuevoFlujoViable(self) -> bool:
        if self.newFlowCalculated:
            isViable = len(self.nuevoFlujoBerex.facturas) <= 9 # AJUSTABLE
            notInfinteLog('nuevo_flujo_viable', 'El nuevo flujo de Berex para la referencia {} es viable: {}'.format(self.ref, isViable), method='debug')
        else:
            notInfinteLog('nuevo_flujo_no_calculado', 'El nuevo flujo de Berex para la referencia {} no ha sido calculado aún. No se puede determinar si es viable.'.format(self.ref), method='warning')
            return False