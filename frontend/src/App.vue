<script setup>
// Tablero de decisión: solo lee public/resultados.json (lo genera 3_reportes.py). No calcula nada.
import { onMounted, ref } from "vue";
import { ChartNoAxesCombined, Database, Leaf, ListChecks, Menu, ShieldCheck, TriangleAlert, X } from "lucide-vue-next";
import VistaResumen from "./views/VistaResumen.vue";
import VistaPortafolio from "./views/VistaPortafolio.vue";
import VistaDatos from "./views/VistaDatos.vue";
import VistaRobustez from "./views/VistaRobustez.vue";
import VistaResidual from "./views/VistaResidual.vue";

const datos = ref(null);
const cargando = ref(true);
const error = ref("");
const vista = ref("Resumen");
const menuAbierto = ref(false);

const vistas = [
  { label: "Resumen", icon: ChartNoAxesCombined, comp: VistaResumen, producto: "Producto 1" },
  { label: "Portafolio", icon: ListChecks, comp: VistaPortafolio, producto: "Producto 2" },
  { label: "Datos y vacíos", icon: Database, comp: VistaDatos, producto: "Producto 1 · 3" },
  { label: "Robustez", icon: ShieldCheck, comp: VistaRobustez, producto: "Producto 2" },
  { label: "Riesgo residual", icon: TriangleAlert, comp: VistaResidual, producto: "Producto 3" },
];

async function cargar() {
  cargando.value = true;
  error.value = "";
  try {
    const r = await fetch("./resultados.json", { cache: "no-store" });
    if (!r.ok) throw new Error(`No se encontró resultados.json (estado ${r.status}).`);
    datos.value = await r.json();
  } catch (e) {
    error.value = e instanceof Error ? e.message : "No fue posible leer los resultados.";
  } finally {
    cargando.value = false;
  }
}

function ir(label) {
  vista.value = label;
  menuAbierto.value = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(cargar);
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ 'sidebar-open': menuAbierto }">
      <a class="brand" href="#" aria-label="Climatic, inicio" @click.prevent="ir('Resumen')">
        <span class="brand-mark"><Leaf :size="21" :stroke-width="2.2" /></span>
        <span>climatic<span class="brand-period">.</span></span>
      </a>

      <div class="workspace-label">MOTOR DE DECISIÓN</div>
      <nav class="side-nav" aria-label="Vistas del tablero">
        <button
          v-for="item in vistas"
          :key="item.label"
          class="nav-item"
          :class="{ 'nav-item-active': vista === item.label }"
          @click="ir(item.label)"
        >
          <component :is="item.icon" :size="18" :stroke-width="1.8" />
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-bottom">
        <div class="sidebar-note">
          <div class="note-icon"><ShieldCheck :size="17" /></div>
          <p>Corredor Rionegro · Guarne · Marinilla</p>
          <span>Fondo de adaptación de $5.000 M · Reto CORNARE</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <button
          class="mobile-menu icon-button"
          :aria-label="menuAbierto ? 'Cerrar menú' : 'Abrir menú'"
          @click="menuAbierto = !menuAbierto"
        >
          <X v-if="menuAbierto" :size="19" />
          <Menu v-else :size="19" />
        </button>
        <div class="breadcrumb">
          Tablero <span>/</span> <strong>{{ vista }}</strong>
          <em class="breadcrumb-tag">{{ vistas.find((v) => v.label === vista)?.producto }}</em>
        </div>
        <div class="topbar-actions">
          <span class="live-status static-status"><span></span> Fuente: CORNARE · modelo reproducible</span>
        </div>
      </header>

      <div v-if="cargando" class="state-message" role="status">
        <span class="loader"></span>
        Leyendo resultados del motor…
      </div>
      <div v-else-if="error" class="state-message error-message" role="alert">
        <div>
          <strong>No se pudieron leer los resultados</strong>
          <span>{{ error }} Ejecute <code>python 3_reportes.py</code>: copia el archivo a <code>frontend/public/</code>.</span>
        </div>
        <button class="retry-button" @click="cargar">Reintentar</button>
      </div>

      <template v-else-if="datos">
        <component :is="vistas.find((v) => v.label === vista).comp" :datos="datos" @ir="ir" />

        <footer class="page-footer">
          <span>{{ datos.meta.titulo }} · {{ datos.meta.decision_stress }}</span>
          <span>Datos institucionales, supuestos e inferencias marcados en cada cifra</span>
        </footer>
      </template>
    </main>
  </div>
</template>
