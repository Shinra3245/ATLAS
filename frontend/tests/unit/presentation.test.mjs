import test from "node:test";
import assert from "node:assert/strict";
import {
  STATUS,
  asLocation,
  filterLocations,
  formatValue,
  plainDifference,
  metadataText,
  summarize,
  validExternalUrl,
  isMunicipal,
  sourceDisplayName,
  sourceInstitutionText,
  sourceOriginText,
  sourceVerificationText,
} from "../../src/utils/presentation.mjs";

test("nulos no se convierten en cero o seguridad", () => {
  assert.equal(formatValue(null, "m"), "Sin dato");
  assert.equal(formatValue(0, "m"), "0 m");
  assert.equal(
    formatValue(0, null, "flood_history"),
    "Sin antecedente registrado",
  );
  assert.equal(formatValue(1, null, "flood_history"), "Antecedente registrado");
  assert.match(STATUS.NO_REGISTERED_CONDITION.description, /No significa/);
});
test("la diferencia observable se lee en frases cortas", () => {
  assert.equal(
    plainDifference({
      factor: "slope",
      status_a: "DATA_AVAILABLE",
      status_b: "PARTIAL_DATA",
      value_a: 14,
      value_b: 9,
      unit: "%",
    }),
    "En A: 14 %. En B: 9 %.",
  );
  assert.equal(
    plainDifference({
      factor: "elevation",
      status_a: "DATA_AVAILABLE",
      status_b: "DATA_AVAILABLE",
      value_a: 1720,
      value_b: 1720,
      unit: "m",
    }),
    "En A y en B el dato es el mismo: 1,720 m.",
  );
  assert.equal(
    plainDifference({
      factor: "land_use",
      status_a: "DATA_AVAILABLE",
      status_b: "INSUFFICIENT_DATA",
      value_a: "agrícola",
      value_b: null,
      unit: null,
    }),
    "Solo está en A: agrícola. En B no hay información para comparar.",
  );
  assert.equal(
    plainDifference({
      factor: "faults",
      status_a: "INSUFFICIENT_DATA",
      status_b: "BLOCKED_DATA_VALIDATION",
      value_a: null,
      value_b: null,
      unit: null,
    }),
    "No hay información para comparar este dato.",
  );
  assert.equal(
    plainDifference({
      factor: "flood_history",
      status_a: "DATA_AVAILABLE",
      status_b: "DATA_AVAILABLE",
      value_a: 1,
      value_b: 0,
      unit: "binary_code",
    }),
    "En A: Antecedente registrado. En B: Sin antecedente registrado.",
  );
});
test("los estados son de disponibilidad y preservan las seis variantes", () => {
  assert.equal(Object.keys(STATUS).length, 6);
  assert.match(
    STATUS.INSUFFICIENT_DATA.description,
    /No significa ausencia de riesgo/,
  );
  assert.match(STATUS.BLOCKED_DATA_VALIDATION.label, /validación/);
});
test("filtro por municipio, nombre sin acentos y CVEGEO, sin inventar registros", () => {
  const rows = [
    { id: "110170001", locality: "Irapuato", municipality: "Irapuato" },
    { id: "110070001", locality: "Celaya", municipality: "Celaya" },
    { id: "110170010", locality: "Purísima", municipality: "Irapuato" },
  ];
  assert.equal(filterLocations(rows, "Irapuato", "").length, 2);
  assert.equal(
    filterLocations(rows, "Irapuato", "purisima")[0].id,
    "110170010",
  );
  assert.equal(filterLocations(rows, "Celaya", "110070001").length, 1);
  assert.equal(filterLocations(rows, "Irapuato", "no existe").length, 0);
});
test("entrada de análisis conserva identidad y coordenadas del catálogo", () => {
  assert.deepEqual(
    asLocation({
      id: "110170001",
      locality: "Irapuato",
      latitude: 20.6,
      longitude: -101.3,
    }),
    { lat: 20.6, lon: -101.3, locality_id: "110170001", label: "Irapuato" },
  );
  assert.throws(() => asLocation({ id: "x", latitude: NaN, longitude: -101 }));
});
test("cobertura cuenta estados, no porcentajes", () => {
  const result = summarize([
    { status: "DATA_AVAILABLE" },
    { status: "INSUFFICIENT_DATA" },
    { status: "INSUFFICIENT_DATA" },
    { status: "BLOCKED_DATA_VALIDATION" },
  ]);
  assert.equal(result.expected, 4);
  assert.equal(result.data_available, 1);
  assert.equal(result.insufficient_data, 2);
  assert.equal(result.blocked_data_validation, 1);
  assert.ok(
    !Object.keys(result).some((key) => /score|percent|winner/.test(key)),
  );
});
test("URL externa solo HTTP/S; procedencia desconocida permanece visible", () => {
  assert.equal(validExternalUrl("javascript:alert(1)"), null);
  assert.equal(validExternalUrl("file:///data/raw/example.xlsx"), null);
  assert.equal(validExternalUrl("UNKNOWN"), null);
  assert.equal(
    validExternalUrl("https://example.org/data"),
    "https://example.org/data",
  );
  assert.equal(metadataText("CRS_UNKNOWN"), "CRS_UNKNOWN");
  assert.match(metadataText("PENDING_SOURCE_PROVENANCE"), /verificar/);
});
test("contexto municipal permanece separado", () => {
  assert.equal(isMunicipal({ factor: "gp_inundac_mun_context" }), true);
  assert.equal(
    isMunicipal({
      factor: "population",
      explanation: { meaning: "Población de la localidad" },
    }),
    false,
  );
});

test("procedencia pública distingue atribución declarada de origen comprobado", () => {
  const core = { id: "core_geospatial", name: "compilacion.xlsx" };
  const municipal = {
    id: "riesgos_naturales_localidades",
    name: "riesgos.xlsx",
  };
  assert.doesNotMatch(sourceDisplayName(core), /\.xlsx|core_geospatial/);
  assert.match(sourceInstitutionText(core), /pendiente de cotejo/);
  assert.match(
    sourceOriginText({ factor: "elevation", source: core }),
    /según|atribuye/i,
  );
  assert.doesNotMatch(
    sourceOriginText({ factor: "elevation", source: core }),
    /\.xlsx/,
  );
  assert.match(sourceInstitutionText(municipal), /no documentada/);
  assert.match(
    sourceOriginText({ factor: "inundacion_mun_context", source: municipal }),
    /no es una medición/,
  );
  assert.match(
    sourceVerificationText({
      verification_status: "SOURCE_PROVENANCE_PARTIAL",
    }),
    /pendiente/,
  );
  assert.match(
    sourceOriginText({ factor: "slope", status: "BLOCKED_DATA_VALIDATION" }),
    /validarse/,
  );
});
