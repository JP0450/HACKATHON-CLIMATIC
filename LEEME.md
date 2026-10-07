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
│   └── fuentes/                        ← archivos originales de CORNARE (no se modifican,
│                                           salvo la columna "Dimensión (sistema)" del histórico, ver sección 7)
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
6. Antecedentes del Excel histórico — y, para las celdas sin dato actual donde alcance el mínimo de
   registros, el valor que el histórico predijo en lugar del valor fijo (ver sección 7).

Termina con `OK` o con la lista de errores a corregir (valores fuera de 0–1, pesos que no suman 100%, evidencia faltante…).

## 6. Decisión del stress test

En `datos_entrada.xlsx` → hoja **Parametros** → "Decisión del stress test (A / B / C)":
- **A** (por defecto): mantener el portafolio robusto.
- **B**: adoptar el portafolio SSP3-7.0/2060.
- **C**: híbrido (portafolio casi equivalente que incluye una medida que entra en 2060).

Después de cambiar SOLO la decisión A/B/C basta con `python 1_preparar.py` y `python 3_reportes.py`.

**Cualquier otro cambio (presupuesto, datos, pesos, evidencia, parámetros) exige correr los TRES scripts**, incluido `python 2_motor.py`.

## 7. Cómo aporta el histórico cuando falta un dato actual

Cuando una celda de `datos_entrada.xlsx` queda en **NO DISPONIBLE** (nadie la llenó todavía), el sistema
no usa directo el valor fijo de referencia. Primero busca si el Excel histórico
(`datos/fuentes/REPORTE_MEDIDAS_ADAPTACION_MUNICIPIOS.xlsx`) tiene suficientes registros de ese
municipio en esa dimensión. El orden en que decide qué valor usar es siempre:

1. **Dato actual** (oficial, calculado o puesto por el usuario en `datos_entrada.xlsx`) — si existe, se usa tal cual y el histórico no lo toca.
2. **Dato predicho desde el histórico** — solo si no hay dato actual Y el histórico tiene al menos
   el mínimo de registros configurado (parámetro `minimo_registros_historico`, hoja **Parametros**, 3 por defecto).
3. **Valor fijo de referencia** (`valor_vacio_base`, 0,5 por defecto) — solo si no hay dato actual ni histórico suficiente.

Cada vez que se usa el paso 2 o el 3 queda registrado en `salidas/motor/celdas_vacias_usadas.csv`,
columna "regla", para que se pueda auditar de dónde salió cada número.

### Cómo clasificar una fila del histórico para que el sistema la use

Por hoy, el histórico solo trae una amenaza (columna **Vulnerabilidad**) que el sistema traduce
automáticamente a la dimensión **"Riesgo de desastres"** (Inundaciones, Movimiento en masa, Avenidas
torrenciales, Incendios forestales, Vendavales). El resto de registros — todos los que dicen
"No Aplica", o cualquier medida de otra línea de trabajo — no se usan todavía porque no hay forma
automática de saber a cuál de las otras 6 dimensiones pertenecen.

Para que una fila del histórico **sí cuente** en una de esas otras dimensiones, hay que agregarle
el dato que falta: abrir `REPORTE_MEDIDAS_ADAPTACION_MUNICIPIOS.xlsx` y escribir, en la columna
**"Dimensión (sistema)"** (se crea la primera vez que se necesite), el nombre exacto de una de estas
7 dimensiones — deben coincidir letra por letra, incluidas las tildes:

```
Biodiversidad
Recurso hídrico
Seguridad alimentaria
Hábitat
Infraestructura
Riesgo de desastres
Salud
```

Reglas:

| Columna | ¿Qué va? | ¿Obligatoria? |
|---|---|---|
| Municipio | Debe coincidir con Rionegro, Guarne o Marinilla (si es de otro municipio del histórico, se ignora) | Sí (ya viene) |
| Valor Inversion | Número en pesos COP, sin texto ni símbolos | Sí (ya viene) |
| Vulnerabilidad | Se deja igual; el sistema la sigue usando para "Riesgo de desastres" | No se toca |
| **Dimensión (sistema)** | Una de las 7 dimensiones de la lista de arriba, exactamente así escrita. Vacío = la fila no se usa para predecir ningún dato | Solo si se quiere que esa fila cuente en una dimensión distinta a "Riesgo de desastres" |

No hace falta clasificar las 300 filas de una vez: cada fila que se clasifique suma al conteo de esa
dimensión/municipio, y en cuanto una combinación llegue al mínimo de registros, `python 1_preparar.py`
la empieza a usar sola, sin tocar código. Después de editar el Excel histórico hay que volver a correr
los tres scripts (`1_preparar.py`, `2_motor.py`, `3_reportes.py`).
