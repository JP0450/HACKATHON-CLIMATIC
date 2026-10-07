<script setup>
// Vista 2 · Portafolio (Producto 2: portafolio priorizado de adaptación)
import { computed, ref } from "vue";
import { ChevronDown, MapPin, Users } from "lucide-vue-next";
import TextoTrazable from "../components/TextoTrazable.vue";
import { COLOR_TERRITORIO, fmtM } from "../utils.js";

const props = defineProps({ datos: { type: Object, required: true } });
defineEmits(["ir"]);
const abierta = ref(props.datos.portafolio[0]?.alternativa ?? null);
const total = computed(() => props.datos.portafolio.reduce((s, p) => s + p.costo_M, 0));
const P = computed(() => props.datos.kpis.presupuesto_M);
const toggle = (alt) => (abierta.value = abierta.value === alt ? null : alt);
const separa = (txt) => String(txt || "").split(" | ");
const porQue = (txt) => String(txt || "").split(" · ");
</script>

<template>
  <section class="welcome-section compact">
    <div>
      <div class="eyebrow"><span class="eyebrow-line"></span> PRODUCTO 2</div>
      <h1>Portafolio priorizado, <span>en orden de implementación.</span></h1>
      <p class="welcome-copy">{{ datos.portafolio[0]?.regla_de_orden }}</p>
    </div>
  </section>

  <section class="budget-strip panel">
    <div class="budget-row">
      <span>Total asignado</span>
      <strong>{{ fmtM(total) }}</strong>
      <span class="muted">de {{ fmtM(P) }}</span>
      <span class="ok-badge" :class="{ 'bad-badge': total > P }">{{ total <= P ? "✓ dentro del presupuesto" : "✗ excede" }}</span>
    </div>
    <div class="stack-bar">
      <div
        v-for="p in datos.portafolio"
        :key="p.alternativa"
        class="stack-seg"
        :style="{ width: (p.costo_M / P) * 100 + '%', background: COLOR_TERRITORIO[p.territorio] }"
        :title="`${p.orden}. ${p.medida} · ${p.territorio} · ${fmtM(p.costo_M)}`"
      ></div>
    </div>
  </section>

  <section class="portfolio-list">
    <article v-for="p in datos.portafolio" :key="p.alternativa" class="portfolio-card" :class="{ open: abierta === p.alternativa }">
      <button class="portfolio-head" :aria-expanded="abierta === p.alternativa" @click="toggle(p.alternativa)">
        <span class="decision-order big">{{ p.orden }}</span>
        <span class="portfolio-title">
          <strong>{{ p.medida }}</strong>
          <small>{{ p.dimension }} · {{ p.alternativa }}</small>
        </span>
        <span class="territorio-tag" :style="{ '--c': COLOR_TERRITORIO[p.territorio] }">{{ p.territorio }}</span>
        <span class="conf-tag" :class="`conf-${p.confianza.toLowerCase()}`">confianza {{ p.confianza }}</span>
        <span class="decision-cost">{{ fmtM(p.costo_M) }}</span>
        <ChevronDown :size="18" class="chev" />
      </button>

      <div v-if="abierta === p.alternativa" class="portfolio-body">
        <div class="pb-grid">
          <div class="pb-block">
            <h4>Problema que atiende</h4>
            <p><TextoTrazable :texto="p.problema" /></p>
          </div>
          <div class="pb-block two">
            <div>
              <h4>Sensibilidad que reduce</h4>
              <p>{{ p.sensibilidad_que_reduce }}</p>
            </div>
            <div>
              <h4>Capacidad adaptativa que fortalece</h4>
              <p>{{ p.capacidad_que_fortalece }}</p>
            </div>
          </div>
          <div class="pb-block">
            <h4><MapPin :size="14" /> Dónde (según las fuentes)</h4>
            <ul class="plain-list"><li v-for="(l, i) in separa(p.localizacion)" :key="i">{{ l }}</li></ul>
          </div>
          <div class="pb-block">
            <h4><Users :size="14" /> Actores</h4>
            <p><TextoTrazable :texto="p.actores" /></p>
          </div>
          <div class="pb-block highlight">
            <h4>¿Por qué aquí y no en otra parte?</h4>
            <ul class="plain-list"><li v-for="(l, i) in porQue(p.explicacion)" :key="i">{{ l }}</li></ul>
          </div>
          <div class="pb-block">
            <h4>Beneficio esperado</h4>
            <p><TextoTrazable :texto="p.beneficio_esperado" /></p>
          </div>
          <div class="pb-block">
            <h4>Stress test SSP3-7.0 / 2060</h4>
            <p>{{ p.cambio_ssp370_2060 }}</p>
          </div>
          <div class="pb-block two">
            <div>
              <h4>Indicador de actividad</h4>
              <p><TextoTrazable :texto="p.indicador_actividad" /></p>
            </div>
            <div>
              <h4>Indicador de resultado</h4>
              <p><TextoTrazable :texto="p.indicador_resultado" /></p>
            </div>
          </div>
        </div>
      </div>
    </article>
  </section>
</template>
