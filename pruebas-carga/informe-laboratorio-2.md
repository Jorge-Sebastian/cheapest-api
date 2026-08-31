# Laboratorio 2: pruebas de carga del backend monolítico Cheapest

**Sistema evaluado:** Cheapest API (NestJS y PostgreSQL)  
**Distribución principal:** Pareto 80/20  
**Herramientas:** Apache JMeter 5.6.3 y Python con `aiohttp`  
**Entorno:** MacBook Pro M5 Pro, 24 GB de memoria; PostgreSQL 15 en Docker  
**Rama:** `lab-2`  
**Fecha:** 30 de agosto de 2026

## 1. Alcance del informe

En el laboratorio se evaluó el comportamiento del backend monolítico de Cheapest ante un incremento progresivo de carga. Se completó la matriz del endpoint GET desde *smoke test* hasta estrés, con las repeticiones solicitadas para cada escenario alcanzado. También se validó el endpoint POST con un pedido realista de 24 ítems.

Por la restricción de tiempo de la sesión no se ejecutaron el escenario de estrés fuerte, la matriz completa del POST ni las corridas de control con distribución uniforme. Estas limitaciones se indican de forma explícita para no presentar como mediciones resultados que no fueron obtenidos.

## 2. Objetivos y ASRs

| ASR | Endpoint | Condición de aceptación |
|---|---|---|
| ASR 1 | `GET /logistics/tenderos/productos-disponibles` | Latencia p99 menor que 1.000 ms en operación normal (500 req/min). |
| ASR 2 | `POST /logistics/pedidos` | Porcentaje de error menor o igual al 2 % durante el pico estimado (5.000 req/min). |

El punto de inflexión se define como el primer nivel de carga en el que se incumple al menos uno de los ASRs.

## 3. Preparación y validación del ambiente

Antes de ejecutar las pruebas se comprobó lo siguiente:

- 41 suites y 342 pruebas unitarias exitosas.
- Compilación correcta del backend.
- PostgreSQL saludable dentro de Docker.
- Respuesta correcta de `/health`.
- Validación manual del GET con HTTP 200 y ocho productos.
- Validación manual del POST con HTTP 201.

![PostgreSQL saludable](capturas-de-pantalla/06-postgresql-docker-healthy.png)

*Figura 1. PostgreSQL ejecutándose correctamente en Docker.*

![Health check del backend](capturas-de-pantalla/07-backend-health-check.png)

*Figura 2. Verificación del estado del backend.*

![Validación manual del GET](capturas-de-pantalla/08-get-productos-disponibles.png)

*Figura 3. Validación manual del endpoint GET: HTTP 200 y ocho productos devueltos.*

![Validación manual del POST](capturas-de-pantalla/09-post-pedido-manual.png)

*Figura 4. Validación manual de creación de un pedido.*

## 4. Diseño y distribución de los datos

Se definieron dos configuraciones con los mismos volúmenes totales. La única diferencia es la manera de asignar la actividad, lo cual permite atribuir las diferencias de rendimiento a la distribución y no al tamaño del conjunto de datos.

| Entidad | Volumen | Justificación |
|---|---:|---|
| Tiendas | 3.000 | Escala suficiente para representar tiendas con comportamientos heterogéneos. |
| Zonas | 10 | Permite representar zonas con diferente densidad comercial. |
| Productos | 1.200 | Catálogo base para las consultas y relaciones. |
| Catálogos | 3.000 | Referencia aproximada de un catálogo por tienda. |
| Catálogo-producto | 600.000 | Promedio de 200 referencias visibles por catálogo. |
| Promociones | 240 | Equivale al 20 % del catálogo; el seeder deja el 70 % vigente. |
| Pedidos | 100.000 | Aproximadamente 33 pedidos históricos por tienda. |
| Ítems de pedido | 500.000 | Promedio de cinco ítems por pedido histórico. |
| Despachos | 80.000 | Aproxima que el 80 % de los pedidos alcanzó despacho. |
| Disponibilidad por zona | 600.000 | Cobertura comparable con catálogo-producto. |
| Notas crédito | 5.000 | Aproxima incidencias sobre el 5 % de los pedidos. |
| Ítems de inventario | 300.000 | Promedio global de 100 referencias por tienda. |
| Registros de compra | 300.000 | Histórico de abastecimiento. |
| Registros de venta | 600.000 | Dos movimientos de venta por ítem de inventario. |
| Productos externos | 300 | Referencias vendidas por fuera del catálogo formal. |
| Ventas / ítems de venta | 150.000 / 600.000 | Promedio de cuatro ítems por venta. |

