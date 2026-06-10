# datos/evento_real.py
# Datos reales del evento del 12 de junio — completar después del testeo sensorial
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

# Completar con los datos reales post-evento
RESULTADOS_EVENTO = {
    # Flujo de personas
    "asistentes_reales": None,               # int: cuántos asistieron
    "tiempo_formulario_real_min": None,      # float: tiempo promedio del formulario (min)
    "picos_carga_reales": None,              # int: cuántas personas tuvieron que esperar

    # Stock de porciones
    "porciones_consumidas_reales": None,     # int: porciones efectivamente consumidas
    "desperdicio_real": None,                # int: porciones sobrantes/desperdiciadas

    # Viabilidad / Sensorial
    "aceptacion_sensorial_real_pct": None,   # float: % de evaluaciones positivas (1-100)
    "costo_real_por_budin": None,            # float: costo real medido en el evento ($)

    # Metadata
    "fecha_evento": "2026-06-12",
    "completado": False,                     # cambiar a True al cargar los datos reales
}
