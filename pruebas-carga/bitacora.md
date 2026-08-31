# Bitácora de pruebas de carga

## Ambiente de referencia

- Equipo: MacBook Pro, Apple M5 Pro, 15 núcleos, 24 GB de memoria.
- Backend: NestJS ejecutado localmente.
- Base de datos: PostgreSQL 15 Alpine en Docker.
- Herramientas: Apache JMeter 5.6.3 y script asíncrono de Python.
- Rama: `lab-2`.

No registrar números de serie, UUID de hardware ni otros identificadores del equipo.

## Diseño de datos

Los dos escenarios usan los mismos totales. Solo cambia la forma de asignar la
actividad, para que cualquier diferencia observada pueda atribuirse a la
distribución y no al volumen total.

| Entidad | Total | Criterio |
| --- | ---: | --- |
| Tiendas | 3.000 IDs lógicos | Escala actual indicada en el caso Cheapest. La rama de carga no persiste una tabla `tiendas`; el seeder usa este pool para distribuir relaciones y actividad. |
| Zonas | 10 | Permite representar zonas de alta y baja densidad. |
| Productos | 1.200 | Catálogo actual indicado en el caso. |
| Catálogos | 3.000 | Referencia de un catálogo por tienda en el volumen total. |
| Catálogo-producto | 600.000 | Promedio de 200 referencias visibles por catálogo. |
| Promociones | 240 | 20 % del catálogo con promoción; el seeder deja 70 % vigentes. |
| Pedidos | 100.000 | Aproximadamente 33 pedidos históricos por tienda. |
| Ítems de pedido | 500.000 | Promedio de cinco ítems por pedido histórico. |
| Despachos | 80.000 | Aproxima que 80 % de los pedidos alcanzó despacho. |
| Disponibilidad por zona | 600.000 | Mantiene una cobertura comparable con catálogo-producto. |
| Notas crédito | 5.000 | Aproxima incidencias sobre 5 % de los pedidos. |
| Ítems de inventario | 300.000 | Promedio global de 100 referencias controladas por tienda. |
| Registros de compra | 300.000 | Histórico de abastecimiento para inventario. |
| Registros de venta | 600.000 | Dos movimientos de venta por ítem de inventario. |
| Productos externos | 300 | Referencias vendidas fuera del catálogo formal. |
| Ventas | 150.000 | Histórico local de ventas de las tiendas. |
| Ítems de venta | 600.000 | Promedio de cuatro ítems por venta. |

### Estrategia uniforme

Asigna actividad round-robin entre tiendas, zonas y productos. Es el control
experimental y permite identificar el sesgo de asumir que todos los actores
generan la misma carga.

### Estrategia Pareto

El 20 % de tiendas, zonas o productos que conforma la cabeza recibe el 80 % de
las asignaciones. Es el escenario principal porque representa tiendas de alto
volumen, zonas densas y productos populares.

## Registro de corridas