### 4.1 Distribución uniforme

La configuración uniforme asigna actividad mediante *round-robin* entre tiendas, zonas y productos. Se usa como control experimental. Su desventaja es que supone que todos los actores generan aproximadamente la misma demanda.

### 4.2 Distribución Pareto 80/20

En el escenario principal, el 20 % de las tiendas, zonas o productos que conforman la cabeza recibe el 80 % de las asignaciones. Esto representa mejor un comercio electrónico: unas pocas tiendas compran mucho más, algunas zonas tienen mayor actividad y determinados productos son mucho más populares.

![Comparación de distribuciones](graficas/distribuciones.png)

*Figura 5. Comparación conceptual usando los mismos ejes y escala. La uniformidad oculta puntos calientes, mientras Pareto reproduce la concentración de demanda.*

![Configuración Pareto](capturas-de-pantalla/10-configuracion-pareto-completa.png)

*Figura 6. Volúmenes y parámetros de la distribución Pareto 80/20.*

![Seed Pareto](capturas-de-pantalla/11-seed-pareto-exitoso.png)

*Figura 7. Generación exitosa del conjunto de datos Pareto.*

![Conteos de logística](capturas-de-pantalla/12-conteos-logistica-pareto.png)

*Figura 8. Verificación de los conteos del módulo de logística.*

## 5. Metodología de las pruebas

JMeter se utilizó hasta 450 usuarios, porque permite inspeccionar gráficamente la configuración y los listeners. Para escenarios mayores se utilizó obligatoriamente el ejecutor asíncrono de Python.

Cada solicitud del ejecutor registra:

- timestamp ISO;
- método y URL;
- código HTTP;
- latencia en milisegundos;
- error, cuando aplica.

El resumen calcula total de solicitudes, duración, throughput, promedio, p95, p99 y porcentaje de errores. También realiza un *preflight* contra `/health`, limita la concurrencia, aplica ramp-up y evita sobrescribir resultados anteriores.

| Escenario | Usuarios | Ramp-up | Corridas ejecutadas | Herramienta |
|---|---:|---:|---:|---|
| Smoke | 5 | 5 s | 4 | JMeter |
| Baja | 30 | 10 s | 4 | JMeter |
| Media | 100 | 20 s | 4 | JMeter |
| Operación normal | 450 | 50 s | 8 | JMeter |
| Alta | 1.500 | 75 s | 4 | Python |
| Muy alta | 3.000 | 100 s | 4 | Python |
| Estrés | 7.500 | 150 s | 4 | Python |
| Estrés fuerte | 18.000 | 200 s | No ejecutado | Python |

![Variables JMeter](capturas-de-pantalla/16a-jmeter-get-variables.png)

*Figura 9. Variables parametrizadas en JMeter.*

![Sampler GET](capturas-de-pantalla/16b-jmeter-get-request-configuracion.png)

*Figura 10. Configuración del servidor, puerto, ruta y parámetros del GET.*

![Validación en JMeter](capturas-de-pantalla/18-jmeter-get-smoke-aggregate.png)

*Figura 11. Aggregate Report de la validación inicial.*

![Ayuda del ejecutor Python](capturas-de-pantalla/24-python-aiohttp-script-ayuda.png)

*Figura 12. Interfaz CLI del ejecutor Python para cargas superiores a 450 usuarios.*

