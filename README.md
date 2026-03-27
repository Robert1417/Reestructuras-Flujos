# **Calculadora de Reestructuras**
___
El objetivo del código consiste en minimizar los errores que se realizan a la hora de tener en cuenta el proceso de una reestructuración de forma manual. Esto se va a realizar mediante una *aplicación de streamlit* en la cuál se conecten los datos y sea posible todo el proceso automático e interactivo

Para esto, se requieren los siguientes datos:
- **Flujo de Cartera Berex**: Para entender los Pagos que se han incumplido y el flujo total
- **Datos de Moras**: Para saber lo pagado por el cliente y lo que había que cobrar
- **Datos de Mensualidades**: Para tener en cuenta los Pagos de Mensualidades por parte del Cliente

Con toda esta información se realiza el siguiente procedimiento:
1. **Última Originación**: Se dejan los datos de la Última Originación para el flujo de cartera berex y las moras.
2. **Unión de Datos**: La unión entre el flujo y las moras será por Referencia, mientras que la unión con las Mensualidades se realizará mes a mes.

___

# **Datos de la Reestructura**

Los Datos se almacenan localmente en formato *.parquet* e incluyen:
- **moras.parquet**: Referencia - Fecha - Fecha_Origen - Por_Cobrar - Pago - Status_Mora
- **cartera.parquet**: Referencia - Fecha_Origen - Fecha_Pago_Berex - Monto_Berex - Destino
- **mensualidades.parquet**: Referencia - Status_Facturacion - Status_Reparadora - Monto_Mensualidad - Fecha_Cobro

___
# **Parámetros de la Reestructura**

Los Parámetros son datos que pueden ser cambiados para negociar la reestructura, incluyendo:
- **Referencia**: La Referencia del Cliente al Cúal se le va a realizar la Reestructura
- **Fecha de Pago Inicial**: El Primer pago que realizará el cliente (en body)
- **Nuevo Apartado Mensual**: El nuevo AM del cliente (en body)
- **Valor de Pago Inicial**: El Monto del primer pago que realizará el cliente (en body)
- **Descuento Condonado?**: (en sidebar)

___
# **Alertas**

Se producirá una alerta bajo los siguientes casos:
- **Pago a Banco Faltante**: Existe una factura con destino al banco que no se realizó antes (en sidebar)
- **Plazo mayor a x Meses**: El Plazo de la reestructura excede lo convencional (en sidebar)

___
# **Estructura del Proyecto**

El proyecto esta dividido bajo la siguiente estructura:
- **data**: Todo lo Relacionado con Datos (incluyendo tests)
- **src**: Carpeta Inicial donde se encuentra todo el proyecto
- **src/app.py**: La Calculadora en Sí
- **src/core**: Cálculos y Clases de Vital Importancia
- **src/utils**: Funciones de Ayuda
- **src/ui**: Componentes de Visualización de Streamlit

