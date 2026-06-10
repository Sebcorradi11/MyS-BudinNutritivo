# utils/verificacion.py
# Validación de parámetros antes de ejecutar cualquier simulación
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────
def verificar_parametros(params: dict) -> tuple[bool, list[str]]:
    """
    Verifica que los parámetros sean válidos antes de simular.
    
    Retorna:
        - True y lista vacía si todo está bien
        - False y lista de errores si hay problemas
    """
    errores = []

    for clave, valor in params.items():
        # Sin valores negativos
        if isinstance(valor, (int, float)) and valor < 0:
            errores.append(f"'{clave}' no puede ser negativo (valor: {valor})")

    return len(errores) == 0, errores


# ─────────────────────────────────────────
# VERIFICACIONES ESPECÍFICAS
# ─────────────────────────────────────────
def verificar_tiempos(t_min: float, t_max: float, nombre: str) -> tuple[bool, str]:
    """
    Verifica que el tiempo mínimo sea menor o igual al máximo.
    """
    if t_min < 0 or t_max < 0:
        return False, f"Los tiempos de '{nombre}' no pueden ser negativos."
    if t_min > t_max:
        return False, f"El tiempo mínimo de '{nombre}' no puede ser mayor al máximo."
    return True, ""


def verificar_probabilidad(valor: float, nombre: str) -> tuple[bool, str]:
    """
    Verifica que un valor sea una probabilidad válida (entre 0 y 1).
    """
    if not (0.0 <= valor <= 1.0):
        return False, f"'{nombre}' debe estar entre 0 y 1 (valor: {valor})"
    return True, ""


def verificar_positivo(valor: float, nombre: str) -> tuple[bool, str]:
    """
    Verifica que un valor sea estrictamente positivo.
    """
    if valor <= 0:
        return False, f"'{nombre}' debe ser mayor a 0 (valor: {valor})"
    return True, ""


def verificar_costos(costos: dict) -> tuple[bool, list[str]]:
    """
    Verifica que todos los costos sean no negativos.
    """
    errores = []
    for nombre, valor in costos.items():
        if valor < 0:
            errores.append(f"El costo '{nombre}' no puede ser negativo (valor: {valor})")
    return len(errores) == 0, errores


# ─────────────────────────────────────────
# MOSTRAR ERRORES EN STREAMLIT
# ─────────────────────────────────────────
def mostrar_errores(errores: list[str]) -> None:
    """
    Muestra los errores de verificación en la interfaz de Streamlit.
    Importar streamlit solo cuando se llama esta función.
    """
    import streamlit as st
    for error in errores:
        st.error(f"⚠️ {error}")