## 6. Resultados del endpoint GET

| Escenario | Corrida | Usuarios | Ramp-up | p95 (ms) | p99 (ms) | Throughput (req/s) | Error % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Smoke | 1 | 5 | 5 | 101 | 101 | 1,25 | 0 |
| Smoke | 2 | 5 | 5 | 84 | 84 | 1,24 | 0 |
| Smoke | 3 | 5 | 5 | 74 | 74 | 1,24 | 0 |
| Smoke | 4 | 5 | 5 | 79 | 79 | 1,24 | 0 |
| Baja | 1 | 30 | 10 | 75 | 81 | 3,09 | 0 |
| Baja | 2 | 30 | 10 | 78 | 78 | 3,09 | 0 |
| Baja | 3 | 30 | 10 | 73 | 74 | 3,09 | 0 |
| Baja | 4 | 30 | 10 | 72 | 72 | 3,09 | 0 |
| Media | 1 | 100 | 20 | 61 | 67 | 5,04 | 0 |
| Media | 2 | 100 | 20 | 69 | 74 | 5,04 | 0 |
| Media | 3 | 100 | 20 | 65 | 71 | 5,04 | 0 |
| Media | 4 | 100 | 20 | 67 | 70 | 5,04 | 0 |
| Normal | 1 | 450 | 50 | 56 | 59 | 9,02 | 0 |
| Normal | 2 | 450 | 50 | 54 | 59 | 9,03 | 0 |
| Normal | 3 | 450 | 50 | 57 | 64 | 9,02 | 0 |
| Normal | 4 | 450 | 50 | 56 | 60 | 9,03 | 0 |
| Normal | 5 | 450 | 50 | 56 | 59 | 9,02 | 0 |
| Normal | 6 | 450 | 50 | 56 | 57 | 9,02 | 0 |
| Normal | 7 | 450 | 50 | 55 | 61 | 9,02 | 0 |
| Normal | 8 | 450 | 50 | 56 | 58 | 9,02 | 0 |
| Alta | 1 | 1.500 | 75 | 60,16 | 63,75 | 20,00 | 0 |
| Alta | 2 | 1.500 | 75 | 59,70 | 62,61 | 20,00 | 0 |
| Alta | 3 | 1.500 | 75 | 59,66 | 62,98 | 20,00 | 0 |
| Alta | 4 | 1.500 | 75 | 60,14 | 62,87 | 20,00 | 0 |
| Muy alta | 1 | 3.000 | 100 | 65,52 | 69,07 | 29,99 | 0 |
| Muy alta | 2 | 3.000 | 100 | 64,89 | 68,17 | 29,99 | 0 |
| Muy alta | 3 | 3.000 | 100 | 64,57 | 67,64 | 29,99 | 0 |
| Muy alta | 4 | 3.000 | 100 | 64,39 | 68,50 | 29,99 | 0 |
| Estrés | 1 | 7.500 | 150 | 76,62 | 79,76 | 49,98 | 0 |
| Estrés | 2 | 7.500 | 150 | 74,57 | 78,50 | 49,98 | 0 |
| Estrés | 3 | 7.500 | 150 | 78,61 | 81,68 | 49,98 | 0 |
| Estrés | 4 | 7.500 | 150 | 73,84 | 77,18 | 49,98 | 0 |

![Evolución del GET](graficas/resultados_get.png)

*Figura 13. Evolución del p99 y del throughput del endpoint GET.*

En operación normal el p99 promedio fue de 59,6 ms, aproximadamente un 94 % inferior al límite del ASR 1. En estrés, el p99 promedio fue de 79,28 ms. Las cuatro corridas procesaron 7.500 solicitudes sin errores y alcanzaron cerca de 50 req/s.

![Smoke test](capturas-de-pantalla/20a-jmeter-get-smoke-corridas-01-02.png)

*Figura 14. Primeras dos corridas del smoke test.*

