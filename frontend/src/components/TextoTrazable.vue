<script setup>
// Muestra un texto y convierte sus etiquetas [OFICIAL], [INFERENCIA]... en chips de trazabilidad
import { computed } from "vue";
import { ETIQUETAS } from "../utils.js";

const props = defineProps({ texto: { type: [String, Number], default: "" } });
const RE = /\[(OFICIAL|CALCULADO|DERIVADO|USUARIO|SUPUESTO|INFERENCIA|PROPUESTO|RELACIONADO|NO DISPONIBLE)([^\]]*)\]|(NO DISPONIBLE)/g;

const partes = computed(() => {
  const s = String(props.texto ?? "");
  const out = [];
  let ultimo = 0;
  for (const m of s.matchAll(RE)) {
    if (m.index > ultimo) out.push({ t: s.slice(ultimo, m.index) });
    const tipo = m[1] || m[3];
    out.push({ chip: tipo, extra: (m[2] || "").replace(/^[:\s]+/, "") });
    ultimo = m.index + m[0].length;
  }
  if (ultimo < s.length) out.push({ t: s.slice(ultimo) });
  return out;
});
</script>

<template>
  <span class="trazable">
    <template v-for="(p, i) in partes" :key="i">
      <span v-if="p.t">{{ p.t }}</span>
      <span
        v-else
        class="chip"
        :class="`chip-${p.chip.replace(' ', '-').toLowerCase()}`"
        :title="ETIQUETAS[p.chip] + (p.extra ? ' · ' + p.extra : '')"
      >{{ p.chip }}<template v-if="p.extra">: {{ p.extra }}</template></span>
    </template>
  </span>
</template>
