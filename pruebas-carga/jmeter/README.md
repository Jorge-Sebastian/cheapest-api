# Pruebas GET con JMeter

El plan `get-productos-disponibles.jmx` prueba únicamente el endpoint del ASR 1.
Los valores de usuarios, ramp-up y loops se reciben como propiedades para no
editar manualmente el archivo entre corridas.

## Ejecución

Desde la raíz de `cheapest-api`:

```bash
./pruebas-carga/jmeter/run-get.sh <escenario> <corrida> <usuarios> <ramp-up> <loops>
```

Ejemplo de smoke test:

```bash
./pruebas-carga/jmeter/run-get.sh smoke 1 5 5 1
```

Cada ejecución crea un `.jtl` y un `.log` independientes dentro de
`pruebas-carga/resultados/jmeter/get/<escenario>/`. El script se niega a
sobrescribir una corrida existente.

## Matriz hasta 450 usuarios

| Escenario | Usuarios | Ramp-up | Loops | Repeticiones mínimas |
| --- | ---: | ---: | ---: | ---: |
| Smoke | 5 | 5 s | 1 | 4 |
| Baja | 30 | 10 s | 1 | 4 |
| Media | 100 | 20 s | 1 | 4 |
| Operación normal | 450 | 50 s | 1 | 8 |

Para cargas superiores se usa el script asíncrono de Python exigido por el
laboratorio.
