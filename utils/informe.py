# utils/informe.py
# Generación de informe académico en Markdown descargable
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

from datetime import date


def generar_informe(
    metricas_flujo: dict | None = None,
    metricas_stock: dict | None = None,
    metricas_viabilidad: dict | None = None,
    params_flujo: dict | None = None,
    params_stock: dict | None = None,
    params_viabilidad: dict | None = None,
) -> str:
    """
    Genera un informe académico en formato Markdown con los resultados
    de los tres simuladores. Incluye parámetros usados, métricas clave
    y recomendaciones automáticas.

    Retorna:
        - str: contenido del informe en Markdown
    """
    hoy = date.today().strftime("%d/%m/%Y")

    secciones = []

    secciones.append(_encabezado(hoy))

    if metricas_flujo:
        secciones.append(_seccion_flujo(metricas_flujo, params_flujo or {}))

    if metricas_stock:
        secciones.append(_seccion_stock(metricas_stock, params_stock or {}))

    if metricas_viabilidad:
        secciones.append(_seccion_viabilidad(metricas_viabilidad, params_viabilidad or {}))

    secciones.append(_pie_de_pagina())

    return "\n\n".join(secciones)


# ─────────────────────────────────────────
# SECCIONES DEL INFORME
# ─────────────────────────────────────────

def _encabezado(fecha: str) -> str:
    return f"""# Informe de Simulación — Nutridin

**Universidad de la Cuenca del Plata · ISI 4to Año · LN · Grupo 3 · 2026**
**Modelos y Simulación · Tecnología, Ciencia y Responsabilidad Social**

Producto: Nutridin (Budín de Lentejas, Manzana y Zucchini)
Fecha de generación: {fecha}

---"""


def _seccion_flujo(metricas: dict, params: dict) -> str:
    lineas = [
        "## Simulador 1 — Flujo de Personas y Formulario Digital",
        "",
        "**Modelo:** Simulación de eventos discretos",
        "",
        "### Parámetros utilizados",
        "",
    ]

    if params:
        lineas += [
            f"- Comensales simulados: {params.get('comensales', '-')}",
            f"- Tasa de llegada: {params.get('tasa_llegada_min', '-')} – {params.get('tasa_llegada_max', '-')} personas/min",
            f"- Tiempo de degustación: {params.get('t_degustacion_min', '-')} – {params.get('t_degustacion_max', '-')} min",
            f"- Tiempo de formulario: {params.get('t_formulario_min', '-')} – {params.get('t_formulario_max', '-')} min",
            f"- Capacidad del sistema: {params.get('capacidad_sistema', '-')} personas",
        ]

    lineas += [
        "",
        "### Resultados",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Comensales simulados | {metricas.get('comensales', '-')} |",
        f"| Duración total del evento | {metricas.get('tiempo_total_evento', '-')} min |",
        f"| Tiempo promedio en el sistema | {metricas.get('tiempo_promedio_sistema', '-')} min |",
        f"| Tiempo promedio de degustación | {metricas.get('tiempo_promedio_degustacion', '-')} min |",
        f"| Tiempo promedio de formulario | {metricas.get('tiempo_promedio_formulario', '-')} min |",
        f"| Comensales con espera | {metricas.get('comensales_con_espera', '-')} |",
        f"| % de saturación | {metricas.get('pct_saturacion', '-')}% |",
        f"| Nivel de saturación | {metricas.get('saturacion', '-')} |",
        "",
        "### Recomendación",
        "",
        f"> {metricas.get('recomendacion', '-')}",
        "",
        "---",
    ]

    return "\n".join(lineas)


def _seccion_stock(metricas: dict, params: dict) -> str:
    lineas = [
        "## Simulador 2 — Stock de Porciones",
        "",
        "**Modelo:** Monte Carlo",
        "",
        "### Parámetros utilizados",
        "",
    ]

    if params:
        lineas += [
            f"- Comensales esperados: {params.get('comensales_esperados', '-')}",
            f"- % de consumo: {int(params.get('pct_consumo_min', 0) * 100)}% – {int(params.get('pct_consumo_max', 0) * 100)}%",
            f"- Lotes preparados: {params.get('lotes_preparados', '-')}",
            f"- Budines por lote: {params.get('budines_por_lote', '-')}",
            f"- Iteraciones: {params.get('iteraciones', 1000)}",
        ]

    lineas += [
        "",
        "### Resultados",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Porciones disponibles | {metricas.get('total_porciones', '-')} |",
        f"| Demanda promedio | {metricas.get('demanda_promedio', '-')} porciones |",
        f"| Demanda mínima | {metricas.get('demanda_minima', '-')} porciones |",
        f"| Demanda máxima | {metricas.get('demanda_maxima', '-')} porciones |",
        f"| Probabilidad de quiebre | {metricas.get('prob_quiebre', '-')}% |",
        f"| Desperdicio promedio | {metricas.get('desperdicio_promedio', '-')} porciones |",
        f"| Porciones recomendadas (p90) | {metricas.get('porciones_recomendadas', '-')} |",
        f"| Lotes recomendados | {metricas.get('lotes_recomendados', '-')} |",
        "",
        "### Recomendación",
        "",
        f"> {metricas.get('recomendacion', '-')}",
        "",
        "---",
    ]

    return "\n".join(lineas)