![Carga baja](capturas-de-pantalla/21a-jmeter-get-baja-corridas-01-02.png)

*Figura 15. Primeras dos corridas de baja carga.*

![Carga media](capturas-de-pantalla/22a-jmeter-get-media-corridas-01-02.png)

*Figura 16. Primeras dos corridas de carga media.*

![Operación normal](capturas-de-pantalla/23a-jmeter-get-normal-corridas-01-02.png)

*Figura 17. Primeras dos corridas de operación normal.*

![Carga alta](capturas-de-pantalla/27a-python-get-alta-corridas-01-02.png)

*Figura 18. Primeras dos corridas de carga alta.*

![Carga muy alta](capturas-de-pantalla/28-python-get-muy-alta-corridas-01-04.png)

*Figura 19. Cuatro corridas GET de muy alta carga.*

![Estrés](capturas-de-pantalla/29-python-get-estres-corridas-01-04.png)

*Figura 20. Cuatro corridas GET de estrés: 7.500 solicitudes por corrida y 0 % de error.*

## 7. Validación del endpoint POST

El POST se validó con un pedido de 24 ítems y produjo:

- 227 solicitudes en 3,023 segundos;
- throughput de 75,10 req/s;
- latencia promedio de 24,41 ms;
- p95 de 26,76 ms;
- p99 de 29,28 ms;
- 0 % de errores;
- respuestas HTTP 201 en las filas inspeccionadas.

Esta validación comprueba el funcionamiento del ejecutor y del cuerpo JSON, pero no sustituye las repeticiones de la matriz necesarias para concluir sobre el ASR 2.

![Validación POST](capturas-de-pantalla/26-python-validacion-post-24-items.png)

*Figura 21. Validación POST con un pedido de 24 ítems.*

## 8. Respuestas a las preguntas del laboratorio

### Pregunta 1: ¿qué endpoint priorizaría antes de un pico comercial?

Priorizaría `POST /logistics/pedidos`. El GET afecta el descubrimiento de productos y la conversión, pero una falla al crear pedidos produce pérdida directa de ventas, posibles duplicados e inconsistencias. Además, el objetivo del POST es de 5.000 req/min, casi diez veces la operación normal definida para el GET, y la escritura transaccional tiene mayor riesgo de contención de locks y agotamiento del pool.

Como mejora inicial de costo y tiempo moderados aplicaría claves de idempotencia, validaciones anticipadas, transacciones cortas, índices sobre las relaciones utilizadas y medición del pool. Posteriormente separaría mediante una cola las actividades secundarias que no tengan que completarse dentro de la respuesta HTTP.

### Pregunta 2: distribución, sesgos e hipótesis

Una distribución uniforme reduce artificialmente las colisiones sobre tiendas, zonas y productos populares. También genera cachés equilibradas y planes de consulta estables, lo que podría desplazar falsamente el punto de inflexión y llevar a la conclusión de que el sistema soporta mejor la hora pico.

Las estrategias propuestas son:

1. **Uniforme como control:** mantiene igual probabilidad para todos los actores. Permite validar si la degradación depende únicamente del volumen total.
2. **Pareto 80/20 como escenario principal:** concentra actividad sobre tiendas, zonas y productos populares. Valida la capacidad del monolito frente a hotspots realistas, cachés sesgadas y contención.
3. **Ráfagas temporales como extensión:** concentra solicitudes durante ventanas cortas, con una zona dominante y promociones sincronizadas. Permitiría validar absorción de picos, backpressure y recuperación.

En la Figura 5, el patrón que hace más realista a Pareto es la concentración visible de aproximadamente el 80 % de la actividad en el 20 % de las zonas.

### Pregunta 3: diseño para distinguir el origen del quiebre

Se modificaría una sola variable por experimento, manteniendo constantes el dataset, el endpoint, la tasa objetivo y el generador.

#### Hipótesis A: saturación del pool

