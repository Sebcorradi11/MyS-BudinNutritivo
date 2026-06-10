# simuladores/flujo_personas.py
# Simulador 1: Flujo de personas y formulario digital
# Modelo: Simulación de eventos discretos
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

import numpy as np
import pandas as pd
from datos.parametros import EVENTO, SEMILLA

# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────
def simular_flujo(
    comensales: int,
    tasa_llegada_min: float,
    tasa_llegada_max: float,
    t_degustacion_min: float,
    t_degustacion_max: float,
    t_formulario_min: float,
    t_formulario_max: float,
    capacidad_sistema: int,
    semilla: int = SEMILLA,
) -> tuple[pd.DataFrame, dict]:
    """
    Simula el flujo de personas durante el evento de degustación.

    Modelo: simulación de eventos discretos.
    Cada comensal es una entidad que pasa por tres etapas:
        1. Llegada al stand
        2. Degustación del budín
        3. Completar y enviar el formulario QR

    Retorna:
        - df: DataFrame con el detalle de cada comensal
        - metricas: dict con los indicadores principales
    """
    np.random.seed(semilla)

    eventos = []
    tiempo_actual = 0
    sistema_ocupado = 0  # personas actualmente en el sistema

    for i in range(comensales):

        # Tiempo entre llegadas (distribución uniforme)
        intervalo_llegada = np.random.uniform(
            60 / tasa_llegada_max,  # intervalo mínimo
            60 / tasa_llegada_min,  # intervalo máximo
        )
        tiempo_llegada = tiempo_actual + intervalo_llegada
        tiempo_actual = tiempo_llegada

        # Espera si el sistema está en capacidad máxima
        espera = 0
        if sistema_ocupado >= capacidad_sistema:
            espera = np.random.uniform(1, 3)

        # Degustación
        t_degust = np.random.uniform(t_degustacion_min, t_degustacion_max)

        # Formulario QR
        t_form = np.random.uniform(t_formulario_min, t_formulario_max)

        # Tiempo total en el sistema
        t_total = espera + t_degust + t_form

        # Fin del proceso
        tiempo_salida = tiempo_llegada + t_total

        sistema_ocupado = max(0, sistema_ocupado - 1)

        eventos.append({
            "Comensal": i + 1,
            "Llegada (min)": round(tiempo_llegada, 2),
            "Espera (min)": round(espera, 2),
            "Degustación (min)": round(t_degust, 2),
            "Formulario (min)": round(t_form, 2),
            "Tiempo total (min)": round(t_total, 2),
            "Salida (min)": round(tiempo_salida, 2),
            "Saturación": "⚠️ Sí" if espera > 0 else "✅ No",
        })

    df = pd.DataFrame(eventos)

    # ─────────────────────────────────────────
    # MÉTRICAS
    # ─────────────────────────────────────────
    saturados = df[df["Espera (min)"] > 0]

    metricas = {
        "comensales": comensales,
        "tiempo_total_evento": round(df["Salida (min)"].max(), 1),
        "tiempo_promedio_sistema": round(df["Tiempo total (min)"].mean(), 1),
        "tiempo_promedio_degustacion": round(df["Degustación (min)"].mean(), 1),
        "tiempo_promedio_formulario": round(df["Formulario (min)"].mean(), 1),
        "espera_promedio": round(df["Espera (min)"].mean(), 2),
        "comensales_con_espera": len(saturados),
        "pct_saturacion": round(len(saturados) / comensales * 100, 1),
        "saturacion": "Alta" if len(saturados) / comensales > 0.3 else
                      "Media" if len(saturados) / comensales > 0.1 else "Baja",
        "recomendacion": _recomendacion(len(saturados) / comensales),
    }

    return df, metricas


# ─────────────────────────────────────────
# ESCENARIOS
# ─────────────────────────────────────────
def escenarios_flujo() -> dict:
    """
    Define los tres escenarios del simulador de flujo.
    Modifica parámetros reales del modelo, no son solo etiquetas.
    """
    return {
        "optimista": {
            "nombre": "🟢 Optimista",
            "comensales": 60,
            "tasa_llegada_min": 2,
            "tasa_llegada_max": 4,
            "t_degustacion_min": 2,
            "t_degustacion_max": 4,
            "t_formulario_min": 1,
            "t_formulario_max": 3,
            "capacidad_sistema": 20,
            "descripcion": "Alta llegada, tiempos cortos, sistema holgado.",
        },
        "esperado": {
            "nombre": "🟡 Esperado",
            "comensales": 60,
            "tasa_llegada_min": 1,
            "tasa_llegada_max": 3,
            "t_degustacion_min": 3,
            "t_degustacion_max": 7,
            "t_formulario_min": 2,
            "t_formulario_max": 5,
            "capacidad_sistema": 15,
            "descripcion": "Condiciones probables basadas en el evento real.",
        },
        "pesimista": {
            "nombre": "🔴 Pesimista",
            "comensales": 60,
            "tasa_llegada_min": 3,
            "tasa_llegada_max": 6,
            "t_degustacion_min": 5,
            "t_degustacion_max": 10,
            "t_formulario_min": 4,
            "t_formulario_max": 8,
            "capacidad_sistema": 10,
            "descripcion": "Llegada masiva, tiempos largos, sistema saturado.",
        },
    }


# ─────────────────────────────────────────
# VALIDACIÓN POST-EVENTO
# ─────────────────────────────────────────
def validar_con_reales(
    metricas_simuladas: dict,
    asistentes_reales: int,
    tiempo_formulario_real: float,
    picos_carga_reales: int,
) -> pd.DataFrame:
    """
    Compara los resultados simulados con los datos reales del evento.
    Retorna un DataFrame con la comparación para mostrar en la app.
    """
    comparacion = {
        "Variable": [
            "Asistentes",
            "Tiempo promedio formulario (min)",
            "Comensales con espera",
        ],
        "Simulado": [
            metricas_simuladas["comensales"],
            metricas_simuladas["tiempo_promedio_formulario"],
            metricas_simuladas["comensales_con_espera"],
        ],
        "Real": [
            asistentes_reales,
            tiempo_formulario_real,
            picos_carga_reales,
        ],
    }

    df = pd.DataFrame(comparacion)
    df["Diferencia (%)"] = (
        abs(df["Simulado"] - df["Real"]) / df["Real"] * 100
    ).round(1)

    return df


# ─────────────────────────────────────────
# RECOMENDACIÓN AUTOMÁTICA
# ─────────────────────────────────────────
def _recomendacion(pct_saturacion: float) -> str:
    if pct_saturacion > 0.3:
        return (
            "Se detecta saturación alta. Se recomienda escalonar "
            "el ingreso de comensales en grupos de 10-15 personas "
            "o preparar formularios en papel como respaldo."
        )
    elif pct_saturacion > 0.1:
        return (
            "Se detecta saturación moderada. Se recomienda monitorear "
            "el flujo durante el evento y estar preparados para escalonar "
            "si los tiempos de espera aumentan."
        )
    else:
        return (
            "El sistema opera con baja saturación. "
            "No se requieren medidas adicionales para el flujo de personas."
        )