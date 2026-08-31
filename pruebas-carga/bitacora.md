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

## Incidencias y decisiones

Registrar aquí cualquier corrida descartada, reinicio de base de datos, cambio
de configuración o condición externa que pueda afectar la comparación.

- Seed Pareto inicial: completado correctamente en aproximadamente 65 segundos.
- Validación funcional posterior al seed: GET HTTP 200, 8 productos, 2.874 bytes
  y 0,120183 segundos. Es un control funcional, no una corrida oficial.
- La tabla `promocion_tiendas` contiene 241 filas para 240 promociones porque
  `seed.sql` aporta una asociación base adicional.