Se repetiría la misma carga con tamaños de pool de 5, 10, 20 y 40 conexiones. Se medirían tiempo de espera para adquirir conexión, conexiones activas, latencia y errores. La firma esperada es un codo de latencia al alcanzar el límite; si se amplía el pool, ese codo debe desplazarse.

#### Hipótesis B: consultas SQL ineficientes

Se mantendrían pool y concurrencia, comparando la consulta base contra una versión con índices y otra simplificada. Se utilizaría `EXPLAIN (ANALYZE, BUFFERS)`. Una reducción marcada del p99 y de lecturas de bloques después de indexar confirmaría el costo SQL.

#### Hipótesis C: límite del generador

Se ejecutaría el mismo cliente contra un stub HTTP liviano, se observarían CPU y event loop del generador y se repetiría desde otra máquina. Si el throughput se aplana también contra el stub y el servidor permanece ocioso, el generador es el cuello de botella.

![Hipótesis de cuellos de botella](graficas/hipotesis.png)

*Figura 22. Firmas visuales esperadas para pool saturado, SQL ineficiente y límite del generador.*

### Pregunta 4: estrategia para que la IA siga reglas del equipo

La consistencia no debería depender únicamente de redactar un prompt diferente en cada tarea. Para Cheapest propongo combinar:

1. **Instrucciones versionadas en el repositorio:** un archivo `AGENTS.md` o equivalente que indique arquitectura por capas, TypeScript estricto, uso de DTOs, transacciones, manejo de errores, nombres y operaciones prohibidas.
2. **Plantillas de implementación:** esqueletos aprobados para controladores, servicios, repositorios, pruebas y migraciones.
3. **Ejemplos de referencia:** implementaciones pequeñas consideradas correctas por el equipo para aplicar aprendizaje por ejemplos (*few-shot*).
4. **Contexto recuperable:** documentación y decisiones arquitectónicas cercanas al código para que el agente consulte los estándares relevantes antes de editar.
5. **Flujo obligatorio:** solicitar primero plan, luego un cambio pequeño, pruebas y explicación de las decisiones.
6. **Verificación automática:** lint, pruebas unitarias, integración, análisis de seguridad y revisión humana en CI.

Las reglas deben ser específicas y comprobables. Por ejemplo, “todo endpoint de escritura debe aceptar una clave de idempotencia y contar con una prueba de solicitud repetida” es más útil que “escriba código robusto”.

## 9. Respuestas de análisis solicitadas en los entregables

### 9.1 ¿Cuál fue el punto de inflexión y cuál ASR se rompió primero?

No se encontró un punto de inflexión dentro del rango medido. El ASR 1 se cumplió en todas las corridas hasta estrés. El ASR 2 no puede declararse cumplido ni incumplido porque se realizó una validación funcional, pero no su matriz oficial. Por la misma razón, no es válido afirmar que algún ASR se rompió primero.

### 9.2 ¿El monolito benefició el cumplimiento de los ASRs?

Para el GET observado, el despliegue local monolítico favoreció una latencia baja al evitar saltos de red entre módulos y permitir acceso directo al mismo PostgreSQL. Los resultados demuestran buen comportamiento dentro del rango medido, pero no prueban escalabilidad ilimitada.

El acoplamiento de lectura y escritura dentro del mismo proceso también implica que ambos endpoints pueden competir por CPU, memoria, event loop y conexiones cuando se ejecuten simultáneamente.

### 9.3 ¿Qué modificaciones ayudarían a sostener los ASRs?

- Índices compuestos y revisión mediante `EXPLAIN ANALYZE` para filtros de tienda, zona, vigencia y disponibilidad.
- Caché *read-through* para productos disponibles, con invalidación por zona o promoción.
- Réplicas de lectura o CQRS si el GET domina el consumo.
- Claves de idempotencia, transacciones cortas y una cola para tareas secundarias del POST.
- Pool dimensionado a partir de métricas de espera.
- Backpressure, límites y circuit breaker.
- Escalamiento horizontal del backend detrás de un balanceador, vigilando que PostgreSQL no se convierta en el cuello común.

