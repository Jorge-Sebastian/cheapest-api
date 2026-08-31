# Prompt utilizado para generar el ejecutor de carga alta

Genera para Cheapest un script de carga en Python con `asyncio` y exactamente
una dependencia, `aiohttp`. Debe probar los endpoints GET de productos
disponibles y POST de pedidos, y aceptar `--endpoint`, `--users`, `--ramp-up`,
`--duration`, `--body`, `--base-url`, `--timeout` y `--output`.

El script debe registrar por solicitud timestamp ISO, método, URL, código HTTP,
latencia y error; considerar error los HTTP >= 400, timeouts y fallos de
conexión; exportar CSV; y calcular total, duración, throughput, promedio, p95,
p99 y porcentaje de error. Para POST debe validar una plantilla con más de 20
ítems y generar identificador y fecha únicos por solicitud. Debe limitar la
concurrencia, aplicar ramp-up gradual, manejar excepciones y negarse a
sobrescribir resultados existentes. Incluye documentación y ejemplos para la
matriz de alta carga del laboratorio.
