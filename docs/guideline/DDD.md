## 3. Actores y casos de uso
Actor principal: Usuario del sistema. El usuario puede ingresar los votos de cada lista, ejecutar el cálculo de asignación de escaños y consultar resultados históricos.

**Casos de uso principales**:

- Ingresar cantidad total de escaños a disputar.
- Registrar los votos obtenidos por cada partido o lista.
- Visualizar los datos ingresados. [DDD]
- Ejecutar el cálculo de asignación de escaños.
- Visualizar los resultados del cálculo. [DDD]
- Consultar el historial de votos.

## 4. Requerimientos funcionales
- Permitir registrar la cantidad total de escaños.
- Permitir registrar los votos por lista o partido.
- Calcular la asignación de escaños según el método D’Hondt.
- Mostrar el resultado de la asignación por partido.
- Almacenar un historial consultable.
- El sistema debe garantizar la integridad referencial de los datos. [DDD]

## 5. Requerimientos no funcionales
- El sistema debe ejecutarse en contenedores Docker.
- La base de datos debe ser PostgreSQL. [DDD]
- La interfaz web debe ser desarrollada en Astro y consumir la API mediante HTTP. [DDD]
- El cálculo debe realizarse como un servicio de la API y desacoplado de la interfaz. [DDD]
- El sistema debe registrar logs de operaciones y errores. [DDD]
- El sistema debe soportar consultas concurrentes sin pérdida de datos. [DDD]

## 6. Lógica de negocio
### 1 Reglas generales

- Cada votación se asocia a un cálculo específico. [DDD]
- Cada partido o lista debe estar registrado en la tabla de partidos/listas válidas. [DDD]
- Cada voto ingresado se registra en una tabla y debe referenciar un partido válido. [DDD]
- Los votos deben ser números enteros no negativos; valores negativos generan error. [DDD]
- La cantidad de escaños a asignar debe ser mayor a cero. [DDD]

### 2 Flujo de asignación de escaños (D’Hondt)

- Se obtienen todos los votos registrados por partido para un cálculo dado. [DDD]
- Se aplica el umbral mínimo del 3% de los votos totales; solo las listas que superan el umbral participan en la asignación. [DDD]
- Para cada lista elegible, se generan divisores hasta cubrir la cantidad de escaños a asignar.
- Se ordenan todos los cocientes de mayor a menor.
- Se asignan los escaños uno por uno a los cocientes más altos hasta agotar la cantidad de escaños disponibles.
- En caso de empate en cociente, se asigna el escaño al partido con mayor cantidad de votos totales. [DDD]
- Si persiste empate exacto en votos y cociente, se requiere regla externa o sorteo manual. [DDD]
- Los resultados (votos totales y escaños asignados) se registran en una tabla de resultados para consulta posterior. [DDD]

### 3 Restricciones de negocio

- Los resultados históricos deben ser consultables, respetando el orden temporal de las ejecuciones. [DDD]
- Los votos en blanco e impugnados no compiten por escaños, pero influyen en el cálculo del total de votos para el umbral. [DDD]
- No se permite ingresar votos negativos; cualquier intento genera error y detiene la operación. [DDD]