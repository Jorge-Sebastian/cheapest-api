#!/usr/bin/env python3
"""Genera el informe PDF del laboratorio a partir de evidencias del repositorio."""
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-cheapest")
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, ListFlowable, ListItem)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "entregables"
TMP = ROOT / "tmp-informe"
GRAPH = ROOT / "graficas"
CAP = ROOT / "capturas-de-pantalla"
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)
GRAPH.mkdir(exist_ok=True)
PDF = OUT / "informe-laboratorio-2-pruebas-carga.pdf"

font = "Helvetica"
font_bold = "Helvetica-Bold"
for regular, bold in [
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]:
    if Path(regular).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont("ReportFont", regular))
        pdfmetrics.registerFont(TTFont("ReportFont-Bold", bold))
        font, font_bold = "ReportFont", "ReportFont-Bold"
        break

BLUE = colors.HexColor("#17365D")
MID = colors.HexColor("#2E75B6")
LIGHT = colors.HexColor("#D9EAF7")
GRAY = colors.HexColor("#F2F4F7")
INK = colors.HexColor("#20252B")
GREEN = colors.HexColor("#E2F0D9")
AMBER = colors.HexColor("#FFF2CC")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName=font_bold, fontSize=24, leading=29,
                          textColor=BLUE, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName=font, fontSize=13, leading=18,
                          textColor=INK, alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="H1x", fontName=font_bold, fontSize=16, leading=20,
                          textColor=BLUE, spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="H2x", fontName=font_bold, fontSize=12.5, leading=16,
                          textColor=MID, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", fontName=font, fontSize=9.4, leading=13,
                          textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", fontName=font, fontSize=8, leading=10.5,
                          textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle(name="HeaderCellx", fontName=font_bold, fontSize=7.2, leading=9,
                          textColor=colors.white, spaceAfter=0))
styles.add(ParagraphStyle(name="Captionx", fontName=font, fontSize=8, leading=10,
                          textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="Calloutx", fontName=font, fontSize=9, leading=12,
                          textColor=INK, backColor=AMBER, borderColor=colors.HexColor("#D6B656"),
                          borderWidth=.6, borderPadding=8, spaceBefore=5, spaceAfter=8))

def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])

def bullets(items):
    return ListFlowable([ListItem(P(x), leftIndent=10) for x in items], bulletType="bullet",
                        start="circle", leftIndent=18, bulletFontName=font, bulletFontSize=7)