### 9.4 ¿La degradación fue gradual o abrupta y dónde está el cuello de botella?

La degradación observada fue gradual y pequeña. El p99 promedio pasó de 59,6 ms en operación normal a 79,28 ms en estrés, sin saltos abruptos ni errores. Con la evidencia disponible no se puede localizar definitivamente el cuello de botella, pues faltan métricas de CPU, event loop, espera del pool, locks y planes SQL.

### 9.5 ¿Qué endpoint degradó primero?

No puede realizarse una comparación experimental porque no se ejecutó la misma matriz sobre POST. Arquitectónicamente se espera que el POST sea más sensible a la contención transaccional y al pool, pero esto queda planteado como hipótesis, no como resultado observado.

## 10. Incidencias

La primera validación del ejecutor Python se inició con la API detenida y generó 42.223 fallos de conexión. Esa corrida fue descartada y se añadió un *preflight* de `/health` para detener la prueba antes de generar carga si el sistema no está disponible. El CSV inválido se mantuvo separado y no se mezcló con resultados oficiales.

![Incidencia API detenida](capturas-de-pantalla/25a-python-validacion-get-api-detenida.png)

*Figura 23. Corrida descartada debido a que el backend estaba detenido.*

![Validación posterior](capturas-de-pantalla/25b-python-validacion-get-exitosa.png)

*Figura 24. Validación correcta después de levantar el backend y agregar el preflight.*

## 11. Prompt utilizado para generar el ejecutor Python

> Genera para Cheapest un script de carga en Python con `asyncio` y exactamente una dependencia, `aiohttp`. Debe probar los endpoints GET de productos disponibles y POST de pedidos, y aceptar `--endpoint`, `--users`, `--ramp-up`, `--duration`, `--body`, `--base-url`, `--timeout` y `--output`.
>
> El script debe registrar por solicitud timestamp ISO, método, URL, código HTTP, latencia y error; considerar error los HTTP >= 400, timeouts y fallos de conexión; exportar CSV; y calcular total, duración, throughput, promedio, p95, p99 y porcentaje de error. Para POST debe validar una plantilla con más de 20 ítems y generar identificador y fecha únicos por solicitud. Debe limitar la concurrencia, aplicar ramp-up gradual, manejar excepciones y negarse a sobrescribir resultados existentes. Incluye documentación y ejemplos para la matriz de alta carga del laboratorio.

El prompt completo también se conserva en [`python/prompt-utilizado.md`](python/prompt-utilizado.md), y el resultado generado en [`python/load_test.py`](python/load_test.py).

## 12. Conclusiones

1. El endpoint GET cumplió el ASR 1 en todas las cargas ejecutadas, desde smoke hasta estrés.
2. En operación normal obtuvo un p99 promedio de 59,6 ms; en estrés, 79,28 ms.
3. Las 32 corridas oficiales del GET terminaron con 0 % de errores.
4. No se encontró el punto de inflexión dentro del rango medido de hasta 7.500 usuarios y 50 req/s.
5. La validación POST demostró que el ejecutor y el pedido de 24 ítems funcionan, pero no permite concluir sobre ASR 2.
6. Pareto representa mejor el escenario comercial porque conserva hotspots que una distribución uniforme ocultaría.
7. Para atribuir futuros quiebres se requiere telemetría del pool, SQL, CPU, memoria, event loop y generador.

## 13. Limitaciones y trabajo pendiente

- Ejecutar ocho corridas de estrés fuerte GET con 18.000 usuarios.
- Ejecutar la matriz completa del POST.
- Cargar el control uniforme y repetir escenarios equivalentes.
- Ejecutar GET y POST simultáneamente para medir interferencia dentro del monolito.
- Recolectar métricas de infraestructura y planes SQL.

## 14. Archivos de reproducibilidad

