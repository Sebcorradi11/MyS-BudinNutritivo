# Simulador de Producción Masiva
## Budín Nutritivo de Lentejas, Manzana y Zucchini
**Universidad de la Cuenca del Plata · ISI 4to Año · Modelos y Simulación / Ingeniería de Software III · Grupo 3 · 2026**

---

## Descripción del proyecto

Herramienta Streamlit para la evaluación integradora intercátedra entre Ingeniería en Sistemas de Información y Licenciatura en Nutrición.

Producto simulado: Budín Nutritivo de Lentejas, Manzana y Zucchini, elaborado con ingredientes de origen vegetal alineados con el ODS N°2.

Objetivo académico: apoyar la toma de decisiones antes y después del testeo sensorial mediante simulación de eventos discretos, Monte Carlo, análisis de escenarios, análisis de sensibilidad, verificación, validación posterior con datos reales e informe académico automático.

---

## Estructura del proyecto
simulador-budin/
├── app.py                  # Punto de entrada principal de Streamlit
├── requirements.txt        # Dependencias para el deploy
├── CLAUDE.md               # Este archivo
│
├── simuladores/
│   ├── init.py
│   ├── flujo_personas.py   # Simulador 1: eventos discretos
│   ├── stock_porciones.py  # Simulador 2: Monte Carlo stock
│   └── viabilidad.py       # Simulador 3: Monte Carlo económico
│
├── utils/
│   ├── init.py
│   ├── verificacion.py     # Validación de parámetros
│   ├── graficos.py         # Gráficos Plotly reutilizables
│   └── informe.py          # Generación de informe Markdown descargable
│
└── datos/
└── parametros.py       # Valores por defecto del proceso productivo


El claude.md es un archivo que le dice a Claude Code (la IA en la terminal) cómo está estructurado el proyecto, qué hace cada archivo y qué convenciones seguir. Es como un manual interno del proyecto.
markdown# Simulador de Producción Masiva
## Budín Nutritivo de Lentejas, Manzana y Zucchini
**Universidad de la Cuenca del Plata · ISI 4to Año · Modelos y Simulación / Ingeniería de Software III · Grupo 3 · 2026**

---

## Descripción del proyecto

Herramienta Streamlit para la evaluación integradora intercátedra entre Ingeniería en Sistemas de Información y Licenciatura en Nutrición.

Producto simulado: Budín Nutritivo de Lentejas, Manzana y Zucchini, elaborado con ingredientes de origen vegetal alineados con el ODS N°2.

Objetivo académico: apoyar la toma de decisiones antes y después del testeo sensorial mediante simulación de eventos discretos, Monte Carlo, análisis de escenarios, análisis de sensibilidad, verificación, validación posterior con datos reales e informe académico automático.

---

## Estructura del proyecto
simulador-budin/
├── app.py                  # Punto de entrada principal de Streamlit
├── requirements.txt        # Dependencias para el deploy
├── CLAUDE.md               # Este archivo
│
├── simuladores/
│   ├── init.py
│   ├── flujo_personas.py   # Simulador 1: eventos discretos
│   ├── stock_porciones.py  # Simulador 2: Monte Carlo stock
│   └── viabilidad.py       # Simulador 3: Monte Carlo económico
│
├── utils/
│   ├── init.py
│   ├── verificacion.py     # Validación de parámetros
│   ├── graficos.py         # Gráficos Plotly reutilizables
│   └── informe.py          # Generación de informe Markdown descargable
│
└── datos/
└── parametros.py       # Valores por defecto del proceso productivo

---

## Simuladores

### 1. Flujo de personas (`simuladores/flujo_personas.py`)
- **Modelo:** Simulación de eventos discretos
- **Qué simula:** llegada de comensales al stand, tiempo de degustación, tiempo de completar el formulario QR, concurrencia y saturación del sistema
- **Decisión que ayuda a tomar:** si conviene escalonar los ingresos, reforzar la red o preparar respaldo en papel
- **Parámetros clave:** cantidad de comensales, tasa de llegada (λ), tiempo de degustación, tiempo de formulario, capacidad del sistema

