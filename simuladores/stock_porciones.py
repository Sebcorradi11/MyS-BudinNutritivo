# simuladores/stock_porciones.py
# Simulador 2: Stock de porciones
# Modelo: Monte Carlo
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

import numpy as np
import pandas as pd
from datos.parametros import SEMILLA

# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────
def simular_stock(
    comensales_esperados: int,
    pct_consumo_min: float,
    pct_consumo_max: float,
    budines_por_lote: int,
    porciones_por_budin: int,
    lotes_preparados: int,
    iteraciones: int = 1000,
    semilla: int = SEMILLA,
) -> tuple[pd.DataFrame, dict]:
    """
    Simula la demanda de porciones durante el evento usando Monte Carlo.

    En cada iteración:
        1. Se sortea cuántos comensales asisten (variabilidad de asistencia)
        2. Se sortea qué porcentaje de ellos consume el budín
        3. Se calcula si hay quiebre de stock o desperdicio

    Cada lote produce: budines_por_lote × porciones_por_budin porciones.

    Retorna:
        - df: DataFrame con el resultado de cada iteración
        - metricas: dict con los indicadores principales
    """
    np.random.seed(semilla)

    total_porciones = lotes_preparados * budines_por_lote * porciones_por_budin
    resultados = []

    for i in range(iteraciones):

        # Asistencia variable (entre 80% y 100% de los esperados)
        asistentes = int(np.random.uniform(
            comensales_esperados * 0.8,
            comensales_esperados * 1.0,
        ))

        # Porcentaje de consumo variable
        pct_consumo = np.random.uniform(pct_consumo_min, pct_consumo_max)

        # Porciones demandadas
        demanda = int(asistentes * pct_consumo)

        # Quiebre de stock o desperdicio
        diferencia = total_porciones - demanda
        quiebre = max(0, -diferencia)
        desperdicio = max(0, diferencia)

        resultados.append({
            "Iteración": i + 1,
            "Asistentes": asistentes,
            "% Consumo": round(pct_consumo * 100, 1),
            "Demanda (porciones)": demanda,
            "Stock disponible": total_porciones,
            "Quiebre (porciones)": quiebre,
            "Desperdicio (porciones)": desperdicio,
            "Estado": "⚠️ Quiebre" if quiebre > 0 else "✅ OK",
        })

    df = pd.DataFrame(resultados)

    # ─────────────────────────────────────────
    # MÉTRICAS
    # ─────────────────────────────────────────
    iteraciones_quiebre = df[df["Quiebre (porciones)"] > 0]
    prob_quiebre = len(iteraciones_quiebre) / iteraciones * 100

    metricas = {
        "total_porciones": total_porciones,
        "lotes_preparados": lotes_preparados,
        "demanda_promedio": round(df["Demanda (porciones)"].mean(), 1),
        "demanda_minima": int(df["Demanda (porciones)"].min()),
        "demanda_maxima": int(df["Demanda (porciones)"].max()),
        "prob_quiebre": round(prob_quiebre, 1),
        "quiebre_promedio": round(df["Quiebre (porciones)"].mean(), 1),
        "desperdicio_promedio": round(df["Desperdicio (porciones)"].mean(), 1),
        "porciones_recomendadas": int(df["Demanda (porciones)"].quantile(0.90)),
        "lotes_recomendados": int(
            np.ceil(df["Demanda (porciones)"].quantile(0.90) / (budines_por_lote * porciones_por_budin))
        ),
        "recomendacion": _recomendacion_stock(prob_quiebre, lotes_preparados, budines_por_lote, porciones_por_budin),
    }

    return df, metricas


# ─────────────────────────────────────────
# ESCENARIOS
# ─────────────────────────────────────────
def escenarios_stock() -> dict:
    """
    Define los tres escenarios del simulador de stock.
    Modifica parámetros reales del modelo, no son solo etiquetas.
    """
    return {
        "optimista": {
            "nombre": "🟢 Optimista",
            "comensales_esperados": 60,
            "pct_consumo_min": 0.60,
            "pct_consumo_max": 0.75,
            "lotes_preparados": 3,
            "descripcion": "Demanda moderada con preparación estándar. Stock de sobra, sin quiebre.",
        },
        "esperado": {
            "nombre": "🟡 Esperado",
            "comensales_esperados": 60,
            "pct_consumo_min": 0.70,
            "pct_consumo_max": 0.90,
            "lotes_preparados": 3,
            "descripcion": "Demanda probable del evento. Balance entre quiebre y desperdicio.",
        },
        "pesimista": {
            "nombre": "🔴 Pesimista",
            "comensales_esperados": 60,
            "pct_consumo_min": 0.85,
            "pct_consumo_max": 1.0,
            "lotes_preparados": 2,
            "descripcion": "Alta demanda con poca preparación. Riesgo alto de quedarse sin stock.",
        },
    }


# ─────────────────────────────────────────
# VALIDACIÓN POST-EVENTO
# ─────────────────────────────────────────
def validar_con_reales(
    metricas_simuladas: dict,
    porciones_consumidas_reales: int,
    desperdicio_real: int,
) -> pd.DataFrame:
    """
    Compara los resultados simulados con los datos reales del evento.
    """
    comparacion = {
        "Variable": [
            "Demanda promedio (porciones)",
            "Desperdicio (porciones)",
            "Probabilidad de quiebre (%)",
        ],
        "Simulado": [
            metricas_simuladas["demanda_promedio"],
            metricas_simuladas["desperdicio_promedio"],
            metricas_simuladas["prob_quiebre"],
        ],
        "Real": [
            porciones_consumidas_reales,
            desperdicio_real,
            "-",
        ],
    }

    df = pd.DataFrame(comparacion)
    return df


# ─────────────────────────────────────────
# RECOMENDACIÓN AUTOMÁTICA
# ─────────────────────────────────────────
def _recomendacion_stock(
    prob_quiebre: float,
    lotes_preparados: int,
    budines_por_lote: int,
    porciones_por_budin: int = 10,
) -> str:
    ppp = budines_por_lote * porciones_por_budin
    if prob_quiebre > 30:
        return (
            f"Probabilidad de quiebre alta ({prob_quiebre:.1f}%). "
            f"Se recomienda preparar al menos {lotes_preparados + 3} lotes "
            f"({(lotes_preparados + 3) * ppp} porciones)."
        )
    elif prob_quiebre > 10:
        return (
            f"Probabilidad de quiebre moderada ({prob_quiebre:.1f}%). "
            f"Se recomienda preparar {lotes_preparados + 1} lotes como margen de seguridad "
            f"({(lotes_preparados + 1) * ppp} porciones)."
        )
    else:
        return (
            f"Probabilidad de quiebre baja ({prob_quiebre:.1f}%). "
            f"Los {lotes_preparados} lotes planificados "
            f"({lotes_preparados * ppp} porciones) son suficientes."
        )