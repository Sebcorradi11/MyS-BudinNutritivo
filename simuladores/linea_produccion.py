# simuladores/linea_produccion.py
# Simulador de línea de producción con eventos discretos
# Modela horno y operarios como recursos compartidos entre lotes
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

import numpy as np
import pandas as pd
from datos.parametros import TIEMPOS, CAPACIDAD, SEMILLA


ETAPAS_DEF = [
    ("Preparación",      "preparacion_min",      "preparacion_max",      "operario"),
    ("Cocción lentejas", "coccion_lentejas_min",  "coccion_lentejas_max", None),
    ("Mezclado",         "mezclado_min",          "mezclado_max",         None),
    ("Horneado",         "horneado_min",           "horneado_max",         "horno"),
    ("Enfriado",         "enfriado_min",           "enfriado_max",         None),
    ("Envasado",         "envasado_min",           "envasado_max",         None),
]


def simular_linea_produccion(
    lotes_a_producir: int,
    hornos_disponibles: int = None,
    operarios: int = None,
    semilla: int = SEMILLA,
) -> tuple[pd.DataFrame, dict]:
    """
    Simula la línea de producción usando eventos discretos.

    Recursos modelados:
    - Operarios: controlan cuándo puede empezar la preparación de un nuevo lote.
      Con 2 operarios, dos lotes pueden arrancar prep en paralelo.
    - Hornos: recurso compartido para la etapa de horneado.
      Con 1 horno, los lotes hacen cola; con 2, pueden hornear en paralelo.

    Las etapas pasivas (Cocción lentejas, Enfriado) no consumen recursos —
    el lote espera solo el tiempo de la etapa antes de continuar.

    Retorna:
        - df: una fila por (lote, etapa) con Inicio, Fin, Duración y Espera
        - metricas: indicadores de la línea (makespan, throughput, bottleneck, etc.)
    """
    np.random.seed(semilla)

    hornos_disponibles = hornos_disponibles or CAPACIDAD["hornos_disponibles"]
    operarios = operarios or CAPACIDAD["operarios"]

    # Recursos: cada elemento es el momento en que queda libre
    horno_libre = [0.0] * hornos_disponibles
    operario_libre = [0.0] * operarios

    registros = []

    for i in range(lotes_a_producir):
        # El lote empieza cuando un operario termine la preparación anterior.
        # Mezclado y Envasado son manejados por el equipo sin bloquear el arranque
        # del siguiente lote — el cuello de botella real es el horno.
        op_idx = int(np.argmin(operario_libre))
        t = operario_libre[op_idx]

        for nombre, k_min, k_max, recurso in ETAPAS_DEF:
            dur = round(np.random.uniform(TIEMPOS[k_min], TIEMPOS[k_max]), 1)

            if recurso == "operario":
                # Solo la Preparación ocupa el operario (determina el stagger entre lotes)
                t_inicio = t
                operario_libre[op_idx] = t_inicio + dur

            elif recurso == "horno":
                h_idx = int(np.argmin(horno_libre))
                t_inicio = max(t, horno_libre[h_idx])
                horno_libre[h_idx] = t_inicio + dur

            else:
                t_inicio = t

            espera = round(max(0.0, t_inicio - t), 1)

            registros.append({
                "Lote": f"Lote {i + 1}",
                "Etapa": nombre,
                "Inicio": round(t_inicio, 1),
                "Fin": round(t_inicio + dur, 1),
                "Duración": dur,
                "Espera horno (min)": espera if nombre == "Horneado" else 0.0,
                "Recurso": recurso or "—",
            })

            t = t_inicio + dur

    df = pd.DataFrame(registros)

    makespan = df["Fin"].max()
    total_espera_horno = df["Espera horno (min)"].sum()
    espera_prom_horno = round(df[df["Etapa"] == "Horneado"]["Espera horno (min)"].mean(), 1)

    tiempo_activo_hornos = df[df["Etapa"] == "Horneado"]["Duración"].sum()
    utilizacion_horno = round(
        tiempo_activo_hornos / (hornos_disponibles * makespan) * 100, 1
    ) if makespan > 0 else 0.0

    # Cuello de botella: la etapa que más esperas acumula
    espera_por_etapa = df.groupby("Etapa")["Espera horno (min)"].sum()
    if espera_por_etapa.max() > 0:
        bottleneck = espera_por_etapa.idxmax()
    else:
        bottleneck = "Sin cola"

    metricas = {
        "makespan_min": round(makespan, 1),
        "makespan_hs": round(makespan / 60, 2),
        "lotes_completados": lotes_a_producir,
        "budines_producidos": lotes_a_producir * CAPACIDAD["budines_por_lote"],
        "porciones_producidas": lotes_a_producir * CAPACIDAD["budines_por_lote"] * CAPACIDAD["porciones_por_budin"],
        "throughput_lotes_hora": round(lotes_a_producir / (makespan / 60), 2) if makespan > 0 else 0.0,
        "bottleneck": bottleneck,
        "espera_prom_horno_min": espera_prom_horno,
        "total_espera_horno_min": round(total_espera_horno, 1),
        "utilizacion_horno_pct": utilizacion_horno,
    }

    return df, metricas


def estado_en_tiempo(df: pd.DataFrame, t: float) -> dict:
    """
    Para un instante t, retorna qué etapa está haciendo cada lote.
    "Cola horneado": lote terminó Mezclado pero el horno aún no está libre.
    """
    etapas = ["Preparación", "Cocción lentejas", "Mezclado", "Horneado", "Enfriado", "Envasado"]
    result = {e: [] for e in etapas}
    result["Cola horneado"] = []
    result["No iniciado"] = []
    result["Completado"] = []

    for lote in sorted(df["Lote"].unique(), key=lambda x: int(x.split()[1])):
        lote_df = df[df["Lote"] == lote].set_index("Etapa")
        num = lote.split()[1]

        primer_inicio = lote_df["Inicio"].min()
        ultimo_fin = lote_df["Fin"].max()

        if t < primer_inicio:
            result["No iniciado"].append(num)
        elif t >= ultimo_fin:
            result["Completado"].append(num)
        else:
            # Buscar la etapa activa en t
            lote_raw = df[df["Lote"] == lote]
            activa = lote_raw[(lote_raw["Inicio"] <= t) & (lote_raw["Fin"] > t)]
            if len(activa) > 0:
                result[activa.iloc[0]["Etapa"]].append(num)
            else:
                # Entre dos etapas — determinar cuál es la "transición"
                mez_fin = lote_df.loc["Mezclado", "Fin"] if "Mezclado" in lote_df.index else None
                horn_ini = lote_df.loc["Horneado", "Inicio"] if "Horneado" in lote_df.index else None
                if mez_fin is not None and horn_ini is not None and mez_fin <= t < horn_ini:
                    result["Cola horneado"].append(num)
                else:
                    # Transición entre otras etapas: mostrar en la última completada
                    pasadas = lote_raw[lote_raw["Fin"] <= t]
                    if len(pasadas) > 0:
                        result[pasadas.iloc[-1]["Etapa"]].append(num)

    return result
