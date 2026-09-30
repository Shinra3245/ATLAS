export const PROJECTS = {
  housing: "Vivienda",
  building: "Edificación",
  road: "Carretera / vialidad",
};
export const CORE = [
  "flood_history",
  "faults",
  "slope",
  "landslide_susceptibility",
  "land_use",
  "elevation",
];
export const STATUS = {
  DATA_AVAILABLE: {
    label: "Dato disponible",
    tone: "available",
    description:
      "Existe un valor publicado para la unidad. No es una conclusión de seguridad.",
  },
  PARTIAL_DATA: {
    label: "Información parcial",
    tone: "partial",
    description:
      "Hay información, con limitaciones de cobertura, resolución o procedencia.",
  },
  INSUFFICIENT_DATA: {
    label: "Sin información suficiente",
    tone: "missing",
    description:
      "No hay evidencia utilizable para concluir. No significa ausencia de riesgo.",
  },
  NO_REGISTERED_CONDITION: {
    label: "Sin condición registrada",
    tone: "unregistered",
    description:
      "La fuente no registra la condición. No significa que la ubicación sea segura.",
  },
  BLOCKED_DATA_VALIDATION: {
    label: "Pendiente de validación",
    tone: "pending",
    description:
      "Existe un candidato que todavía no está validado para este análisis.",
  },
  OUTSIDE_SUPPORTED_AREA: {
    label: "Fuera del área de cobertura",
    tone: "outside",
    description: "Selecciona una localidad publicada de Irapuato o Celaya.",
  },
};
export const COVERAGE = [
  ["data_available", "Datos disponibles", "available"],
  ["partial_data", "Información parcial", "partial"],
  ["insufficient_data", "Información insuficiente", "missing"],
  ["no_registered_condition", "Sin condición registrada", "unregistered"],
  ["blocked_data_validation", "Por validar", "pending"],
];
export const FACTOR_NAMES = {
  flood_history: "Antecedente de inundación 2014",
  faults: "Fallas y fracturas",
  slope: "Pendiente del terreno",
  landslide_susceptibility: "Susceptibilidad de laderas",
  land_use: "Uso de suelo",
  elevation: "Altitud censal",
  population: "Población de la localidad",
  services_coverage: "Indicador de servicios",
  mobility: "Movilidad",
  road_proximity: "Proximidad a red vial",
  hydrography_proximity: "Proximidad a hidrografía",
  rail_proximity: "Proximidad a ferrocarril",
  industry_proximity: "Proximidad a industria",
  power_infrastructure_proximity: "Proximidad a infraestructura eléctrica",
  precipitation: "Precipitación",
};
const SOURCE_NAMES = {
  core_geospatial: "Datos censales y cartografía territorial compilados",
  statewide_census: "Información censal de Irapuato y Celaya",
  climate_celaya: "Registros de precipitación de Celaya",
  climate_irapuato: "Registros de precipitación de Irapuato",
  subbasins_state: "Referencia de subcuencas de Guanajuato",
  subbasins_national: "Referencia nacional de subcuencas",
  landuse_series_iv: "Uso del suelo y vegetación, serie IV",
  landuse_series_i: "Uso del suelo y vegetación, serie I histórica",
  rail_national: "Referencia de infraestructura ferroviaria",
  terrain_candidate: "Valores de terreno pendientes de validación",
  riesgos_naturales_localidades:
    "Indicadores municipales de fenómenos naturales",
  vulnerabilidad_resiliencia_localidades:
    "Indicadores municipales de vulnerabilidad y resiliencia",
  riesgos_ambientales_localidades: "Indicadores municipales ambientales",
  exposicion_riesgos_localidades: "Indicadores municipales de exposición",
};
const MUNICIPAL_SOURCES = new Set([
  "riesgos_naturales_localidades",
  "vulnerabilidad_resiliencia_localidades",
  "riesgos_ambientales_localidades",
  "exposicion_riesgos_localidades",
]);
export const sourceDisplayName = (source) =>
  source
    ? SOURCE_NAMES[source.id] || "Conjunto de información recibido"
    : "Sin fuente utilizable";