def _seccion_viabilidad(metricas: dict, params: dict) -> str:
    lineas = [
        "## Simulador 3 — Viabilidad Productiva y Comercial",
        "",
        "**Modelo:** Monte Carlo económico",
        "",
        "### Parámetros utilizados",
        "",
    ]

    if params:
        lineas += [
            f"- Lotes por día: {params.get('lotes_por_dia', '-')}",
            f"- Días de producción/mes: {params.get('dias_produccion_mes', '-')}",
            f"- Precio de venta: ${params.get('precio_venta', '-'):,.0f}" if isinstance(params.get('precio_venta'), (int, float)) else f"- Precio de venta: {params.get('precio_venta', '-')}",
            f"- Costos fijos mensuales: ${params.get('costos_fijos_mensuales', '-'):,.0f}" if isinstance(params.get('costos_fijos_mensuales'), (int, float)) else f"- Costos fijos mensuales: {params.get('costos_fijos_mensuales', '-')}",
            f"- Variación de costos: ±{params.get('margen_variacion_costos_pct', '-')}%",
            f"- Aceptación sensorial esperada: {params.get('aceptacion_sensorial_pct', '-')}%",
            f"- Iteraciones: {params.get('iteraciones', 1000)}",
        ]

    ganancia_prom = metricas.get('ganancia_promedio', 0)
    ganancia_str = f"${ganancia_prom:,.0f}" if isinstance(ganancia_prom, (int, float)) else str(ganancia_prom)

    lineas += [
        "",
        "### Resultados",
        "",
        f"| Métrica | Valor |",
        f"|---------|-------|",
        f"| Costo MP por budín | ${metricas.get('costo_mp_base', '-'):,.0f} |" if isinstance(metricas.get('costo_mp_base'), (int, float)) else f"| Costo MP por budín | {metricas.get('costo_mp_base', '-')} |",
        f"| Costo mano de obra/budín | ${metricas.get('costo_mo_por_budin', '-'):,.0f} |" if isinstance(metricas.get('costo_mo_por_budin'), (int, float)) else f"| Costo mano de obra/budín | {metricas.get('costo_mo_por_budin', '-')} |",
        f"| Costo total por budín | ${metricas.get('costo_total_budin', '-'):,.0f} |" if isinstance(metricas.get('costo_total_budin'), (int, float)) else f"| Costo total por budín | {metricas.get('costo_total_budin', '-')} |",
        f"| Budines por mes | {metricas.get('budines_por_mes', '-')} |",
        f"| Ganancia promedio mensual | {ganancia_str} |",
        f"| Probabilidad de viabilidad | {metricas.get('prob_viabilidad', '-')}% |",
        f"| Punto de equilibrio promedio | {metricas.get('punto_equilibrio_promedio', '-')} uds |",
        f"| Clasificación | {metricas.get('viabilidad', '-')} |",
        "",
        "### Recomendación",
        "",
        f"> {metricas.get('recomendacion', '-')}",
        "",
        "---",
    ]

    return "\n".join(lineas)


def _pie_de_pagina() -> str:
    return """## Notas metodológicas

- Los simuladores de Monte Carlo utilizaron **1000 iteraciones** con semilla aleatoria fija (`seed=42`) para reproducibilidad.
- El simulador de flujo de personas utiliza un modelo de **eventos discretos** con distribución uniforme de tiempos.
- Los escenarios (Optimista, Esperado, Pesimista) modifican parámetros reales del modelo, no son etiquetas decorativas.
- Los resultados son de naturaleza **probabilística**: representan distribuciones de posibles resultados, no valores exactos.

*Generado automáticamente por el Simulador de Producción Masiva — Grupo 3 · UCP · 2026*"""