### 2. Stock de porciones (`simuladores/stock_porciones.py`)
- **Modelo:** Monte Carlo
- **Qué simula:** demanda variable, asistencia, desperdicio y probabilidad de consumo
- **Decisión que ayuda a tomar:** cuántas porciones preparar para no quedar cortos sin generar desperdicio excesivo
- **Parámetros clave:** asistentes esperados, porcentaje de consumo, budines por lote, tolerancia al desperdicio

### 3. Viabilidad productiva y comercial (`simuladores/viabilidad.py`)
- **Modelo:** Monte Carlo económico
- **Qué simula:** demanda, aceptación sensorial, costos de materia prima, desperdicio, precio de venta y rentabilidad
- **Decisión que ayuda a tomar:** si el producto es viable, parcialmente viable o no viable a escala organizacional
- **Parámetros clave:** costos por ingrediente, precio de venta, margen, costos fijos, lotes por día, aceptación sensorial

---

## Escenarios

Cada simulador incluye tres escenarios que modifican parámetros reales del modelo:

| Escenario | Descripción |
|-----------|-------------|
| 🟢 Optimista | Condiciones ideales: alta asistencia, tiempos bajos, costos estables |
| 🟡 Esperado | Condiciones probables basadas en datos reales del proceso |
| 🔴 Pesimista | Condiciones desfavorables: baja asistencia, tiempos altos, costos elevados |

---

## Verificación

La app verifica antes de ejecutar cada simulación:
- Ausencia de tiempos negativos
- Ausencia de cantidades negativas
- Probabilidades válidas (entre 0 y 1)
- Costos no negativos
- Coherencia entre parámetros (ej: mínimo ≤ máximo)

La lógica de verificación vive en `utils/verificacion.py`.

---

## Validación

Después del evento del 12 de junio se comparan los resultados simulados contra los datos reales:
- Asistentes simulados vs reales
- Tiempos de formulario simulados vs reales
- Porciones consumidas simuladas vs reales
- Desperdicio simulado vs real
- Aceptación sensorial simulada vs real

Con esos datos se recalibran los parámetros y se ejecuta la simulación posterior.

---

## Datos del proceso productivo (`datos/parametros.py`)

### Receta (1 budín)
| Ingrediente | Cantidad |
|-------------|----------|
| Lentejas cocidas | 200g |
| Harina de avena | 50g |
| Zucchini rallado | 120g |
| Manzana rallada | 180g |
| Huevos | 2 unidades |
| Cacao amargo | 15g |
| Miel/azúcar mascabo | 60g |
| Polvo de hornear | 5g |
| Esencia de vainilla | 5ml |
| Aceite vegetal | 30ml |

### Tiempos del proceso
| Etapa | Mínimo | Máximo | Promedio |
|-------|--------|--------|----------|
| Preparación | 10 min | 15 min | 12.5 min |
| Cocción lentejas | 30 min | 35 min | 32.5 min |
| Mezclado | 8 min | 12 min | 10 min |
| Horneado | 30 min | 35 min | 32.5 min (180°C) |
| Enfriado | 20 min | 30 min | 25 min |
| Envasado | 5 min | 8 min | 6.5 min |

### Capacidad productiva
- Budines por lote: 4 unidades
- Hornos disponibles: 1
- Operarios: 2

---

## Convenciones de código

- **Idioma:** español para variables de dominio, inglés para variables técnicas internas
- **Nomenclatura:** snake_case para funciones y variables, UPPER_SNAKE_CASE para constantes
- **Funciones de simulación:** siempre reciben parámetros como argumentos, nunca leen del estado global
- **Gráficos:** siempre generados con Plotly, centralizados en `utils/graficos.py`
- **Verificación:** siempre llamar a `utils/verificacion.py` antes de ejecutar cualquier simulación
- **Semilla aleatoria:** usar `np.random.seed(42)` al inicio de cada simulación para reproducibilidad

---

## Deploy

La app se despliega en Streamlit Cloud:
1. Subir el repositorio a GitHub
2. Conectar en share.streamlit.io
3. Seleccionar `app.py` como archivo principal
4. El deploy es automático en cada push a main

---

## Equipo

| Integrante | Rol | Belbin |
|------------|-----|--------|
| Sebastiano Corradi | Project Manager / QA Lead | Impulsor + Coordinador |
| Carla Marturet Ojeda | Líder técnico / Simulador | Implementador + Especialista