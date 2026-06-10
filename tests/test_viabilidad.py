import pytest
from simuladores.viabilidad import (
    simular_viabilidad,
    calcular_costo_materia_prima,
    escenarios_viabilidad,
)


PARAMS_BASE = dict(
    lotes_por_dia=10,
    budines_por_lote=2,
    porciones_por_budin=10,
    dias_produccion_mes=22,
    precio_venta=450.0,               # precio por PORCION
    costos_fijos_mensuales=80000.0,
    costo_mano_obra_budin=500.0,
    margen_variacion_costos_pct=15.0,
    aceptacion_sensorial_pct=65.0,
    iteraciones=500,
)


# ── Costo de materia prima ────────────────────────────────────────────────────

def test_costo_mp_es_positivo():
    costo, _ = calcular_costo_materia_prima()
    assert costo > 0

def test_desglose_mp_tiene_10_ingredientes():
    _, desglose = calcular_costo_materia_prima()
    assert len(desglose) == 10

def test_desglose_suma_igual_a_total():
    costo, desglose = calcular_costo_materia_prima()
    assert abs(sum(desglose.values()) - costo) < 0.01

def test_todos_los_ingredientes_tienen_costo_positivo():
    _, desglose = calcular_costo_materia_prima()
    for nombre, valor in desglose.items():
        assert valor > 0, f"Ingrediente '{nombre}' tiene costo 0 o negativo"


# ── Estructura de salida ───────────────────────────────────────────────────────

def test_retorna_dataframe_y_dict():
    import pandas as pd
    df, met = simular_viabilidad(**PARAMS_BASE)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(met, dict)

def test_dataframe_tiene_n_iteraciones():
    df, _ = simular_viabilidad(**PARAMS_BASE)
    assert len(df) == PARAMS_BASE["iteraciones"]

def test_metricas_tienen_claves_esperadas():
    _, met = simular_viabilidad(**PARAMS_BASE)
    claves = {"costo_mp_base", "costo_total_porcion", "ganancia_promedio",
              "prob_viabilidad", "punto_equilibrio_promedio",
              "viabilidad", "recomendacion", "budines_por_mes"}
    assert claves.issubset(set(met.keys()))


# ── Lógica económica ──────────────────────────────────────────────────────────

def test_budines_por_mes_correcto():
    _, met = simular_viabilidad(**PARAMS_BASE)
    esperado = (PARAMS_BASE["lotes_por_dia"]
                * PARAMS_BASE["budines_por_lote"]
                * PARAMS_BASE["dias_produccion_mes"])
    assert met["budines_por_mes"] == esperado

def test_prob_viabilidad_entre_0_y_100():
    _, met = simular_viabilidad(**PARAMS_BASE)
    assert 0 <= met["prob_viabilidad"] <= 100

def test_precio_alto_aumenta_viabilidad():
    _, met_bajo = simular_viabilidad(**{**PARAMS_BASE, "precio_venta": 50.0})
    _, met_alto = simular_viabilidad(**{**PARAMS_BASE, "precio_venta": 2000.0})
    assert met_alto["prob_viabilidad"] >= met_bajo["prob_viabilidad"]

def test_aceptacion_cero_da_ganancia_negativa():
    _, met = simular_viabilidad(**{**PARAMS_BASE, "aceptacion_sensorial_pct": 0.1})
    assert met["ganancia_promedio"] < 0

def test_clasificacion_viabilidad_valida():
    _, met = simular_viabilidad(**PARAMS_BASE)
    assert met["viabilidad"] in ("✅ Viable", "⚠️ Parcialmente viable", "❌ No viable")


# ── Reproducibilidad ──────────────────────────────────────────────────────────

def test_misma_semilla_mismo_resultado():
    _, met1 = simular_viabilidad(**PARAMS_BASE, semilla=42)
    _, met2 = simular_viabilidad(**PARAMS_BASE, semilla=42)
    assert met1["ganancia_promedio"] == met2["ganancia_promedio"]


# ── Escenarios ────────────────────────────────────────────────────────────────

def test_escenarios_retorna_tres_claves():
    esc = escenarios_viabilidad()
    assert set(esc.keys()) == {"optimista", "esperado", "pesimista"}

def test_escenarios_son_ejecutables():
    from datos.parametros import CAPACIDAD, COMERCIAL
    for clave, esc in escenarios_viabilidad().items():
        params = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
        params["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
        params["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
        params["dias_produccion_mes"] = COMERCIAL["dias_produccion_mes"]
        params["costo_mano_obra_hora"] = COMERCIAL["costo_mano_obra_hora"]
        _, met = simular_viabilidad(**params)
        assert 0 <= met["prob_viabilidad"] <= 100, f"Escenario {clave} falló"

def test_optimista_mas_viable_que_pesimista():
    from datos.parametros import CAPACIDAD, COMERCIAL
    resultados = {}
    for clave, esc in escenarios_viabilidad().items():
        params = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
        params["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
        params["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
        params["dias_produccion_mes"] = COMERCIAL["dias_produccion_mes"]
        params["costo_mano_obra_hora"] = COMERCIAL["costo_mano_obra_hora"]
        _, met = simular_viabilidad(**params)
        resultados[clave] = met["prob_viabilidad"]
    assert resultados["optimista"] >= resultados["pesimista"]
