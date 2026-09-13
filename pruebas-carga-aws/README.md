# Laboratorio 3 - Pruebas de carga en AWS

Esta carpeta contiene las configuraciones, evidencias y resultados del Laboratorio 3.
El experimento despliega el monolito Cheapest detrás de un Application Load
Balancer con tres instancias EC2 de aplicación y una instancia EC2 para
PostgreSQL.

## Estructura

- `bitacora.md`: decisiones, configuración, incidencias y registro de avances.
- `capturas-de-pantalla/`: evidencias numeradas de AWS y de las pruebas.
- `diagramas/`: diagramas de arquitectura y seguridad.
- `infraestructura/`: información reproducible de los recursos creados, sin secretos.
- `resultados/`: resultados JMeter y Python separados por endpoint.

## Reutilización del Laboratorio 2

- Plan JMeter: `../pruebas-carga/jmeter/get-productos-disponibles.jmx`.
- Ejecutor Python: `../pruebas-carga/python/load_test.py`.
- Cuerpo POST: `../pruebas-carga/python/sample_body.json`.

No se deben versionar credenciales, llaves `.pem`, identificadores de sesión de
AWS Academy, contraseñas nuevas ni archivos `.env`.

