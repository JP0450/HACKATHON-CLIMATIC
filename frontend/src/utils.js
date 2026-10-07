// Utilidades de formato y colores compartidas por las vistas

export const fmtM = (v) =>
  v == null ? "—" : `$${Number(v).toLocaleString("es-CO", { maximumFractionDigits: 0 })} M`;

export const fmtPct = (v, d = 0) =>
  v == null ? "—" : `${(Number(v) * 100).toLocaleString("es-CO", { maximumFractionDigits: d })}%`;

export const fmtNum = (v, d = 2) =>
  v == null ? "—" : Number(v).toLocaleString("es-CO", { minimumFractionDigits: d, maximumFractionDigits: d });

export const MUNICIPIOS = ["Rionegro", "Guarne", "Marinilla"];
export const DIMENSIONES = ["Biodiversidad", "Recurso hídrico", "Seguridad alimentaria", "Hábitat",
  "Infraestructura", "Riesgo de desastres", "Salud"];
export const COMPONENTES = ["Amenaza", "Sensibilidad", "Capacidad adaptativa", "Vulnerabilidad",
  "Riesgo hoy", "Riesgo SSP3-7.0 2060"];

// Paleta categórica validada (modo oscuro, superficie #171c16): orden fijo por territorio
export const COLOR_TERRITORIO = {
  Rionegro: "#3987e5",
  Guarne: "#d95926",
  Marinilla: "#199e70",
  Corredor: "#c98500",
};

// Prioridad del riesgo residual (estado: siempre acompañado de etiqueta de texto)
export const PRIORIDAD = {
  ALTA: { color: "#d03b3b", icono: "▲" },
  MEDIA: { color: "#fab219", icono: "◆" },
  BAJA: { color: "#0ca30c", icono: "▼" },
  DESCONOCIDA: { color: "#858d7e", icono: "?" },
  "SIN PROBLEMA DOCUMENTADO": { color: "#5b6355", icono: "·" },
};

export const ETIQUETAS = {
  OFICIAL: "Dato tomado de una fuente CORNARE",
  CALCULADO: "Operación sobre un dato oficial",
  DERIVADO: "Construido por el equipo con regla explícita a partir de fuentes",
  USUARIO: "Ingresado por el usuario en la plantilla",
  SUPUESTO: "Decisión metodológica del equipo",
  HISTORICO: "Estimado a partir del histórico de inversión en adaptación del corredor (no es un dato medido ni un valor neutro)",
  INFERENCIA: "Interpretación del equipo (no literal en la fuente)",
  PROPUESTO: "Indicador sugerido por el equipo",
  RELACIONADO: "Indicador oficial de una medida parecida",
  "NO DISPONIBLE": "Dato requerido que no existe en las fuentes",
};