export function sourceInstitutionText(source) {
  if (!source) return "No documentada";
  if (MUNICIPAL_SOURCES.has(source.id))
    return "Institución original no documentada en el conjunto recibido";
  if (source.id === "core_geospatial" || source.id === "statewide_census")
    return "INEGI, atribuido en la documentación del conjunto recibido; pendiente de cotejo";
  const institution = source.institution || "";
  if (institution.includes("INEGI") && institution.includes("CONABIO"))
    return "INEGI y CONABIO, según la documentación recibida; pendiente de cotejo";
  if (institution.includes("INEGI"))
    return "INEGI, según la documentación recibida; pendiente de cotejo";
  return "Institución original no documentada";
}
export function sourceDateText(source) {
  if (!source) return "No documentada";
  if (source.id === "core_geospatial")
    return "Referencias censales de 2020 e históricas de 2014; fecha de cartografía no acreditada";
  if (MUNICIPAL_SOURCES.has(source.id)) return "Fecha original por verificar";
  const date = source.date_or_version;
  return !date || /UNKNOWN|PENDING/i.test(date)
    ? "Fecha original por verificar"
    : date;
}
export function sourceCoverageText(source) {
  if (!source) return "Cobertura no documentada";
  if (MUNICIPAL_SOURCES.has(source.id))
    return "Irapuato y Celaya; indicador municipal repetido por localidad";
  return (source.coverage_note || "Cobertura no documentada")
    .replace(/SOURCE_PROVENANCE_PARTIAL;?\s*/g, "")
    .replace(/UNKNOWN/g, "no documentada")
    .replace(/extracción MVP/gi, "extracción de Irapuato y Celaya");
}
export function sourceOriginText(factor) {
  const source = factor?.source;
  if (!source)
    return factor?.status === "BLOCKED_DATA_VALIDATION"
      ? "Hay un conjunto candidato, pero su origen y método aún deben validarse antes de usarlo."
      : "Todavía no hay una fuente utilizable para este factor en la localidad.";
  if (source.id === "core_geospatial") {
    if (["population", "elevation"].includes(factor.factor))
      return "El conjunto entregado atribuye esta variable a los resultados por localidad del Censo 2020 de INEGI. Falta cotejar el valor con la descarga oficial.";
    return "Dato de una compilación territorial entregada al proyecto. Sus notas atribuyen las capas de referencia a INEGI, pero faltan los archivos cartográficos y el cálculo original para comprobarlo.";
  }
  if (MUNICIPAL_SOURCES.has(source.id))
    return "Indicador de una compilación municipal entregada al proyecto. La institución y el documento originales aún no están identificados; no es una medición de esta localidad.";
  return `Dato de ${sourceDisplayName(source).toLowerCase()}. ${sourceInstitutionText(source)}.`;
}
export const sourceVerificationText = (source) =>
  source?.verification_status === "SOURCE_PROVENANCE_PARTIAL" ||
  source?.coverage_note?.includes("SOURCE_PROVENANCE_PARTIAL")
    ? "Procedencia original pendiente de verificación"
    : "Procedencia por verificar";
export function publicTechnicalText(value) {
  return metadataText(value)
    .replaceAll(
      "SOURCE_PROVENANCE_PARTIAL",
      "procedencia original no verificada",
    )
    .replaceAll(
      "CRS_UNKNOWN",
      "sistema de referencia de coordenadas sin verificar",
    )
    .replaceAll("GEOMETRY_LIMITATION", "limitación por falta de geometrías")
    .replaceAll(
      "PENDING_SOURCE_PROVENANCE",
      "procedencia original por verificar",
    );
}
export const DISCLAIMER =
  "Evaluación preliminar. No sustituye estudios técnicos, permisos ni dictámenes. Sin información no significa sin riesgo.";
export const isMunicipal = (factor) =>
  factor.factor?.includes("_mun_context") ||
  /municipal/i.test(factor.explanation?.meaning || "");
export const allFactors = (result) =>
  result
    ? [
        ...(result.conditions || []),
        ...(result.territorial_factors || []),
        ...(result.context || []),
      ]
    : [];
