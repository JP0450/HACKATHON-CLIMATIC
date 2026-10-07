<script setup>
// Vista 4 · Robustez: estabilidad de cada medida, stress test SSP3-7.0/2060, contrafactuales y arrepentimiento
import { computed, ref } from "vue";
import { fmtM, fmtNum, fmtPct } from "../utils.js";

const props = defineProps({ datos: { type: Object, required: true } });
defineEmits(["ir"]);
const hover = ref(null);

const nombre = computed(() => Object.fromEntries(props.datos.medidas.map((m) => [m.ID, m.Medida])));
const nombreAlt = computed(() => Object.fromEntries(props.datos.alternativas.map((a) => [a.alternativa, `${a.medida} · ${a.territorio}`])));
const enPortafolio = computed(() => new Set(props.datos.portafolio.map((p) => p.id)));

const frecuencias = computed(() =>
  Object.entries(props.datos.frecuencia_por_medida)
    .map(([id, f]) => ({ id, f, nombre: nombre.value[id] ?? id, sel: enPortafolio.value.has(id),
      etiqueta: f >= 0.6 ? "estable" : f >= 0.2 ? "sensible" : f > 0 ? "marginal" : "nunca" }))
    .sort((a, b) => b.f - a.f)
);

const esc = computed(() => props.datos.escenarios);
const columnas = computed(() => [
  { t: "Hoy (referencia)", lista: esc.value.referencia },
  { t: "SSP3-7.0 / 2060", lista: esc.value.stress_2060 },
  { t: "Robusto (hoy + 2060 + datos faltantes)", lista: esc.value.robusto },
]);
const todas = computed(() => [...new Set(columnas.value.flatMap((c) => c.lista))].sort());
const limite = computed(() => {
  const cambio = esc.value.aguante_robustez.find((x) => !x.igual_a_referencia);
  return cambio ? cambio.peso_robustez : null;
});
const pesoStress = computed(() => props.datos.pesos.find((p) => p.criterio === "Robustez 2060")?.stress_ssp370_2060);
</script>

<template>
  <section class="welcome-section compact">
    <div>
      <div class="eyebrow"><span class="eyebrow-line"></span> PRODUCTO 2 · ROBUSTEZ</div>
      <h1>¿Aguanta la decisión <span>si cambian los supuestos?</span></h1>
      <p class="welcome-copy">
        {{ datos.meta.n_simulaciones.toLocaleString("es-CO") }} escenarios: los datos faltantes, los pesos y la efectividad de las medidas varían al azar.
      </p>
    </div>
  </section>

  <section class="insights-grid">
    <article class="chart-card">
      <div class="card-heading">
        <div>
          <div class="section-kicker">ESTABILIDAD</div>
          <h2>¿En cuántos escenarios sale cada medida?</h2>
        </div>
      </div>
      <div class="hbar-list" role="img" aria-label="Frecuencia de selección de cada medida en los escenarios simulados">
        <div
          v-for="r in frecuencias"
          :key="r.id"
          class="hbar-row"
          :class="{ dim: hover && hover !== r.id }"
          @mouseenter="hover = r.id"
          @mouseleave="hover = null"
        >
          <span class="hbar-label" :title="r.nombre">
            <b v-if="r.sel" class="sel-dot" title="En el portafolio recomendado">●</b>{{ r.nombre }}
          </span>
          <span class="hbar-track"><span class="hbar" :style="{ width: Math.max(r.f * 100, 0.5) + '%' }"></span></span>
          <span class="hbar-val">{{ fmtPct(r.f) }} <small>{{ r.etiqueta }}</small></span>
          <span v-if="hover === r.id" class="hbar-tip">{{ r.nombre }}: sale en el {{ fmtPct(r.f, 1) }} de los escenarios ({{ r.etiqueta }}){{ r.sel ? " · está en el portafolio" : "" }}</span>
        </div>
      </div>
      <p class="fine-print">● = en el portafolio recomendado. Estable ≥ 60% · sensible 20–60% · marginal &lt; 20%.</p>
    </article>

    <article class="chart-card">
      <div class="card-heading">
        <div>
          <div class="section-kicker">STRESS TEST</div>
          <h2>Hoy vs SSP3-7.0 / 2060</h2>
        </div>
      </div>
      <p class="verdict">Veredicto: <strong>{{ datos.kpis.veredicto_2060 }}</strong></p>
      <p class="muted small">
        Con robustez al {{ fmtPct(pesoStress) }}: entra {{ esc.entra_2060.join(", ") || "—" }} · sale {{ esc.sale_2060.join(", ") || "—" }}.
        <template v-if="limite != null"> La decisión de hoy se mantiene hasta un peso de robustez de {{ fmtPct(limite - 0.05) }}.</template>
      </p>
      <div class="table-wrap">
        <table class="data-table compare">
          <thead><tr><th>Alternativa</th><th v-for="c in columnas" :key="c.t">{{ c.t }}</th></tr></thead>
          <tbody>
            <tr v-for="a in todas" :key="a">
              <td :title="nombreAlt[a]"><span class="mono">{{ a }}</span> <small class="muted">{{ nombreAlt[a] }}</small></td>
              <td v-for="c in columnas" :key="c.t" class="center">{{ c.lista.includes(a) ? "✓" : "" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="fine-print">Solo 1 de 21 celdas 2060 tiene dato oficial: parte del cambio refleja la falta de datos futuros, no información nueva.</p>
    </article>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">CONTRAFACTUALES</div>
        <h2>¿Y si…?</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Caso</th><th>Portafolio resultante</th><th class="num">Medidas</th><th class="num">Costo</th><th>Nota</th></tr></thead>
        <tbody>
          <tr v-for="c in datos.contrafactuales" :key="c.caso">
            <td><strong>{{ c.caso }}</strong></td>
            <td class="mono">{{ c.portafolio }}</td>
            <td class="num">{{ c.n }}</td>
            <td class="num">{{ fmtM(c.costo) }}</td>
            <td class="muted small">{{ c.nota || "" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">MÍNIMO ARREPENTIMIENTO</div>
        <h2>¿Por qué esta combinación y no otra?</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>Portafolio</th><th class="num">Pérdida típica</th><th class="num">Pérdida en el peor 10%</th><th class="num">Casi óptimo en</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in datos.regret_top.slice(0, 6)" :key="r.portafolio"
              :class="{ chosen: [...r.portafolio.split(' + ')].sort().join() === [...esc.robusto].sort().join() }">
            <td class="mono">{{ r.portafolio }}</td>
            <td class="num">{{ fmtPct(r.regret_medio, 1) }}</td>
            <td class="num">{{ fmtPct(r.regret_p90, 1) }}</td>
            <td class="num">{{ fmtPct(r.pct_casi_optimo) }} de escenarios</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine-print">
      Pérdida = cuánto beneficio se deja de ganar frente a la mejor canasta de cada escenario. Portafolios a ≤ 1 punto del mejor se
      consideran equivalentes; entre ellos decide la regla de desempate (amenaza oficial registrada). Fila resaltada = elegido.
    </p>
  </section>
</template>
