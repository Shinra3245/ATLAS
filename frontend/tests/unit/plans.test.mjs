import test from "node:test";
import assert from "node:assert/strict";
import { PLANS, PLAN_IDS, canAnalyze, canCompare, planById } from "../../src/plans.mjs";

test("hay tres planes: Básico, Profesional y MAX", () => {
  assert.deepEqual(PLAN_IDS, ["basico", "profesional", "max"]);
  assert.equal(PLANS.length, 3);
  for (const plan of PLANS) {
    assert.equal(planById(plan.id), plan);
  }
  assert.equal(planById("otro"), null);
  const basico = planById("basico");
  assert.equal(basico.cost, "Sin costo");
  assert.equal("price" in basico, false);
  const profesional = planById("profesional");
  assert.equal(profesional.cost, "$399 MXN al mes");
  assert.deepEqual(profesional.price, { amount: "$399", detail: "MXN al mes · por persona" });
  assert.match(profesional.includes.join(" "), /10 análisis/);
  const max = planById("max");
  assert.equal(max.name, "MAX");
  assert.equal(max.cost, "$799 MXN al mes");
  assert.deepEqual(max.price, { amount: "$799", detail: "MXN al mes · por persona" });
  assert.match(max.includes.join(" "), /ilimitados/);
});

test("la comparación y el tope mensual siguen al plan", () => {
  const now = new Date(2026, 8, 30);
  const basicFull = { usageMonth: "2026-09", analysisCount: 3 };
  const professionalFull = { usageMonth: "2026-09", analysisCount: 10 };
  const previous = { usageMonth: "2026-08", analysisCount: 10 };
  assert.equal(canCompare("basico"), false);
  assert.equal(canCompare("profesional"), true);
  assert.equal(canCompare("max"), true);
  assert.equal(canCompare("estudiante"), true);
  assert.equal(canCompare("cliente"), true);
  assert.equal(canCompare(null), false);
  assert.equal(canAnalyze("basico", { usageMonth: "2026-09", analysisCount: 2 }, now), true);
  assert.equal(canAnalyze("basico", basicFull, now), false);
  assert.equal(canAnalyze("basico", previous, now), true);
  assert.equal(canAnalyze("basico", null, now), true);
  assert.equal(canAnalyze("profesional", { usageMonth: "2026-09", analysisCount: 9 }, now), true);
  assert.equal(canAnalyze("profesional", professionalFull, now), false);
  assert.equal(canAnalyze("profesional", previous, now), true);
  assert.equal(canAnalyze("max", professionalFull, now), true);
  assert.equal(canAnalyze("estudiante", basicFull, now), true);
  assert.equal(canAnalyze("cliente", basicFull, now), true);
  assert.equal(canAnalyze(null, null, now), false);
});