| Distribución | Endpoint | Escenario | Corrida | Usuarios | Ramp-up (s) | Duración (s) | p95 (ms) | p99 (ms) | Throughput (req/s) | Error (%) | Archivo | Observaciones |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Pareto 80/20 | GET productos disponibles | Smoke | 1 | 5 | 5 | 4.010 | 101 | 101 | 1.25 | 0.00 | `resultados/jmeter/get/smoke/pareto_get_smoke_run01.jtl` | Validación correcta; 5 de 5 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Smoke | 2 | 5 | 5 | 4.047 | 84 | 84 | 1.24 | 0.00 | `resultados/jmeter/get/smoke/pareto_get_smoke_run02.jtl` | Validación correcta; 5 de 5 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Smoke | 3 | 5 | 5 | 4.024 | 74 | 74 | 1.24 | 0.00 | `resultados/jmeter/get/smoke/pareto_get_smoke_run03.jtl` | Validación correcta; 5 de 5 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Smoke | 4 | 5 | 5 | 4.034 | 79 | 79 | 1.24 | 0.00 | `resultados/jmeter/get/smoke/pareto_get_smoke_run04.jtl` | Validación correcta; 5 de 5 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Baja | 1 | 30 | 10 | 9.707 | 75 | 81 | 3.09 | 0.00 | `resultados/jmeter/get/baja/pareto_get_baja_run01.jtl` | 30 de 30 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Baja | 2 | 30 | 10 | 9.704 | 78 | 78 | 3.09 | 0.00 | `resultados/jmeter/get/baja/pareto_get_baja_run02.jtl` | 30 de 30 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Baja | 3 | 30 | 10 | 9.703 | 73 | 74 | 3.09 | 0.00 | `resultados/jmeter/get/baja/pareto_get_baja_run03.jtl` | 30 de 30 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Baja | 4 | 30 | 10 | 9.704 | 72 | 72 | 3.09 | 0.00 | `resultados/jmeter/get/baja/pareto_get_baja_run04.jtl` | 30 de 30 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Media | 1 | 100 | 20 | 19.850 | 61 | 67 | 5.04 | 0.00 | `resultados/jmeter/get/media/pareto_get_media_run01.jtl` | 100 de 100 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Media | 2 | 100 | 20 | 19.854 | 69 | 74 | 5.04 | 0.00 | `resultados/jmeter/get/media/pareto_get_media_run02.jtl` | 100 de 100 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Media | 3 | 100 | 20 | 19.842 | 65 | 71 | 5.04 | 0.00 | `resultados/jmeter/get/media/pareto_get_media_run03.jtl` | 100 de 100 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Media | 4 | 100 | 20 | 19.842 | 67 | 70 | 5.04 | 0.00 | `resultados/jmeter/get/media/pareto_get_media_run04.jtl` | 100 de 100 solicitudes exitosas; comportamiento estable. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 1 | 450 | 50 | 49.897 | 56 | 59 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run01.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 2 | 450 | 50 | 49.861 | 54 | 59 | 9.03 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run02.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 3 | 450 | 50 | 49.864 | 57 | 64 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run03.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 4 | 450 | 50 | 49.859 | 56 | 60 | 9.03 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run04.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 5 | 450 | 50 | 49.886 | 56 | 59 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run05.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 6 | 450 | 50 | 49.867 | 56 | 57 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run06.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 7 | 450 | 50 | 49.889 | 55 | 61 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run07.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Operación normal | 8 | 450 | 50 | 49.864 | 56 | 58 | 9.02 | 0.00 | `resultados/jmeter/get/normal/pareto_get_normal_run08.jtl` | Cumple ASR 1; p99 menor que 1000 ms. |
| Pareto 80/20 | GET productos disponibles | Alta | 1 | 1500 | 75 | 75.016 | 60.16 | 63.75 | 20.00 | 0.00 | `resultados/python/get/alta/pareto_get_alta_run01.csv` | Cumple ASR 1; ejecutor Python, una solicitud por usuario. |
| Pareto 80/20 | GET productos disponibles | Alta | 2 | 1500 | 75 | 75.011 | 59.70 | 62.61 | 20.00 | 0.00 | `resultados/python/get/alta/pareto_get_alta_run02.csv` | Cumple ASR 1; ejecutor Python, una solicitud por usuario. |
| Pareto 80/20 | GET productos disponibles | Alta | 3 | 1500 | 75 | 75.004 | 59.66 | 62.98 | 20.00 | 0.00 | `resultados/python/get/alta/pareto_get_alta_run03.csv` | Cumple ASR 1; ejecutor Python, una solicitud por usuario. |
| Pareto 80/20 | GET productos disponibles | Alta | 4 | 1500 | 75 | 75.007 | 60.14 | 62.87 | 20.00 | 0.00 | `resultados/python/get/alta/pareto_get_alta_run04.csv` | Cumple ASR 1; ejecutor Python, una solicitud por usuario. |
| Pareto 80/20 | GET productos disponibles | Muy alta | 1 | 3000 | 100 | 100.035 | 65.52 | 69.07 | 29.99 | 0.00 | `resultados/python/get/muy-alta/pareto_get_muy_alta_run01.csv` | Cumple ASR 1; no se observa punto de inflexión. |
| Pareto 80/20 | GET productos disponibles | Muy alta | 2 | 3000 | 100 | 100.028 | 64.89 | 68.17 | 29.99 | 0.00 | `resultados/python/get/muy-alta/pareto_get_muy_alta_run02.csv` | Cumple ASR 1; no se observa punto de inflexión. |
| Pareto 80/20 | GET productos disponibles | Muy alta | 3 | 3000 | 100 | 100.029 | 64.57 | 67.64 | 29.99 | 0.00 | `resultados/python/get/muy-alta/pareto_get_muy_alta_run03.csv` | Cumple ASR 1; no se observa punto de inflexión. |
| Pareto 80/20 | GET productos disponibles | Muy alta | 4 | 3000 | 100 | 100.032 | 64.39 | 68.50 | 29.99 | 0.00 | `resultados/python/get/muy-alta/pareto_get_muy_alta_run04.csv` | Cumple ASR 1; no se observa punto de inflexión. |
| Pareto 80/20 | GET productos disponibles | Estrés | 1 | 7500 | 150 | 150.063 | 76.62 | 79.76 | 49.98 | 0.00 | `resultados/python/get/estres/pareto_get_estres_run01.csv` | Cumple ASR 1; 7.500 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Estrés | 2 | 7500 | 150 | 150.064 | 74.57 | 78.50 | 49.98 | 0.00 | `resultados/python/get/estres/pareto_get_estres_run02.csv` | Cumple ASR 1; 7.500 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Estrés | 3 | 7500 | 150 | 150.065 | 78.61 | 81.68 | 49.98 | 0.00 | `resultados/python/get/estres/pareto_get_estres_run03.csv` | Cumple ASR 1; 7.500 solicitudes exitosas. |
| Pareto 80/20 | GET productos disponibles | Estrés | 4 | 7500 | 150 | 150.062 | 73.84 | 77.18 | 49.98 | 0.00 | `resultados/python/get/estres/pareto_get_estres_run04.csv` | Cumple ASR 1; 7.500 solicitudes exitosas. |