def table(data, widths, font_size=7.2, header=True):
    rendered = []
    for ridx, row in enumerate(data):
        rendered.append([P(str(c), "HeaderCellx" if header and ridx == 0 else "Smallx") for c in row])
    t = Table(rendered, colWidths=widths,
              repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [("GRID", (0,0), (-1,-1), .35, colors.HexColor("#B8C2CC")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]
    if header:
        cmds += [("BACKGROUND", (0,0), (-1,0), BLUE), ("TEXTCOLOR", (0,0), (-1,0), colors.white)]
    for r in range(1 if header else 0, len(data)):
        if r % 2 == 0: cmds.append(("BACKGROUND", (0,r), (-1,r), GRAY))
    t.setStyle(TableStyle(cmds))
    return t

def figure(filename, caption, maxw=6.25*inch, maxh=3.55*inch):
    path = CAP / filename
    if not path.exists(): return [P(f"Evidencia no encontrada: {filename}", "Calloutx")]
    img = Image(str(path))
    ratio = min(maxw/img.imageWidth, maxh/img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth*ratio, img.imageHeight*ratio
    return [KeepTogether([img, P(caption, "Captionx")])]

def make_charts():
    zones = list(range(1, 11))
    uniform = [10]*10
    pareto = [40, 40] + [2.5]*8
    fig, ax = plt.subplots(1,2, figsize=(10,3.5), sharey=True)
    for a, values, title, col in [(ax[0], uniform, "Distribución uniforme", "#5B9BD5"),
                                  (ax[1], pareto, "Distribución Pareto 80/20", "#ED7D31")]:
        a.bar(zones, values, color=col); a.set_title(title); a.set_xlabel("Zona ordenada por demanda")
        a.set_xticks(zones); a.grid(axis="y", alpha=.25)
    ax[0].set_ylabel("Porcentaje de asignaciones")
    fig.suptitle("Comparación conceptual con los mismos ejes y escala")
    fig.tight_layout(); p = GRAPH/"distribuciones.png"; fig.savefig(p, dpi=180); plt.close(fig)

    scenarios = ["Smoke","Baja","Media","Normal","Alta","Muy alta","Estrés"]
    p99 = [84.5,76.25,70.5,59.6,63.05,68.35,79.28]
    thr = [1.24,3.09,5.04,9.02,20,29.99,49.98]
    fig, ax1 = plt.subplots(figsize=(9,4)); ax2=ax1.twinx()
    ax1.plot(scenarios,p99,"o-",color="#C00000",label="p99 promedio")
    ax2.plot(scenarios,thr,"s--",color="#2E75B6",label="Throughput")
    ax1.axhline(1000,color="#777",ls=":",label="ASR 1: 1000 ms")
    ax1.set_ylabel("p99 (ms)"); ax2.set_ylabel("Throughput (req/s)"); ax1.tick_params(axis="x",rotation=25)
    ax1.grid(alpha=.25); fig.suptitle("Evolución observada del endpoint GET")
    lines=ax1.get_lines()+ax2.get_lines(); ax1.legend(lines,[x.get_label() for x in lines],loc="upper left")
    fig.tight_layout(); p2=GRAPH/"resultados_get.png"; fig.savefig(p2,dpi=180); plt.close(fig)

    x=[10,25,50,75,100]
    fig,axs=plt.subplots(1,3,figsize=(11,3.2))
    axs[0].plot(x,[55,58,75,260,900],"o-"); axs[0].axvline(50,ls=":",color="r"); axs[0].set_title("Pool saturado")
    axs[0].set_ylabel("Latencia p99"); axs[0].set_xlabel("Carga req/s")
    axs[1].bar(["Consulta base","Con índice","Consulta simple"],[420,85,35],color=["#C55A11","#70AD47","#5B9BD5"])
    axs[1].set_title("SQL ineficiente"); axs[1].set_ylabel("Latencia p99")
    axs[2].plot(x,[10,25,49,51,51],"o-",label="Generado"); axs[2].plot(x,[10,25,50,75,100],"--",label="Objetivo")
    axs[2].set_title("Límite del generador"); axs[2].set_xlabel("Carga objetivo"); axs[2].set_ylabel("req/s"); axs[2].legend(fontsize=7)
    for a in axs: a.grid(alpha=.2)
    fig.suptitle("Firmas esperadas para distinguir cuellos de botella"); fig.tight_layout()
    p3=GRAPH/"hipotesis.png"; fig.savefig(p3,dpi=180); plt.close(fig)
    return p, p2, p3

def page(canvas, doc):
    canvas.saveState(); canvas.setFont(font,7.5); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(.8*inch,.45*inch,"Arquitecturas de Software - Laboratorio 2")
    canvas.drawRightString(7.7*inch,.45*inch,f"Página {doc.page}"); canvas.restoreState()

dist_chart, result_chart, hyp_chart = make_charts()
story=[]
story += [Spacer(1,1.25*inch), P("LABORATORIO 2", "CoverSub"),
          P("Pruebas de carga del backend monolítico Cheapest", "CoverTitle"),
          P("Informe de resultados, evidencias y análisis arquitectónico", "CoverSub"), Spacer(1,.4*inch),
          table([["Sistema","Cheapest API - NestJS + PostgreSQL"],["Distribución principal","Pareto 80/20"],
                 ["Herramientas","Apache JMeter 5.6.3 y Python aiohttp"],["Entorno","MacBook Pro M5 Pro, 24 GB; PostgreSQL 15 en Docker"],
                 ["Rama","lab-2"],["Fecha","30 de agosto de 2026"]],[1.55*inch,4.5*inch],8.5,False),
          Spacer(1,.35*inch), P("Alcance efectivo", "H2x"),
          P("Se ejecutó la progresión completa del endpoint GET desde smoke hasta estrés, incluyendo las repeticiones mínimas de cada nivel alcanzado. También se validó funcionalmente el POST con un pedido de 24 ítems. Por restricción temporal no se ejecutaron estrés fuerte, la matriz completa del POST ni el control uniforme. El documento distingue resultados observados de propuestas y no fabrica mediciones.", "Calloutx"), PageBreak()]

story += [P("1. Objetivo y ASRs", "H1x"),
          P("El experimento evalúa el comportamiento del backend monolítico ante carga concurrente sobre lectura intensiva y escritura transaccional."),
          table([["ASR","Endpoint","Condición de aceptación"],["ASR 1","GET /logistics/tenderos/productos-disponibles","p99 menor que 1000 ms en operación normal (500 req/min)"],
                 ["ASR 2","POST /logistics/pedidos","Errores menores o iguales al 2% durante el pico estimado (5000 req/min)"]],[.65*inch,3.25*inch,2.25*inch],8),
          P("2. Preparación y validación", "H1x"),
          P("Se verificaron pruebas unitarias (41 suites y 342 pruebas), compilación, PostgreSQL saludable, health check del backend y solicitudes manuales GET/POST. El GET devolvió HTTP 200 y ocho productos; el POST devolvió HTTP 201."),
          *figure("06-postgresql-docker-healthy.png","Figura 1. PostgreSQL ejecutándose correctamente en Docker."),
          *figure("08-get-productos-disponibles.png","Figura 2. Validación manual del endpoint GET: HTTP 200 y ocho productos."), PageBreak()]

story += [P("3. Diseño y distribución de datos", "H1x"),
          P("Los escenarios Pareto y uniforme conservan los mismos totales para aislar el efecto de la distribución. La configuración principal concentra el 80% de las asignaciones en el 20% de tiendas, zonas o productos, representando actores de alto volumen y referencias populares. El control uniforme usa round-robin."),
          table([["Entidad","Volumen","Justificación"],["Tiendas / zonas","3.000 / 10","Heterogeneidad comercial y densidad geográfica"],
                 ["Productos / catálogos","1.200 / 3.000","Catálogo suficiente para JOINs y disponibilidad"],
                 ["Catálogo-producto","600.000","200 referencias promedio por catálogo"],
                 ["Promociones","240","20% del catálogo; el seeder mantiene 70% vigentes"],
                 ["Pedidos / ítems","100.000 / 500.000","Histórico de 33 pedidos por tienda y cinco ítems por pedido"],
                 ["Disponibilidad por zona","600.000","Cobertura comparable con catálogo-producto"],
                 ["Inventario / ventas","300.000 / 150.000","Actividad operativa e histórica representativa"]],[1.55*inch,1.15*inch,3.55*inch],7.5),
          Spacer(1,6), Image(str(dist_chart),width=6.25*inch,height=2.2*inch),
          P("Figura 3. Comparación equivalente: la uniformidad oculta puntos calientes; Pareto reproduce concentración realista.","Captionx"),
          *figure("10-configuracion-pareto-completa.png","Figura 4. Configuración de volúmenes y distribución Pareto 80/20."), PageBreak()]

story += [P("4. Metodología", "H1x"),
          P("JMeter se utilizó hasta 450 usuarios y el ejecutor Python asíncrono para cargas superiores. Cada petición registra timestamp, método, endpoint, código HTTP, latencia y error. El resumen calcula total, throughput, promedio, p95, p99 y porcentaje de error."),
          table([["Escenario","Usuarios","Ramp-up","Repeticiones ejecutadas","Herramienta"],
                 ["Smoke","5","5 s","4","JMeter"],["Baja","30","10 s","4","JMeter"],
                 ["Media","100","20 s","4","JMeter"],["Operación normal","450","50 s","8","JMeter"],
                 ["Alta","1.500","75 s","4","Python"],["Muy alta","3.000","100 s","4","Python"],
                 ["Estrés","7.500","150 s","4","Python"],["Estrés fuerte","18.000","200 s","No ejecutado","Python"]],[1.45*inch,.75*inch,.8*inch,1.55*inch,1.25*inch],7.5),
          *figure("16b-jmeter-get-request-configuracion.png","Figura 5. Sampler GET con servidor, puerto, ruta y parámetros parametrizados."),
          *figure("24-python-aiohttp-script-ayuda.png","Figura 6. Ejecutor Python generado para escenarios superiores a 450 usuarios."), PageBreak()]

rows = [
 ("Smoke",1,5,5,101,101,1.25,0),("Smoke",2,5,5,84,84,1.24,0),("Smoke",3,5,5,74,74,1.24,0),("Smoke",4,5,5,79,79,1.24,0),
 ("Baja",1,30,10,75,81,3.09,0),("Baja",2,30,10,78,78,3.09,0),("Baja",3,30,10,73,74,3.09,0),("Baja",4,30,10,72,72,3.09,0),
 ("Media",1,100,20,61,67,5.04,0),("Media",2,100,20,69,74,5.04,0),("Media",3,100,20,65,71,5.04,0),("Media",4,100,20,67,70,5.04,0),
 ("Normal",1,450,50,56,59,9.02,0),("Normal",2,450,50,54,59,9.03,0),("Normal",3,450,50,57,64,9.02,0),("Normal",4,450,50,56,60,9.03,0),
 ("Normal",5,450,50,56,59,9.02,0),("Normal",6,450,50,56,57,9.02,0),("Normal",7,450,50,55,61,9.02,0),("Normal",8,450,50,56,58,9.02,0),
 ("Alta",1,1500,75,60.16,63.75,20,0),("Alta",2,1500,75,59.70,62.61,20,0),("Alta",3,1500,75,59.66,62.98,20,0),("Alta",4,1500,75,60.14,62.87,20,0),
 ("Muy alta",1,3000,100,65.52,69.07,29.99,0),("Muy alta",2,3000,100,64.89,68.17,29.99,0),("Muy alta",3,3000,100,64.57,67.64,29.99,0),("Muy alta",4,3000,100,64.39,68.50,29.99,0),
 ("Estrés",1,7500,150,76.62,79.76,49.98,0),("Estrés",2,7500,150,74.57,78.50,49.98,0),("Estrés",3,7500,150,78.61,81.68,49.98,0),("Estrés",4,7500,150,73.84,77.18,49.98,0)]
data=[["Escenario","Run","Usuarios","Ramp-up","p95","p99","req/s","Error %"]]+[[*r] for r in rows]
story += [P("5. Resultados obtenidos - GET", "H1x"),
          P("Tabla 1. Resultados completos de las 32 corridas oficiales ejecutadas."),
          table(data,[1.05*inch,.38*inch,.62*inch,.62*inch,.58*inch,.58*inch,.62*inch,.58*inch],6.5),
          PageBreak(), Image(str(result_chart),width=6.25*inch,height=2.75*inch),
          P("Figura 7. El p99 se mantiene muy por debajo de 1000 ms; el throughput sigue la carga objetivo.","Captionx"),
          P("En operación normal, el p99 promedio fue 59,6 ms, aproximadamente 94% menor que el límite del ASR 1. En estrés, el p99 promedio fue 79,28 ms y no hubo errores. No apareció un punto de inflexión hasta 50 req/s."),
          *figure("23a-jmeter-get-normal-corridas-01-02.png","Figura 8. Evidencia de las primeras corridas de operación normal."),
          *figure("28-python-get-muy-alta-corridas-01-04.png","Figura 9. Cuatro corridas GET de muy alta carga sin errores."),
          *figure("29-python-get-estres-corridas-01-04.png","Figura 10. Cuatro corridas GET de estrés: 7.500 solicitudes por corrida y 0% de error."), PageBreak()]

story += [P("6. Validación del endpoint POST", "H1x"),
          P("El POST se validó con un pedido realista de 24 ítems. Produjo 227 solicitudes en 3,023 s, throughput de 75,10 req/s, promedio de 24,41 ms, p95 de 26,76 ms, p99 de 29,28 ms y 0% de errores; las respuestas inspeccionadas fueron HTTP 201. Esta validación prueba la corrección del ejecutor y del cuerpo, pero no sustituye la matriz repetida requerida para concluir sobre ASR 2."),
          *figure("26-python-validacion-post-24-items.png","Figura 11. Validación POST con 24 ítems, HTTP 201 y 0% de errores."),
          P("7. Respuestas solicitadas", "H1x"),
          P("Pregunta 1 - Prioridad de optimización", "H2x"),
          P("Antes de un pico comercial priorizaría POST /logistics/pedidos. La consulta GET afecta descubrimiento y conversión, pero una falla de creación de pedidos produce pérdida directa de ventas, duplicados o inconsistencias. Además, el objetivo de 5000 req/min es casi diez veces la operación normal del GET y la escritura transaccional tiene mayor riesgo de locks y agotamiento del pool. Como mejora inicial de costo moderado aplicaría idempotencia, validaciones anticipadas, transacciones cortas, índices y medición del pool; después desacoplaría procesamiento no crítico."),
          P("Pregunta 2 - Distribuciones y sesgos", "H2x"),
          P("La distribución uniforme reparte actividad por igual y reduce colisiones sobre tiendas, zonas y productos populares. Esto puede producir cachés artificialmente equilibradas, planes de consulta estables y menor contención, desplazando falsamente el punto de inflexión. Pareto valida la capacidad del monolito frente a hotspots realistas. Una segunda estrategia, uniforme, funciona como control para aislar si la degradación proviene del volumen total o de la concentración. Una tercera estrategia útil sería temporal por ráfagas, con una zona dominante y promociones sincronizadas, para validar absorción de picos y recuperación."),
          P("Pregunta 3 - Diseño alternativo para identificar el cuello", "H2x"),
          P("Se propone variar una causa a la vez manteniendo dataset, endpoint, generador y tasa constantes. Para el pool: repetir con tamaños 5, 10, 20 y 40, midiendo espera de adquisición y conexiones activas; saturación mostraría un codo que se desplaza al aumentar el pool. Para SQL: conservar concurrencia y comparar consulta base, EXPLAIN ANALYZE e índices; un gran descenso de latencia sin cambiar pool confirma costo SQL. Para el generador: ejecutar contra un stub liviano, medir CPU/event loop del cliente y repetir desde otra máquina; si el throughput se aplana también contra el stub, el límite está en el generador."),
          Image(str(hyp_chart),width=6.25*inch,height=1.85*inch),
          P("Figura 12. Patrones visuales esperados para las tres hipótesis.","Captionx")]

story += [P("Pregunta 4 - Estrategia de IA para Cheapest", "H2x"),
          P("La consistencia no debe depender únicamente del prompt. La estrategia recomendada combina instrucciones versionadas en el repositorio, una plantilla de tarea con contexto/criterios/restricciones, ejemplos aprobados, recuperación de estándares del equipo y verificación automática. Para Cheapest: (1) crear AGENTS.md o instrucciones equivalentes con arquitectura por capas, TypeScript estricto, DTOs, transacciones, manejo de errores y prohibiciones; (2) mantener plantillas para controladores, servicios, repositorios, pruebas y migraciones; (3) incluir ejemplos de referencia; (4) exigir al agente plan, diff pequeño, pruebas y explicación; (5) ejecutar lint, unitarias, integración, seguridad y revisión humana en CI. Las reglas deben ser concretas, comprobables y cercanas al código. El prompt utilizado para el ejecutor se conserva en pruebas-carga/python/prompt-utilizado.md."),
          P("8. Conclusiones arquitectónicas", "H1x"),
          P("Punto de inflexión y ASR roto", "H2x"),
          P("No se encontró punto de inflexión en el rango medido. ASR 1 cumplió en todas las corridas hasta estrés. ASR 2 no puede declararse cumplido ni incumplido porque solo se realizó una validación, no su matriz oficial. Por ello tampoco es válido afirmar cuál ASR se rompió primero."),
          P("Beneficio del monolito", "H2x"),
          P("Para el GET observado, el despliegue local monolítico favoreció baja latencia al evitar saltos de red entre módulos y permitir acceso directo al mismo PostgreSQL. Esta evidencia demuestra buen comportamiento en el rango medido, no escalabilidad ilimitada. El acoplamiento de lectura y escritura puede generar competencia por CPU, memoria y conexiones cuando ambos endpoints se prueben simultáneamente."),
          P("Cambios propuestos", "H2x"),
          bullets(["Índices compuestos y revisión con EXPLAIN ANALYZE para filtros de tienda, zona, vigencia y disponibilidad.",
                   "Read-through cache para productos disponibles, con invalidación por zona/promoción.",
                   "Réplicas de lectura o CQRS si el GET domina el consumo.",
                   "Idempotency key, transacciones cortas y cola para tareas secundarias del POST.",
                   "Pool dimensionado con métricas de espera; límites, backpressure y circuit breaker.",
                   "Escalamiento horizontal del backend detrás de un balanceador, manteniendo la base como recurso vigilado."]),
          P("Degradación y endpoint primero", "H2x"),
          P("El GET mostró una degradación suave y pequeña: el p99 promedio pasó de 59,6 ms en operación normal a 79,28 ms en estrés, sin salto abrupto ni errores. No puede localizarse definitivamente un cuello de botella sin telemetría de CPU, pool y SQL. Tampoco puede compararse qué endpoint degradó primero porque no se ejecutó la misma matriz sobre POST. Arquitectónicamente se espera que POST sea más sensible a contención transaccional, pero esto es una hipótesis, no un resultado."),
          P("9. Limitaciones y trabajo pendiente", "H1x"),
          bullets(["Ejecutar ocho corridas de estrés fuerte GET (18.000 usuarios, 90 req/s objetivo).",
                   "Ejecutar la matriz completa del POST y comparar ambos endpoints.",
                   "Cargar el control uniforme con los mismos volúmenes y ejecutar escenarios equivalentes.",
                   "Recolectar CPU, memoria, event-loop lag, conexiones activas, locks y EXPLAIN ANALYZE.",
                   "Ejecutar pruebas conjuntas GET/POST para medir interferencia dentro del monolito."]),
          P("10. Prompts y reproducibilidad", "H1x"),
          P("El prompt de generación del ejecutor, el script, requisitos, cuerpo POST de 24 ítems, plan JMeter, configuraciones de seed, CSV/JTL y bitácora se incluyen en el repositorio. Los resultados inválidos por API detenida se conservaron como incidencia separada y no se mezclaron con las corridas oficiales."),
          P("Comando de regeneración del informe: python3 pruebas-carga/generar_informe.py", "Calloutx"), PageBreak()]

captures=sorted(x.name for x in CAP.glob("*.png"))
story += [P("Anexo A. Inventario de evidencias", "H1x"),
          P("Las siguientes capturas permanecen versionadas como evidencia completa. En el cuerpo se incluyeron las más representativas."),
          bullets(captures),
          P("Anexo B. Trazabilidad de archivos", "H1x"),
          table([["Elemento","Ruta"],["Bitácora","pruebas-carga/bitacora.md"],["Plan GET JMeter","pruebas-carga/jmeter/get-productos-disponibles.jmx"],
                 ["Ejecutor Python","pruebas-carga/python/load_test.py"],["Prompt IA","pruebas-carga/python/prompt-utilizado.md"],
                 ["Resultados","pruebas-carga/resultados/"],["Capturas","pruebas-carga/capturas-de-pantalla/"]],[1.65*inch,4.5*inch],8),
          P("Fin del informe.","Captionx")]

doc=SimpleDocTemplate(str(PDF),pagesize=letter,rightMargin=.75*inch,leftMargin=.75*inch,
                      topMargin=.7*inch,bottomMargin=.7*inch,title="Laboratorio 2 - Pruebas de carga Cheapest",
                      author="Equipo Cheapest")
doc.build(story,onFirstPage=page,onLaterPages=page)
print(PDF)