| Elemento | Ruta |
|---|---|
| Bitácora detallada | [`bitacora.md`](bitacora.md) |
| Plan JMeter GET | [`jmeter/get-productos-disponibles.jmx`](jmeter/get-productos-disponibles.jmx) |
| Ejecutor Python | [`python/load_test.py`](python/load_test.py) |
| Prompt utilizado | [`python/prompt-utilizado.md`](python/prompt-utilizado.md) |
| Cuerpo POST | [`python/sample_body.json`](python/sample_body.json) |
| Resultados | [`resultados/`](resultados/) |
| Evidencias completas | [`capturas-de-pantalla/`](capturas-de-pantalla/) |

## Anexo A. Evidencias complementarias

Las siguientes capturas completan la trazabilidad del procedimiento. Se dejan en el anexo para conservar la secuencia sin interrumpir el análisis principal.

![Estado inicial de la rama](capturas-de-pantalla/01-rama-lab2-estado-inicial.png)

*Figura A1. Estado inicial de la rama de trabajo.*

![JMeter instalado](capturas-de-pantalla/02-jmeter-instalado.png)

*Figura A2. Verificación de la instalación de JMeter.*

![Interfaz de JMeter](capturas-de-pantalla/03-interfaz-jmeter.png)

*Figura A3. Interfaz gráfica de Apache JMeter.*

![Pruebas unitarias](capturas-de-pantalla/04-pruebas-unitarias-iniciales.png)

*Figura A4. Pruebas unitarias iniciales exitosas.*

![Compilación inicial](capturas-de-pantalla/05-compilacion-inicial-exitosa.png)

*Figura A5. Compilación inicial del backend.*

![Conteos de inventario y ventas](capturas-de-pantalla/13-conteos-inventario-ventas.png)

*Figura A6. Conteos de las entidades de inventario y ventas.*

![GET individual Pareto](capturas-de-pantalla/14-get-individual-base-pareto.png)

*Figura A7. Solicitud individual sobre la base Pareto.*

![Configuración del smoke test](capturas-de-pantalla/15-jmeter-get-smoke-configuracion.png)

*Figura A8. Grupo de usuarios del smoke test.*

![Árbol de resultados](capturas-de-pantalla/17-jmeter-get-smoke-results-tree.png)

*Figura A9. Solicitudes exitosas en View Results Tree.*

![Resumen del smoke test](capturas-de-pantalla/19-jmeter-get-smoke-summary.png)

*Figura A10. Summary Report de la validación smoke.*

![Smoke corridas 3 y 4](capturas-de-pantalla/20b-jmeter-get-smoke-corridas-03-04.png)

*Figura A11. Corridas 3 y 4 del smoke test.*

![Baja corridas 3 y 4](capturas-de-pantalla/21b-jmeter-get-baja-corridas-03-04.png)

*Figura A12. Corridas 3 y 4 de baja carga.*

![Media corridas 3 y 4](capturas-de-pantalla/22b-jmeter-get-media-corridas-03-04.png)

*Figura A13. Corridas 3 y 4 de carga media.*

![Normal corridas 3 y 4](capturas-de-pantalla/23b-jmeter-get-normal-corridas-03-04.png)

*Figura A14. Corridas 3 y 4 de operación normal.*

![Normal corridas 5 y 6](capturas-de-pantalla/23c-jmeter-get-normal-corridas-05-06.png)

*Figura A15. Corridas 5 y 6 de operación normal.*

![Normal corridas 7 y 8](capturas-de-pantalla/23d-jmeter-get-normal-corridas-07-08.png)

*Figura A16. Corridas 7 y 8 de operación normal.*

![Archivos de operación normal](capturas-de-pantalla/23e-jmeter-get-normal-archivos-resultados.png)

*Figura A17. Archivos producidos por las ocho corridas de operación normal.*

![Alta corridas 3 y 4](capturas-de-pantalla/27b-python-get-alta-corridas-03-04.png)

*Figura A18. Corridas 3 y 4 de carga alta.*