export const coreFactors = (result) =>
  CORE.map((code) => allFactors(result).find((f) => f.factor === code)).filter(
    Boolean,
  );
export const factorName = (factor) =>
  FACTOR_NAMES[factor.factor] || factor.label || factor.factor;
export const temporalLabel = (value) =>
  ({
    historical: "Antecedente histórico",
    reference_period: "Período de referencia",
    current: "Actual según fuente",
    unknown: "Temporalidad no documentada",
    not_applicable: "No aplica / sin dato utilizable",
  })[value] || "No documentado";
export const metadataText = (value) =>
  !value || /^(UNKNOWN|CRS_UNKNOWN|PENDING.*)$/i.test(value)
    ? value === "CRS_UNKNOWN"
      ? "CRS_UNKNOWN"
      : "No documentado / por verificar"
    : String(value);
export function formatValue(value, unit, code = "") {
  if (value === null || value === undefined || value === "") return "Sin dato";
  if (typeof value === "boolean")
    return value ? "Registrado en la fuente" : "Sin condición registrada";
  if (code === "flood_history")
    return Number(value) === 1
      ? "Antecedente registrado"
      : "Sin antecedente registrado";
  if (typeof value !== "number") return String(value);
  const formatted = new Intl.NumberFormat("es-MX", {
    maximumFractionDigits: Number.isInteger(value)
      ? 0
      : unit === "ratio_0_1"
        ? 6
        : 2,
  }).format(value);
  const suffix =
    {
      persons: "personas",
      dwellings: "viviendas",
      ratio_0_1: "(escala 0–1)",
      binary_code: "",
      decimal_degrees: "°",
    }[unit] ?? unit;
  return `${formatted}${suffix ? ` ${suffix}` : ""}`;
}
const COMPARABLE = new Set(["DATA_AVAILABLE", "PARTIAL_DATA"]);
function hasComparableValue(status, value) {
  return (
    COMPARABLE.has(status) && value !== null && value !== undefined && value !== ""
  );
}
export function plainDifference(factor) {
  const aHas = hasComparableValue(factor.status_a, factor.value_a);
  const bHas = hasComparableValue(factor.status_b, factor.value_b);
  const text = (side) =>
    formatValue(
      factor[side === "A" ? "value_a" : "value_b"],
      factor.unit,
      factor.factor,
    );
  if (aHas && bHas) {
    return factor.value_a === factor.value_b
      ? `En A y en B el dato es el mismo: ${text("A")}.`
      : `En A: ${text("A")}. En B: ${text("B")}.`;
  }
  if (aHas || bHas) {
    const side = aHas ? "A" : "B";
    const other = aHas ? "B" : "A";
    return `Solo está en ${side}: ${text(side)}. En ${other} no hay información para comparar.`;
  }
  return "No hay información para comparar este dato.";
}
export function asLocation(record) {
  if (
    !record?.id ||
    !Number.isFinite(record.latitude) ||
    !Number.isFinite(record.longitude)
  )
    throw new Error(
      "La localidad no tiene una identidad o coordenadas publicadas válidas.",
    );
  return {
    lat: record.latitude,
    lon: record.longitude,
    locality_id: record.id,
    label: record.locality,
  };
}
export function filterLocations(records, municipality, query) {
  const normalize = (s) =>
    String(s || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  const q = normalize(query.trim());
  return records.filter(
    (r) =>
      (!municipality || r.municipality === municipality) &&
      (!q || normalize(`${r.locality} ${r.id}`).includes(q)),
  );
}
export function summarize(factors) {
  const result = Object.fromEntries(COVERAGE.map(([key]) => [key, 0]));
  const keys = {
    DATA_AVAILABLE: "data_available",
    PARTIAL_DATA: "partial_data",
    INSUFFICIENT_DATA: "insufficient_data",
    NO_REGISTERED_CONDITION: "no_registered_condition",
    BLOCKED_DATA_VALIDATION: "blocked_data_validation",
  };
  for (const factor of factors)
    if (keys[factor.status]) result[keys[factor.status]]++;
  return { ...result, expected: factors.length };
}
export function validExternalUrl(value) {
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}
