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
# **Parámetros de la Reestructura**

Los Parámetros son Movimientos de 

___
# **Estructura del Proyecto**

El proyecto esta dividido bajo la siguiente estructura:
- **data**: Todo lo Relacionado con Datos (incluyendo tests)
- **src**: Carpeta Inicial donde se encuentra todo el proyecto
- **src/app.py**: La Calculadora en Sí
- **src/core**: Cálculos y Clases de Vital Importancia
- **src/utils**: Funciones de Ayuda
- **src/ui**: Componentes de Visualización de Streamlit

Por favor no romper la estructura