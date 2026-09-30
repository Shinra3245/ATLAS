export const PLANS = [
  {
    id: "basico",
    name: "Básico",
    audience: "Plan 1",
    cost: "Sin costo",
    summary:
      "Consulta el mapa, los tres tipos de proyecto y la ficha con fuentes y faltantes.",
    includes: [
      "Mapa de localidades de Irapuato y Celaya",
      "Vivienda, edificación y carretera / vialidad",
      "Hasta 3 análisis al mes",
      "Ficha con fuentes, cobertura y limitaciones",
    ],
  },
  {
    id: "profesional",
    name: "Profesional",
    audience: "Plan 2",
    cost: "$399 MXN al mes",
    price: { amount: "$399", detail: "MXN al mes · por persona" },
    summary: "Para repetir análisis y comparar localidades con un cupo mensual.",
    includes: [
      "Hasta 10 análisis al mes",
      "Comparación A/B",
      "Informe de la ficha",
      "Una cuenta por persona",
    ],
  },
  {
    id: "max",
    name: "MAX",
    audience: "Plan 3",
    cost: "$799 MXN al mes",
    price: { amount: "$799", detail: "MXN al mes · por persona" },
    summary: "Para consultar sin tope mensual de análisis.",
    includes: [
      "Análisis ilimitados",
      "Comparación A/B",
      "Informe de la ficha",
      "Una cuenta por persona",
    ],
  },
];

export const PLAN_IDS = PLANS.map((plan) => plan.id);
export const LEGACY_PLAN_IDS = ["estudiante", "cliente"];
export const BASIC_ANALYSIS_LIMIT = 3;
export const PROFESSIONAL_ANALYSIS_LIMIT = 10;

export function isKnownPlan(id) {
  return PLAN_IDS.includes(id) || LEGACY_PLAN_IDS.includes(id);
}

export function analysisLimit(role) {
  if (role === "basico") return BASIC_ANALYSIS_LIMIT;
  if (role === "profesional") return PROFESSIONAL_ANALYSIS_LIMIT;
  if (role === "max" || role === "estudiante" || role === "cliente") return null;
  return 0;
}

export function planById(id) {
  return PLANS.find((plan) => plan.id === id) || null;
}

export function usageMonth(date = new Date()) {
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${date.getFullYear()}-${month}`;
}

function analysesThisMonth(usage, date) {
  if (!usage || usage.usageMonth !== usageMonth(date)) return 0;
  return Number.isInteger(usage.analysisCount) ? usage.analysisCount : BASIC_ANALYSIS_LIMIT;
}

export function canCompare(role) {
  return role === "profesional" || role === "max" || role === "estudiante" || role === "cliente";
}

export function canAnalyze(role, usage, date = new Date()) {
  const limit = analysisLimit(role);
  if (limit == null) return role === "max" || role === "estudiante" || role === "cliente";
  if (limit === 0) return false;
  return analysesThisMonth(usage, date) < limit;
}
