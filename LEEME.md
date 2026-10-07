# Motor de decisión de adaptación — CORNARE (Rionegro · Guarne · Marinilla)

## 1. Instalar (una sola vez)

Necesitan Python 3.10 o superior. En la terminal del IDE, dentro de esta carpeta:

```
pip install pandas numpy openpyxl
```

## 2. Ejecutar

```
python 1_preparar.py      # Paso 2: valida y ordena los datos  (listo)
python 2_motor.py         # Paso 3: puntaje + optimización $5.000 M + stress test + simulación  (listo, ~40 s)
python 3_reportes.py      # Paso 5: portafolio final, riesgo residual, MEA, brechas, JSON para Vue y Excel  (listo)
```

Si `python` no funciona, prueben con `python3` (Mac/Linux) o `py` (Windows).

## 3. Qué editar

Solo se edita **`datos/datos_entrada.xlsx`**:

| Color | Significado | ¿Se edita? |
|---|---|---|
| Verde | Dato oficial de CORNARE (la fuente está en el comentario de la celda) | No |
| Naranja | Calculado o supuesto del equipo | Solo si el equipo decide cambiarlo |
| Amarillo vacío | Dato NO DISPONIBLE: entrada para el usuario | Sí: escriba un valor entre 0 y 1 y anote la fuente en la columna "Fuente…" |
| Texto azul | Pesos y parámetros | Sí |

Después de editar: guardar el Excel y volver a ejecutar `python 1_preparar.py`.

> No sobrescriba celdas verdes: conservan la etiqueta [OFICIAL] de su comentario.

## 4. Estructura

```
modelo_cornare/
├── datos/
│   ├── datos_entrada.xlsx              ← lo único que se edita
│   └── fuentes/                        ← archivos originales de CORNARE (no se modifican)
├── 1_preparar.py                       ← ingesta, calidad, matriz de riesgo, catálogo de medidas
├── 2_motor.py                          ← priorización, mochila, stress test, simulación, regret, valor de la información
├── salidas/preparado/                  ← lo genera 1_preparar.py (no editar a mano)
├── 3_reportes.py                       ← productos 2 y 3, resultados.json (para el frontend Vue) y reporte_completo.xlsx
├── salidas/motor/                      ← lo genera 2_motor.py: alternativas, portafolio, regret, contrafactuales
├── salidas/reportes/                   ← lo genera 3_reportes.py
└── LEEME.md
```

## 5. Qué muestra `1_preparar.py`

1. Cuántos datos hay de cada tipo (OFICIAL / CALCULADO / USUARIO / NO DISPONIBLE) por componente.
2. La lista de valores existentes.
3. Medidas y evidencia.
4. Pesos de referencia y del stress test SSP3-7.0/2060 (robustez 25%, los demás bajan en proporción).
5. Parámetros.
6. Antecedentes del Excel histórico (solo contexto: no entran al puntaje).

Termina con `OK` o con la lista de errores a corregir (valores fuera de 0–1, pesos que no suman 100%, evidencia faltante…).

## 6. Decisión del stress test

En `datos_entrada.xlsx` → hoja **Parametros** → "Decisión del stress test (A / B / C)":
- **A** (por defecto): mantener el portafolio robusto.
- **B**: adoptar el portafolio SSP3-7.0/2060.
- **C**: híbrido (portafolio casi equivalente que incluye una medida que entra en 2060).

Después de cambiar SOLO la decisión A/B/C basta con `python 1_preparar.py` y `python 3_reportes.py`.

**Cualquier otro cambio (presupuesto, datos, pesos, evidencia, parámetros) exige correr los TRES scripts**, incluido `python 2_motor.py`.
