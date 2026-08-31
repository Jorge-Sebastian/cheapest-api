# Pruebas de carga alta con Python

Este ejecutor asíncrono se usa exclusivamente para los escenarios mayores a
450 usuarios, como exige el laboratorio. Utiliza una sola dependencia externa:
`aiohttp`.

## Preparación

Desde la raíz de `cheapest-api`:

```bash
python3 -m venv .venv-load
source .venv-load/bin/activate
python -m pip install -r pruebas-carga/python/requirements.txt
```

La API y PostgreSQL deben estar activos antes de cada corrida.

## Argumentos

- `--endpoint`: `GET` o `POST`.
- `--users`: concurrencia máxima.
- `--ramp-up`: segundos durante los que se incorporan usuarios gradualmente.
- `--duration`: duración total de la prueba, incluyendo el ramp-up.
- `--output`: CSV único de la corrida; nunca se sobrescribe.
- `--body`: plantilla JSON obligatoria para POST.
- `--base-url`, `--timeout`, `--tienda-id` y `--zona`: ajustes opcionales.

Cada usuario realiza solicitudes sucesivas desde su incorporación hasta el fin
de la duración. Por eso `duration` debe ser mayor que `ramp-up`, permitiendo un
periodo de carga sostenida después de incorporar al último usuario.

## Ejemplos de validación

GET pequeño:

```bash
python pruebas-carga/python/load_test.py \
  --endpoint GET --users 5 --ramp-up 2 --duration 5 \
  --output pruebas-carga/resultados/python/get/validacion/results_get.csv
```

POST pequeño con pedido de 24 ítems:

```bash
python pruebas-carga/python/load_test.py \
  --endpoint POST --users 2 --ramp-up 1 --duration 3 \
  --body pruebas-carga/python/sample_body.json \
  --output pruebas-carga/resultados/python/post/validacion/results_post.csv
```

El CSV contiene una fila por solicitud con timestamp, método, endpoint, estado,
latencia y error. Al terminar se imprime total, duración, throughput, promedio,
p95, p99 y porcentaje de errores.
