import test from "node:test";
import assert from "node:assert/strict";
import { guideMoment } from "../../src/guide/moments.mjs";

const base = {
  route: "/sistema",
  phase: "selectA",
  busy: false,
  error: null,
  selected: false,
  catalogLoading: false,
  catalogError: null,
};

test("el inicio invita a explorar", () => {
  const moment = guideMoment({ ...base, route: "/" });
  assert.equal(moment.expression, "happy");
  assert.match(moment.prompt, /por dónde empezar/);
  assert.match(moment.message, /Explorar ATLAS/);
});

test("las vistas de información explican su contenido", () => {
  assert.equal(guideMoment({ ...base, route: "/metodologia" }).expression, "idle");
  assert.match(guideMoment({ ...base, route: "/fuentes" }).message, /cobertura/);
  assert.match(guideMoment({ ...base, route: "/estados" }).message, /disponibilidad/);
  assert.equal(guideMoment({ ...base, route: "/ficha/a" }).expression, "idle");
  assert.match(guideMoment({ ...base, route: "/ficha/b" }).message, /ficha/);
});

test("una ruta desconocida no inventa una pantalla", () => {
  const moment = guideMoment({ ...base, route: "/no-existe" });
  assert.equal(moment.expression, "unsure");
  assert.match(moment.message, /no existe/);
});

test("la selección cambia al elegir localidad", () => {
  assert.equal(guideMoment(base).expression, "idle");
  assert.equal(guideMoment({ ...base, selected: true }).expression, "happy");
  assert.equal(
    guideMoment({ ...base, phase: "selectB", selected: false }).expression,
    "unsure",
  );
  assert.equal(
    guideMoment({ ...base, phase: "selectB", selected: true }).expression,
    "happy",
  );
});

test("resultado y comparación mantienen la misma lectura", () => {
  assert.match(guideMoment({ ...base, phase: "result" }).message, /ausencia de riesgo/);
  assert.match(
    guideMoment({ ...base, phase: "comparison" }).message,
    /ganador automático/,
  );
  assert.equal(guideMoment({ ...base, phase: "comparison" }).expression, "happy");
});

test("la carga y el error se imponen a la fase", () => {
  assert.equal(
    guideMoment({ ...base, selected: true, busy: true }).expression,
    "thinking",
  );
  assert.match(
    guideMoment({ ...base, phase: "selectB", busy: true }).message,
    /comparando/,
  );
  assert.equal(
    guideMoment({ ...base, selected: true, error: "falló" }).expression,
    "unsure",
  );
  assert.equal(
    guideMoment({ ...base, catalogLoading: true, selected: true }).expression,
    "thinking",
  );
  assert.equal(
    guideMoment({
      ...base,
      catalogLoading: true,
      catalogError: "falló",
    }).expression,
    "unsure",
  );
  assert.equal(
    guideMoment({ ...base, route: "/fuentes", catalogLoading: true }).expression,
    "thinking",
  );
  assert.equal(
    guideMoment({ ...base, route: "/", catalogLoading: true }).expression,
    "happy",
  );
});