## Incidencias y decisiones

Registrar aquí cualquier corrida descartada, reinicio de base de datos, cambio
de configuración o condición externa que pueda afectar la comparación.

- Seed Pareto inicial: completado correctamente en aproximadamente 65 segundos.
- Validación funcional posterior al seed: GET HTTP 200, 8 productos, 2.874 bytes
  y 0,120183 segundos. Es un control funcional, no una corrida oficial.
- La tabla `promocion_tiendas` contiene 241 filas para 240 promociones porque
  `seed.sql` aporta una asociación base adicional.
- Primera validación del ejecutor Python descartada: la API estaba detenida y
  las 42.223 solicitudes fallaron por conexión. A partir de esta incidencia se
  agregó una verificación previa de `/health` para abortar antes de generar
  carga cuando el sistema bajo prueba no esté disponible. El CSV inválido se
  conserva localmente, pero se excluye de Git debido a que ocupa 15 MB; la
  captura `25a` documenta la incidencia.
- Validación funcional GET del ejecutor Python: 327 solicitudes en 5,061 s,
  64,61 req/s, p95 de 73,48 ms, p99 de 78,10 ms y 0 % de errores.
- Validación funcional POST con cuerpo de 24 ítems: 227 solicitudes en 3,023 s,
  75,10 req/s, p95 de 26,76 ms, p99 de 29,28 ms y 0 % de errores. Todas las
  respuestas inspeccionadas en el CSV fueron HTTP 201.
