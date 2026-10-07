<script setup>
// Vista 3 · Datos y vacíos: la ficha municipio × dimensión y qué dato faltante cambiaría la decisión
import { computed } from "vue";
import { Crosshair } from "lucide-vue-next";
import TextoTrazable from "../components/TextoTrazable.vue";
import { COMPONENTES, DIMENSIONES, MUNICIPIOS, fmtNum } from "../utils.js";

const props = defineProps({ datos: { type: Object, required: true } });
defineEmits(["ir"]);

const celda = computed(() => {
  const m = {};
  for (const r of props.datos.ficha) m[`${r.municipio} · ${r.dimension} · ${r.componente}`] = r;
  return m;
});
const voi = computed(() => {
  const m = {};
  for (const r of props.datos.datos_que_cambian_la_decision) m[r.celda_vacia] = r;
  return m;
});
const conteo = computed(() => {
  const c = { OFICIAL: 0, CALCULADO: 0, USUARIO: 0, "NO DISPONIBLE": 0 };
  for (const r of props.datos.ficha) c[r.origen] = (c[r.origen] || 0) + 1;
  return c;
});
const vaciasPorClave = computed(() => {
  const m = {};
  for (const r of props.datos.celdas_vacias || []) m[r.celda] = r;
  return m;
});
// Entre los valores "vacíos" rellenados, solo distinguimos el que viene del histórico
// (los demás —promedio regional, valor fijo— se siguen mostrando como antes).
function historicoUsado(clave) {
  const r = vaciasPorClave.value[clave];
  return r && r.regla?.startsWith("estimado desde histórico") ? r : null;
}
function chipTag(regla) {
  return regla?.startsWith("estimado desde histórico") ? "HISTORICO" : "SUPUESTO";
}

function umbrales(r) {
  const p = [];
  if (r.cambia_QUE_si_sube_a != null) p.push(`cambia QUÉ medidas si ≥ ${fmtNum(r.cambia_QUE_si_sube_a)}`);
  if (r.cambia_QUE_si_baja_a != null) p.push(`cambia QUÉ medidas si ≤ ${fmtNum(r.cambia_QUE_si_baja_a)}`);
  if (r.cambia_DONDE_si_sube_a != null) p.push(`cambia DÓNDE si ≥ ${fmtNum(r.cambia_DONDE_si_sube_a)}`);
  if (r.cambia_DONDE_si_baja_a != null) p.push(`cambia DÓNDE si ≤ ${fmtNum(r.cambia_DONDE_si_baja_a)}`);
  return p.join(" · ");
}
function tooltip(clave) {
  const c = celda.value[clave];
  if (!c) return "";
  if (c.origen !== "NO DISPONIBLE") return `${c.origen}: ${fmtNum(c.valor, 3)}${c.fuente ? " · " + c.fuente : ""}`;
  const h = historicoUsado(clave);
  const base = h ? `HISTÓRICO · ${fmtNum(h.valor_caso_base, 3)} · ${h.regla}` : "NO DISPONIBLE · probado de 0 a 1";
  const v = voi.value[clave];
  return v ? `${base} · ${umbrales(v)}` : `${base} · no cambia la decisión`;
}
const cambiaQue = (r) => r.cambia_QUE_si_sube_a != null || r.cambia_QUE_si_baja_a != null;
const ordenVoi = computed(() =>
  [...props.datos.datos_que_cambian_la_decision].sort((a, b) => Number(cambiaQue(b)) - Number(cambiaQue(a)))
);
</script>

<template>
  <section class="welcome-section compact">
    <div>
      <div class="eyebrow"><span class="eyebrow-line"></span> PRODUCTOS 1 Y 3</div>
      <h1>Lo que sabemos, <span>y lo que falta medir.</span></h1>
      <p class="welcome-copy">
        Ficha CORNARE por municipio × dimensión. Las celdas vacías no se rellenan con datos inventados:
        el motor prueba todo el rango 0–1 y marca con <Crosshair :size="13" /> las que podrían cambiar la decisión.
      </p>
    </div>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">FICHA DE DIMENSIONES · 126 CELDAS</div>
        <h2>Amenaza, sensibilidad, capacidad, vulnerabilidad y riesgo</h2>
      </div>
      <div class="count-pills">
        <span class="cell-oficial pill">Oficial {{ conteo.OFICIAL }}</span>
        <span class="cell-calculado pill">Calculado {{ conteo.CALCULADO }}</span>
        <span class="cell-usuario pill">Usuario {{ conteo.USUARIO }}</span>
        <span class="cell-vacia pill">No disponible {{ conteo["NO DISPONIBLE"] }}</span>
      </div>
    </div>

    <div class="table-wrap">
      <table class="ficha">
        <thead>
          <tr>
            <th>Municipio</th><th>Dimensión</th>
            <th v-for="c in COMPONENTES" :key="c">{{ c }}</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="m in MUNICIPIOS" :key="m">
            <tr v-for="(d, i) in DIMENSIONES" :key="m + d" :class="{ 'group-start': i === 0 }">
              <th v-if="i === 0" :rowspan="DIMENSIONES.length" class="muni-cell">{{ m }}</th>
              <td class="dim-cell">{{ d }}</td>
              <td
                v-for="c in COMPONENTES"
                :key="c"
                :class="[
                  'val',
                  `cell-${(celda[`${m} · ${d} · ${c}`]?.origen || 'NO DISPONIBLE').replace(' ', '-').toLowerCase()}`,
                  { 'cell-voi': voi[`${m} · ${d} · ${c}`] },
                ]"
                :title="tooltip(`${m} · ${d} · ${c}`)"
              >
                <template v-if="celda[`${m} · ${d} · ${c}`]?.origen !== 'NO DISPONIBLE'">
                  {{ fmtNum(celda[`${m} · ${d} · ${c}`]?.valor, celda[`${m} · ${d} · ${c}`]?.origen === 'CALCULADO' ? 3 : 2) }}
                </template>
                <template v-else-if="historicoUsado(`${m} · ${d} · ${c}`)">
                  <span class="val-historico">{{ fmtNum(historicoUsado(`${m} · ${d} · ${c}`).valor_caso_base, 2) }}</span>
                  <Crosshair v-if="voi[`${m} · ${d} · ${c}`]" :size="11" class="voi-mark" />
                </template>
                <template v-else-if="voi[`${m} · ${d} · ${c}`]"><Crosshair :size="13" /></template>
                <template v-else>—</template>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <p class="fine-print">Pase el mouse sobre una celda para ver su fuente o su tratamiento. Amenaza y sensibilidad son contexto: no entran al puntaje.</p>
  </section>

  <section class="panel">
    <div class="card-heading">
      <div>
        <div class="section-kicker">VALOR DE LA INFORMACIÓN</div>
        <h2>Datos faltantes que cambiarían la decisión</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>Dato faltante</th><th>Valor usado mientras tanto</th><th>Umbral</th><th>Portafolio si se cruza el umbral</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in ordenVoi" :key="r.celda_vacia">
            <td><strong>{{ r.celda_vacia }}</strong></td>
            <td><TextoTrazable :texto="`${fmtNum(r.valor_caso_base)} [${chipTag(r.regla_caso_base)}: ${r.regla_caso_base}]`" /></td>
            <td :class="{ 'strong-change': cambiaQue(r) }">{{ umbrales(r) }}</td>
            <td class="mono">{{ r.portafolio_resultante }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="fine-print">
      “Cambia QUÉ” = entran o salen medidas. “Cambia DÓNDE” = la misma medida se muda de municipio.
      Estas celdas son las que CORNARE debería medir primero.
    </p>
  </section>
</template>
