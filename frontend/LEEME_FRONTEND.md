# Tablero de decisión (Vue 3 + Vite)

El tablero **no calcula nada**: solo muestra `public/resultados.json`, que genera `python 3_reportes.py`
(el script lo copia aquí automáticamente). No necesita backend.

## Ejecutar

```
cd frontend
npm install        # una sola vez
npm run dev        # abre http://localhost:5173
```

Si se cambian datos o pesos: volver a correr `1_preparar.py`, `2_motor.py` y `3_reportes.py`, y recargar la página.

## Estructura

```
src/
├── App.vue                    barra lateral + carga de resultados.json
├── utils.js                   formatos, colores por territorio, etiquetas de trazabilidad
├── components/TextoTrazable.vue  convierte [OFICIAL], [SUPUESTO]… en chips
└── views/
    ├── VistaResumen.vue       Producto 1: indicadores, decisión, reparto, 5 hallazgos
    ├── VistaPortafolio.vue    Producto 2: las medidas con problema, dónde, actores, por qué, 2060, indicadores
    ├── VistaDatos.vue         Productos 1 y 3: ficha 21×6 y datos faltantes que cambian la decisión
    ├── VistaRobustez.vue      Producto 2: estabilidad, stress test, contrafactuales, arrepentimiento
    └── VistaResidual.vue      Producto 3: riesgo residual, seguimiento MEA, brechas
```

## Para presentar sin internet

`npm run build` genera `dist/`. Se puede abrir con `npm run preview`.
