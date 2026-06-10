# datos/parametros.py
# Valores por defecto del proceso productivo del Budín Nutritivo
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

# ─────────────────────────────────────────
# RECETA (1 budín)
# ─────────────────────────────────────────
RECETA = {
    "lentejas_cocidas_g": 200,
    "harina_avena_g": 50,
    "zucchini_rallado_g": 120,
    "manzana_rallada_g": 180,
    "huevos_unidades": 2,
    "cacao_amargo_g": 15,
    "miel_g": 60,
    "polvo_hornear_g": 5,
    "esencia_vainilla_ml": 5,
    "aceite_ml": 30,
}

# ─────────────────────────────────────────
# PRECIOS DE REFERENCIA (ARS · junio 2026)
# ─────────────────────────────────────────
PRECIOS = {
    "lentejas_por_kg": 4500,
    "harina_avena_por_kg": 3500,
    "zucchini_por_kg": 2500,
    "manzana_por_kg": 2000,
    "huevos_por_docena": 4000,
    "cacao_por_kg": 12000,
    "miel_por_kg": 6000,
    "polvo_hornear_por_kg": 3000,
    "esencia_vainilla_por_litro": 5000,
    "aceite_por_litro": 2500,
}

# ─────────────────────────────────────────
# TIEMPOS DEL PROCESO (minutos)
# ─────────────────────────────────────────
TIEMPOS = {
    "preparacion_min": 10,
    "preparacion_max": 15,
    "coccion_lentejas_min": 30,
    "coccion_lentejas_max": 35,
    "mezclado_min": 8,
    "mezclado_max": 12,
    "horneado_min": 30,       # actualizar con datos reales del 12/06
    "horneado_max": 35,       # actualizar con datos reales del 12/06
    "temperatura_horno_c": 180,
    "enfriado_min": 20,
    "enfriado_max": 30,
    "envasado_min": 5,
    "envasado_max": 8,
}

# ─────────────────────────────────────────
# CAPACIDAD PRODUCTIVA
# ─────────────────────────────────────────
CAPACIDAD = {
    "budines_por_lote": 4,
    "hornos_disponibles": 1,
    "moldes_disponibles": 4,
    "operarios": 2,
    "jornada_horas": 8,
}

# ─────────────────────────────────────────
# PARÁMETROS COMERCIALES
# ─────────────────────────────────────────
COMERCIAL = {
    "margen_ganancia_pct": 50,
    "costo_mano_obra_hora": 2500,
    "costos_fijos_mensuales": 80000,
    "dias_produccion_mes": 22,
    "lotes_por_dia": 10,
}

# ─────────────────────────────────────────
# PARÁMETROS DEL EVENTO (12/06)
# ─────────────────────────────────────────
EVENTO = {
    "comensales_esperados": 60,
    "comensales_minimo": 50,
    "tiempo_degustacion_min": 3,   # minutos por persona
    "tiempo_degustacion_max": 7,
    "tiempo_formulario_min": 2,    # minutos para completar el QR
    "tiempo_formulario_max": 5,
    "tasa_llegada_personas_min": 1,  # personas por minuto
    "tasa_llegada_personas_max": 3,
}

# ─────────────────────────────────────────
# SEMILLA ALEATORIA
# ─────────────────────────────────────────
SEMILLA = 42