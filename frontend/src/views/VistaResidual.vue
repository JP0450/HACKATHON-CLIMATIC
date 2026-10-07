<script setup>
// Vista 5 · Riesgo residual, seguimiento MEA y brechas de información (Producto 3)
import { computed, ref } from "vue";
import TextoTrazable from "../components/TextoTrazable.vue";
import { DIMENSIONES, MUNICIPIOS, PRIORIDAD } from "../utils.js";

const props = defineProps({ datos: { type: Object, required: true } });
defineEmits(["ir"]);
const sel = ref(null);

const mapa = computed(() => {
  const m = {};
  for (const r of props.datos.riesgo_residual) m[`${r.municipio}|${r.dimension}`] = r;
  return m;
});
const conteo = computed(() => {
  const c = {};
  for (const r of props.datos.riesgo_residual) c[r.prioridad_residual] = (c[r.prioridad_residual] || 0) + 1;
  return c;
});
const detalle = computed(() => (sel.value ? mapa.value[sel.value] : null));
const corto = (p) => (p === "SIN PROBLEMA DOCUMENTADO" ? "SIN DATO" : p);
const brechasDecision = computed(() => props.datos.brechas.filter((b) => b.tipo === "Dato que cambia la decisión"));
const brechasOtras = computed(() => props.datos.brechas.filter((b) => b.tipo !== "Dato que cambia la decisión"));
</script>

<template>
  <section class="welcome-section compact">
    <div>
      <div class="eyebrow"><span class="eyebrow-line"></span> PRODUCTO 3</div>
      <h1>Lo que queda sin resolver, <span>y cómo sabremos si funcionó.</span></h1>
      <p class="welcome-copy">
        La inversión no elimina el riesgo. La reducción no es cuantificable con los datos disponibles (efectividad NO DISPONIBLE),
        así que el residual se expresa por cobertura de las medidas y por problemas documentados sin atender.
      </p>
    </div>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">RIESGO RESIDUAL · MUNICIPIO × DIMENSIÓN</div>
        <h2>Prioridad residual tras invertir el fondo</h2>
      </div>
      <div class="count-pills">
        <span v-for="(v, k) in conteo" :key="k" class="pill prio-pill" :style="{ '--c': PRIORIDAD[k]?.color }">
          {{ PRIORIDAD[k]?.icono }} {{ corto(k) }} {{ v }}
        </span>
      </div>
    </div>

    <div class="table-wrap">
      <table class="residual-grid">
        <thead><tr><th></th><th v-for="d in DIMENSIONES" :key="d">{{ d }}</th></tr></thead>
        <tbody>
          <tr v-for="m in MUNICIPIOS" :key="m">
            <th>{{ m }}</th>
            <td v-for="d in DIMENSIONES" :key="d">
              <button
                class="res-cell"
                :class="{ active: sel === `${m}|${d}` }"
                :style="{ '--c': PRIORIDAD[mapa[`${m}|${d}`]?.prioridad_residual]?.color }"
                :title="mapa[`${m}|${d}`]?.estado_intervencion"
                @click="sel = sel === `${m}|${d}` ? null : `${m}|${d}`"
              >
                <span class="res-icon">{{ PRIORIDAD[mapa[`${m}|${d}`]?.prioridad_residual]?.icono }}</span>
                <span class="res-label">{{ corto(mapa[`${m}|${d}`]?.prioridad_residual) }}</span>
                <small>{{ mapa[`${m}|${d}`]?.estado_intervencion.replace("Atendido con medida municipal directa", "Medida directa").replace("Parcial: ", "") }}</small>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine-print">Haga clic en una celda para ver el detalle. “DESCONOCIDA” = sin datos ni medida: no se puede afirmar que el riesgo sea bajo.</p>

    <div v-if="detalle" class="detail-box">
      <h3>{{ detalle.municipio }} · {{ detalle.dimension }} — {{ detalle.prioridad_residual }}</h3>
      <dl>
        <dt>Situación inicial</dt><dd><TextoTrazable :texto="detalle.situacion_inicial" /></dd>
        <dt>Medidas del portafolio</dt>
        <dd>
          Directas: {{ detalle.medidas_directas || "—" }} · Corredor: {{ detalle.medidas_corredor || "—" }} ·
          Por cobeneficio: {{ detalle.medidas_por_cobeneficio || "—" }}
        </dd>
        <dt>Reducción esperada</dt><dd>{{ detalle.reduccion_esperada }}</dd>
        <dt>Problemas documentados sin medida</dt><dd>{{ detalle.problemas_documentados_sin_medida }}</dd>
      </dl>
    </div>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">SEGUIMIENTO MEA</div>
        <h2>Indicadores: actividad → resultado → vulnerabilidad</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>#</th><th>Medida</th><th>Actividad (¿qué se hizo?)</th><th>Resultado (¿qué cambió?)</th><th>Vulnerabilidad (¿se redujo?)</th><th>Periodicidad</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in datos.seguimiento_mea" :key="r.alternativa">
            <td>{{ r.orden }}</td>
            <td><strong>{{ r.medida }}</strong><br /><small class="mono muted">{{ r.alternativa }}</small></td>
            <td><TextoTrazable :texto="r.actividad_que_se_hizo" /></td>
            <td><TextoTrazable :texto="r.resultado_que_cambio" /></td>
            <td><TextoTrazable :texto="r.vulnerabilidad_se_redujo" /></td>
            <td class="small muted">{{ r.periodicidad }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine-print">Indicador de actividad ≠ indicador de resultado: el primero dice qué se ejecutó; el segundo, si cambió la sensibilidad, la capacidad o la vulnerabilidad.</p>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">BRECHAS DE INFORMACIÓN</div>
        <h2>Qué debería levantar CORNARE</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Tipo</th><th>Dato</th><th>Disponible</th><th>Por qué importa</th></tr></thead>
        <tbody>
          <tr v-for="(b, i) in brechasOtras" :key="'o' + i">
            <td>{{ b.tipo }}</td><td>{{ b.dato }}</td><td>{{ b.disponible }}</td><td>{{ b.por_que_importa }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine-print">
      Además, {{ brechasDecision.length }} datos faltantes cambiarían la decisión si se midieran (ver vista “Datos y vacíos”).
      Las dependencias empresa–territorio no se infieren: se proponen como variables mínimas a caracterizar.
    </p>
  </section>
</template>
