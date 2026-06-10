# simuladores/viabilidad.py
# Simulador 3: Viabilidad productiva y comercial
# Modelo: Monte Carlo económico
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

import numpy as np
import pandas as pd
from datos.parametros import RECETA, PRECIOS, TIEMPOS, CAPACIDAD, COMERCIAL, SEMILLA

# ─────────────────────────────────────────
# COSTO DE MATERIA PRIMA
# ─────────────────────────────────────────
def calcular_costo_materia_prima(
    receta: dict = None,
    precios: dict = None,
) -> tuple[float, dict]:
    """
    Calcula el costo de materia prima por unidad (1 budín).
    Retorna el costo total y el desglose por ingrediente.
    """
    receta = receta or RECETA
    precios = precios or PRECIOS

    desglose = {
        "Lentejas": (receta["lentejas_cocidas_g"] / 1000) * precios["lentejas_por_kg"],
        "Harina de avena": (receta["harina_avena_g"] / 1000) * precios["harina_avena_por_kg"],
        "Zucchini": (receta["zucchini_rallado_g"] / 1000) * precios["zucchini_por_kg"],
        "Manzana": (receta["manzana_rallada_g"] / 1000) * precios["manzana_por_kg"],
        "Huevos": receta["huevos_unidades"] * (precios["huevos_por_docena"] / 12),
        "Cacao amargo": (receta["cacao_amargo_g"] / 1000) * precios["cacao_por_kg"],
        "Miel/azúcar": (receta["miel_g"] / 1000) * precios["miel_por_kg"],
        "Polvo de hornear": (receta["polvo_hornear_g"] / 1000) * precios["polvo_hornear_por_kg"],
        "Esencia de vainilla": (receta["esencia_vainilla_ml"] / 1000) * precios["esencia_vainilla_por_litro"],
        "Aceite": (receta["aceite_ml"] / 1000) * precios["aceite_por_litro"],
    }

    costo_total = sum(desglose.values())
    return costo_total, desglose


# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────
def simular_viabilidad(
    lotes_por_dia: int,
    budines_por_lote: int,
    dias_produccion_mes: int,
    precio_venta: float,
    costos_fijos_mensuales: float,
    costo_mano_obra_hora: float,
    margen_variacion_costos_pct: float,
    aceptacion_sensorial_pct: float,
    iteraciones: int = 1000,
    semilla: int = SEMILLA,
) -> tuple[pd.DataFrame, dict]:
    """
    Simula la viabilidad comercial del budín usando Monte Carlo económico.

    En cada iteración varía:
        - Costo de materia prima (±margen_variacion_costos_pct)
        - Demanda real (afectada por aceptación sensorial)
        - Precio de venta (±5% variación de mercado)

    Retorna:
        - df: DataFrame con el resultado de cada iteración
        - metricas: dict con los indicadores principales
    """
    np.random.seed(semilla)

    # Costo base de materia prima
    costo_mp_base, _ = calcular_costo_materia_prima()

    # Tiempo promedio por lote en horas
    t_prom_lote = (
        (TIEMPOS["preparacion_min"] + TIEMPOS["preparacion_max"]) / 2 +
        (TIEMPOS["coccion_lentejas_min"] + TIEMPOS["coccion_lentejas_max"]) / 2 +
        (TIEMPOS["mezclado_min"] + TIEMPOS["mezclado_max"]) / 2 +
        (TIEMPOS["horneado_min"] + TIEMPOS["horneado_max"]) / 2 +
        (TIEMPOS["enfriado_min"] + TIEMPOS["enfriado_max"]) / 2 +
        (TIEMPOS["envasado_min"] + TIEMPOS["envasado_max"]) / 2
    ) / 60

    costo_mo_por_budin = (costo_mano_obra_hora * t_prom_lote) / budines_por_lote
    budines_por_dia = lotes_por_dia * budines_por_lote
    budines_por_mes = budines_por_dia * dias_produccion_mes

    resultados = []

    for i in range(iteraciones):

        # Variación aleatoria del costo de materia prima
        variacion_costo = np.random.uniform(
            1 - margen_variacion_costos_pct / 100,
            1 + margen_variacion_costos_pct / 100,
        )
        costo_mp_iter = costo_mp_base * variacion_costo
        costo_total_budin = costo_mp_iter + costo_mo_por_budin

        # Variación aleatoria del precio de venta (±5%)
        precio_iter = precio_venta * np.random.uniform(0.95, 1.05)

        # Demanda afectada por aceptación sensorial
        factor_demanda = np.random.uniform(
            aceptacion_sensorial_pct / 100 * 0.9,
            aceptacion_sensorial_pct / 100 * 1.1,
        )
        demanda_real = int(budines_por_mes * factor_demanda)

        # Ingresos y costos
        ingreso = demanda_real * precio_iter
        costo_variable = demanda_real * costo_total_budin
        costo_total = costo_variable + costos_fijos_mensuales
        ganancia = ingreso - costo_total

        # Punto de equilibrio
        contribucion = precio_iter - costo_total_budin
        pe = costos_fijos_mensuales / contribucion if contribucion > 0 else float("inf")

        resultados.append({
            "Iteración": i + 1,
            "Costo MP/budín ($)": round(costo_mp_iter, 0),
            "Costo total/budín ($)": round(costo_total_budin, 0),
            "Precio venta ($)": round(precio_iter, 0),
            "Demanda (uds)": demanda_real,
            "Ingreso ($)": round(ingreso, 0),
            "Costo total ($)": round(costo_total, 0),
            "Ganancia ($)": round(ganancia, 0),
            "Punto equilibrio (uds)": round(pe, 0) if pe != float("inf") else 0,
            "Viable": "✅ Sí" if ganancia > 0 else "❌ No",
        })

    df = pd.DataFrame(resultados)

    # ─────────────────────────────────────────
    # MÉTRICAS
    # ─────────────────────────────────────────
    viables = df[df["Ganancia ($)"] > 0]
    prob_viabilidad = len(viables) / iteraciones * 100

    metricas = {
        "costo_mp_base": round(costo_mp_base, 0),
        "costo_mo_por_budin": round(costo_mo_por_budin, 0),
        "costo_total_budin": round(costo_mp_base + costo_mo_por_budin, 0),
        "budines_por_mes": budines_por_mes,
        "ganancia_promedio": round(df["Ganancia ($)"].mean(), 0),
        "ganancia_minima": round(df["Ganancia ($)"].min(), 0),
        "ganancia_maxima": round(df["Ganancia ($)"].max(), 0),
        "prob_viabilidad": round(prob_viabilidad, 1),
        "punto_equilibrio_promedio": round(df["Punto equilibrio (uds)"].mean(), 0),
        "precio_venta": precio_venta,
        "viabilidad": _clasificar_viabilidad(prob_viabilidad),
        "recomendacion": _recomendacion_viabilidad(prob_viabilidad, aceptacion_sensorial_pct),
    }

    return df, metricas


