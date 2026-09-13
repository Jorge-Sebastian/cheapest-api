# Bitácora - Laboratorio 3

## Estado del laboratorio

| Etapa | Estado | Evidencia |
|---|---|---|
| Rama `lab-3` creada y publicada | Completada | Git local y GitHub |
| Security Groups | Pendiente | `capturas-de-pantalla/` |
| EC2 PostgreSQL | Pendiente | `capturas-de-pantalla/` |
| Tres EC2 de aplicación | Pendiente | `capturas-de-pantalla/` |
| Target Group y ALB | Pendiente | `capturas-de-pantalla/` |
| Validación por DNS del ALB | Pendiente | `capturas-de-pantalla/` |
| Matriz GET | Pendiente | `resultados/` |
| Matriz POST | Pendiente | `resultados/` |
| Análisis e informe | Pendiente | Informe final |
| Recursos AWS detenidos o eliminados | Pendiente | `capturas-de-pantalla/` |

## Ambiente objetivo

| Recurso | Configuración |
|---|---|
| Base de datos | `Cheapest-db`, EC2 `t2.medium`, PostgreSQL en Docker |
| Aplicación 1 | `Cheapest-app-1`, EC2 `t2.medium`, `us-east-1a` |
| Aplicación 2 | `Cheapest-app-2`, EC2 `t2.medium`, `us-east-1b` |
| Aplicación 3 | `Cheapest-app-3`, EC2 `t2.medium`, `us-east-1c` |
| Entrada | Application Load Balancer |
| Generador de carga | Computador personal con JMeter y Python |

## Registro de recursos

Complete esta tabla sin copiar secretos ni credenciales.

| Recurso | Identificador o DNS | IP privada | AZ | Estado |
|---|---|---|---|---|
| Cheapest-db | | | | Pendiente |
| Cheapest-app-1 | | | `us-east-1a` | Pendiente |
| Cheapest-app-2 | | | `us-east-1b` | Pendiente |
| Cheapest-app-3 | | | `us-east-1c` | Pendiente |
| Target Group | | N/A | Regional | Pendiente |
| ALB | | N/A | Regional | Pendiente |

## Registro de decisiones e incidencias

- Se parte de la rama `lab-2` para reutilizar el seed, JMeter y el ejecutor Python.
- Los resultados del Lab 3 se almacenan aparte para no mezclarlos con mediciones locales.

## Convención para capturas

Use nombres consecutivos y descriptivos, por ejemplo:

```text
01-aws-academy-lab-activo.png
02-security-groups-creados.png
03-ec2-cheapest-db-running.png
```

