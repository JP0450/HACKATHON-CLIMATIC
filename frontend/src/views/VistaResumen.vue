<script setup>
// Vista 1 · Resumen (Producto 1: tablero de decisión territorial)
import { computed } from "vue";
import { ArrowRight, Coins, Database, Leaf, ListChecks, ShieldCheck } from "lucide-vue-next";
import TextoTrazable from "../components/TextoTrazable.vue";
import { COLOR_TERRITORIO, ETIQUETAS, fmtM, fmtPct } from "../utils.js";

const props = defineProps({ datos: { type: Object, required: true } });
defineEmits(["ir"]);

const k = computed(() => props.datos.kpis);
const reparto = computed(() =>
  Object.entries(k.value.por_territorio_M)
    .map(([t, v]) => ({ t, v, pct: v / k.value.presupuesto_M }))
);
const robustoIgualRef = computed(() => {
  const e = props.datos.escenarios;
  return [...e.robusto].sort().join() === [...e.referencia].sort().join();
});
</script>

<template>
  <section class="welcome-section">
    <div>
      <div class="eyebrow"><span class="eyebrow-line"></span> RETO CORNARE · CLIMATE RISK HACKATHON</div>
      <h1>Dónde y cómo intervenir, <span>con $5.000 millones.</span></h1>
      <p class="welcome-copy">
        Portafolio de adaptación para Rionegro, Guarne y Marinilla: priorizado con datos de CORNARE,
        optimizado bajo el presupuesto y probado frente a SSP3-7.0/2060 y frente a los datos que faltan.
      </p>
    </div>
  </section>

  <section class="metrics-grid" aria-label="Indicadores del portafolio">
    <article class="metric-card">
      <div class="metric-topline"><span>Presupuesto asignado</span><span class="metric-icon"><Coins :size="18" /></span></div>
      <div class="metric-value">{{ fmtM(k.asignado_M) }}</div>
      <div class="metric-foot"><span class="metric-context">de {{ fmtM(k.presupuesto_M) }} · saldo {{ fmtM(k.saldo_M) }}</span></div>
    </article>
    <article class="metric-card">
      <div class="metric-topline"><span>Intervenciones</span><span class="metric-icon"><ListChecks :size="18" /></span></div>
      <div class="metric-value">{{ k.n_intervenciones }}<small>medidas</small></div>
      <div class="metric-foot"><span class="metric-context">medidas indivisibles del catálogo del reto</span></div>
    </article>
    <article class="metric-card">
      <div class="metric-topline"><span>Datos V/CA disponibles</span><span class="metric-icon"><Database :size="18" /></span></div>
      <div class="metric-value">{{ fmtPct(k.cobertura_datos_VCA) }}</div>
      <div class="metric-foot"><span class="metric-context">el resto se prueba de 0 a 1 en {{ datos.meta.n_simulaciones.toLocaleString("es-CO") }} escenarios</span></div>
    </article>
    <article class="metric-card">
      <div class="metric-topline"><span>Stress test SSP3-7.0 / 2060</span><span class="metric-icon"><ShieldCheck :size="18" /></span></div>
      <div class="metric-value metric-value-text">{{ k.veredicto_2060.toLowerCase() }}</div>
      <div class="metric-foot">
        <span class="metric-context">{{ robustoIgualRef ? "la decisión robusta (hoy + 2060) coincide con la de hoy" : "la decisión robusta difiere de la de hoy" }}</span>
      </div>
    </article>
  </section>

  <section class="insights-grid">
    <article class="chart-card">
      <div class="card-heading">
        <div>
          <div class="section-kicker">DECISIÓN RECOMENDADA</div>
          <h2>Portafolio de adaptación</h2>
        </div>
        <button class="period-select" @click="$emit('ir', 'Portafolio')">Ver detalle <ArrowRight :size="14" /></button>
      </div>
      <ol class="decision-list">
        <li v-for="p in datos.portafolio" :key="p.alternativa">
          <span class="decision-order">{{ p.orden }}</span>
          <span class="decision-name">{{ p.medida }}</span>
          <span class="territorio-tag" :style="{ '--c': COLOR_TERRITORIO[p.territorio] }">{{ p.territorio }}</span>
          <span class="decision-cost">{{ fmtM(p.costo_M) }}</span>
        </li>
      </ol>

      <div class="section-kicker reparto-title">REPARTO DEL FONDO POR TERRITORIO</div>
      <div class="stack-bar" role="img" aria-label="Reparto del presupuesto por territorio">
        <div
          v-for="r in reparto.filter((x) => x.v > 0)"
          :key="r.t"
          class="stack-seg"
          :style="{ width: r.pct * 100 + '%', background: COLOR_TERRITORIO[r.t] }"
          :title="`${r.t}: ${fmtM(r.v)} (${fmtPct(r.pct)})`"
        ></div>
      </div>
      <ul class="stack-legend">
        <li v-for="r in reparto" :key="r.t">
          <i :style="{ background: COLOR_TERRITORIO[r.t] }"></i>
          <span>{{ r.t }}</span><strong>{{ fmtM(r.v) }}</strong><small>{{ fmtPct(r.pct) }}</small>
        </li>
      </ul>
      <p class="fine-print">“Corredor” = medidas que benefician a los tres municipios (áreas protegidas, conocimiento del riesgo).</p>
    </article>

    <article class="insight-card">
      <div class="insight-orbit orbit-one"></div>
      <div class="insight-orbit orbit-two"></div>
      <div class="insight-content">
        <div class="insight-badge"><Leaf :size="15" /> QUÉ PROTEGER PRIMERO</div>
        <h2>{{ datos.hallazgos[0]?.hallazgo }}</h2>
        <p>{{ datos.hallazgos[0]?.implicacion }}</p>
        <a href="#" class="insight-link" @click.prevent="$emit('ir', 'Datos y vacíos')">Ver datos y vacíos <ArrowRight :size="15" /></a>
      </div>
    </article>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">DIAGNÓSTICO DE DECISIÓN</div>
        <h2>Hallazgos (máximo 5)</h2>
      </div>
    </div>
    <ol class="hallazgos">
      <li v-for="(h, i) in datos.hallazgos" :key="i">
        <span class="hallazgo-n">{{ i + 1 }}</span>
        <div>
          <p class="hallazgo-txt">{{ h.hallazgo }}</p>
          <p class="hallazgo-imp"><ArrowRight :size="13" /> {{ h.implicacion }}</p>
          <p class="hallazgo-src"><TextoTrazable :texto="'Fuente: ' + h.fuente" /></p>
        </div>
      </li>
    </ol>
  </section>

  <section class="bottom-banner leyenda">
    <strong>Cómo leer las etiquetas:</strong>
    <span v-for="(desc, tag) in ETIQUETAS" :key="tag" class="leyenda-item">
      <TextoTrazable :texto="`[${tag}]`" /> <small>{{ desc }}</small>
    </span>
  </section>
</template>