# ─────────────────────────────────────────
# ESCENARIOS
# ─────────────────────────────────────────
def escenarios_viabilidad() -> dict:
    """
    Define los tres escenarios del simulador de viabilidad.
    Modifica parámetros reales del modelo, no son solo etiquetas.
    """
    return {
        "optimista": {
            "nombre": "🟢 Optimista",
            "lotes_por_dia": 15,
            "precio_venta": 5500,
            "costos_fijos_mensuales": 70000,
            "margen_variacion_costos_pct": 5,
            "aceptacion_sensorial_pct": 80,
            "descripcion": "Alta producción, buen precio, alta aceptación sensorial.",
        },
        "esperado": {
            "nombre": "🟡 Esperado",
            "lotes_por_dia": 10,
            "precio_venta": 4500,
            "costos_fijos_mensuales": 80000,
            "margen_variacion_costos_pct": 15,
            "aceptacion_sensorial_pct": 65,
            "descripcion": "Condiciones probables basadas en datos reales.",
        },
        "pesimista": {
            "nombre": "🔴 Pesimista",
            "lotes_por_dia": 5,
            "precio_venta": 3800,
            "costos_fijos_mensuales": 90000,
            "margen_variacion_costos_pct": 25,
            "aceptacion_sensorial_pct": 40,
            "descripcion": "Baja producción, precio bajo, baja aceptación sensorial.",
        },
    }


# ─────────────────────────────────────────
# VALIDACIÓN POST-EVENTO
# ─────────────────────────────────────────
def validar_con_reales(
    metricas_simuladas: dict,
    aceptacion_real_pct: float,
    costo_real_por_budin: float,
) -> pd.DataFrame:
    """
    Compara los resultados simulados con los datos reales post-evento.
    """
    comparacion = {
        "Variable": [
            "Costo MP por budín ($)",
            "Ganancia promedio mensual ($)",
            "Probabilidad de viabilidad (%)",
        ],
        "Simulado": [
            metricas_simuladas["costo_mp_base"],
            metricas_simuladas["ganancia_promedio"],
            metricas_simuladas["prob_viabilidad"],
        ],
        "Real": [
            costo_real_por_budin,
            "-",
            f"Aceptación real: {aceptacion_real_pct}%",
        ],
    }

    df = pd.DataFrame(comparacion)
    return df


# ─────────────────────────────────────────
# CLASIFICACIÓN Y RECOMENDACIÓN
# ─────────────────────────────────────────
def _clasificar_viabilidad(prob_viabilidad: float) -> str:
    if prob_viabilidad >= 70:
        return "✅ Viable"
    elif prob_viabilidad >= 40:
        return "⚠️ Parcialmente viable"
    else:
        return "❌ No viable"


def _recomendacion_viabilidad(
    prob_viabilidad: float,
    aceptacion_sensorial_pct: float,
) -> str:
    if prob_viabilidad >= 70:
        return (
            f"El producto es viable comercialmente con una probabilidad del "
            f"{prob_viabilidad:.1f}%. La aceptación sensorial del "
            f"{aceptacion_sensorial_pct:.1f}% respalda su potencial de mercado. "
            f"Se recomienda avanzar con la planificación de producción a escala."
        )
    elif prob_viabilidad >= 40:
        return (
            f"El producto es parcialmente viable con una probabilidad del "
            f"{prob_viabilidad:.1f}%. Se recomienda revisar la estructura de costos "
            f"y evaluar ajustes en la formulación o el precio de venta para mejorar "
            f"la rentabilidad antes de escalar la producción."
        )
    else:
        return (
            f"El producto no es viable en las condiciones actuales "
            f"(probabilidad del {prob_viabilidad:.1f}%). "
            f"Se recomienda reformular los costos, revisar el precio de venta "
            f"y mejorar la aceptación sensorial antes de considerar la producción a escala."
        )