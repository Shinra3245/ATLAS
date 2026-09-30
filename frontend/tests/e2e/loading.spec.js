import { test, expect } from "@playwright/test";

const tile = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aD1sAAAAASUVORK5CYII=", "base64");
const tileURL = "https://tile.openstreetmap.org/**";

function gate() {
  let release;
  const promise = new Promise(resolve => { release = resolve; });
  return { promise, release };
}

async function holdResponse(page, url, pending) {
  await page.route(url, async route => {
    const response = await route.fetch();
    await pending.promise;
    await route.fulfill({ response });
  });
}

async function selectLocality(page, id) {
  await page.getByLabel("Buscar localidad por nombre o clave").fill(id);
  await page.locator(".locality-option").filter({ hasText: id }).click();
}

async function analysisA(page) {
  await page.goto("/#/sistema");
  await selectLocality(page, "110170001");
  await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
  await expect(page.getByRole("heading", { name: /Evaluación territorial preliminar/ })).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await page.route(tileURL, route => route.fulfill({ contentType: "image/png", body: tile }));
});

test("catálogos: loader sin etapas y cierre al recibir los datos", async ({ page }) => {
  const pending = gate();
  await holdResponse(page, "**/api/locations", pending);
  try {
    await page.goto("/#/sistema");
    const loading = page.locator(".workspace-panel .geo-pulse");
    await expect(loading).toContainText("Cargando localidades");
    await expect(loading.locator(".geo-pulse-mark")).toHaveAttribute("href", "/atlas-logo.png");
    await expect(loading.locator(".geo-pulse-steps")).toHaveCount(0);
    await page.getByRole("link", { name: "Fuentes", exact: true }).click();
    await expect(page.locator(".geo-pulse-panel")).toContainText("Cargando fuentes");
    pending.release();
    await expect(page.locator(".source-card").first()).toBeVisible();
    await expect(page.locator(".geo-pulse-panel")).toHaveCount(0);
  } finally { pending.release(); }
});

test("consulta rápida y ficha en memoria: sin modal ni espera añadida", async ({ page }) => {
  await page.goto("/#/sistema");
  await selectLocality(page, "110170001");
  await page.evaluate(() => {
    window.sawLoadingDialog = false;
    new MutationObserver(() => {
      if (document.querySelector(".geo-pulse-dialog")) window.sawLoadingDialog = true;
    }).observe(document.body, { childList: true, subtree: true });
  });
  await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
  await expect(page.getByRole("heading", { name: /Evaluación territorial preliminar/ })).toBeVisible();
  expect(await page.evaluate(() => window.sawLoadingDialog)).toBe(false);
  await page.getByRole("button", { name: "Ver ficha", exact: true }).click();
  await expect(page.locator(".report-page")).toHaveCount(3);
  await expect(page.locator(".geo-pulse, .geo-pulse-dialog")).toHaveCount(0);
});

test("consulta lenta: botón, modal y etapas reales; accesibilidad móvil", async ({ page }) => {
  const pending = gate();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await holdResponse(page, "**/api/analyze", pending);
  try {
    await page.goto("/#/sistema");
    await selectLocality(page, "110170001");
    await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
    const button = page.getByRole("button", { name: "Analizando localidad…", exact: true });
    await expect(button).toBeDisabled();
    await expect(button).toHaveAttribute("aria-busy", "true");
    await expect(button.locator(".geo-pulse-icon-compact")).toBeVisible();
    await button.screenshot({ path: "test-results/geo-pulse-button.png" });
    const dialog = page.getByRole("dialog", { name: "Analizando localidad…", exact: true });
    await expect(dialog).toBeVisible();
    await expect(dialog.locator(".geo-pulse-step-active")).toContainText("Consultando factores y evidencia");
    await expect(dialog.locator(".geo-pulse-step-complete")).toHaveCount(1);
    await expect(dialog.locator(".geo-pulse-step-pending")).toContainText("Preparando evaluación");
    await page.clock.install();
    await page.clock.fastForward(9000);
    await expect(dialog.locator(".geo-pulse-step-complete")).toHaveCount(1);
    await expect(dialog.locator(".geo-pulse-step-active")).toContainText("Consultando factores y evidencia");
    await dialog.screenshot({ path: "test-results/geo-pulse-analysis-modal.png" });
    await page.emulateMedia({ reducedMotion: "reduce" });
    for (const width of [390, 320]) {
      await page.setViewportSize({ width, height: 812 });
      await page.clock.runFor(100);
      await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      expect(await dialog.evaluate(element => element.scrollWidth <= element.clientWidth)).toBe(true);
      await expect(dialog.locator(".geo-pulse-wave").first()).toHaveCSS("animation-name", "none");
    }
    await dialog.screenshot({ path: "test-results/geo-pulse-mobile-modal.png" });
    await expect(page.getByRole("button", { name: "Cancelar consulta", exact: true })).toBeFocused();
    pending.release();
    await expect(dialog).toHaveCount(0);
    await expect(page.getByRole("heading", { name: /Evaluación territorial preliminar/ })).toBeVisible();
    await expect(page.locator(".workspace-panel")).toBeFocused();
    expect(errors).toEqual([]);
  } finally { pending.release(); }
});

for (const method of ["button", "escape"]) {
  test(`cancelar consulta con ${method}: descarta respuesta tardía y permite reintentar`, async ({ page }) => {
    const pending = gate();
    await holdResponse(page, "**/api/analyze", pending);
    try {
      await page.goto("/#/sistema");
      await selectLocality(page, "110170001");
      await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
      await expect(page.locator(".geo-pulse-dialog")).toBeVisible();
      if (method === "button") await page.getByRole("button", { name: "Cancelar consulta", exact: true }).click();
      else await page.keyboard.press("Escape");
      await expect(page.locator(".geo-pulse-dialog")).toHaveCount(0);
      await expect(page.getByRole("button", { name: "Analizar localidad", exact: true })).toBeEnabled();
      pending.release();
      await expect(page.locator(".factor-card")).toHaveCount(0);
      await page.unroute("**/api/analyze");
      await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
      await expect(page.locator(".factor-card")).toHaveCount(6);
    } finally { pending.release(); }
  });
}

for (const first of ["analysis", "comparison"]) {
  test(`comparación paralela: ${first} termina primero y las etapas siguen las respuestas`, async ({ page }) => {
    await analysisA(page);
    await page.getByRole("button", { name: "Comparar otra localidad", exact: true }).click();
    await selectLocality(page, "110070001");
    const analysis = gate(), comparison = gate();
    await holdResponse(page, "**/api/analyze", analysis);
    await holdResponse(page, "**/api/compare", comparison);
    try {
      await page.getByRole("button", { name: "Analizar B y comparar", exact: true }).click();
      const dialog = page.getByRole("dialog", { name: "Comparando localidades…", exact: true });
      await expect(dialog).toBeVisible();
      await expect(dialog.locator(".geo-pulse-step-active")).toHaveCount(2);
      (first === "analysis" ? analysis : comparison).release();
      await expect(dialog.locator(".geo-pulse-step-complete")).toHaveCount(2);
      await expect(dialog.locator(".geo-pulse-step-active")).toHaveCount(1);
      await expect(dialog.locator(".geo-pulse-step-pending")).toContainText("Preparando comparación");
      await dialog.screenshot({ path: `test-results/geo-pulse-comparison-${first}.png` });
      (first === "analysis" ? comparison : analysis).release();
      await expect(dialog).toHaveCount(0);
      await expect(page.getByRole("heading", { name: /Comparación territorial A\/B/ })).toBeVisible();
    } finally { analysis.release(); comparison.release(); }
  });
}

test("fallo de consulta: cierra el modal y muestra un error sin resultados", async ({ page }) => {
  const pending = gate();
  await page.route("**/api/analyze", async route => {
    await pending.promise;
    await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ message: "Consulta no disponible", error: "TEST_UNAVAILABLE" }) });
  });
  try {
    await page.goto("/#/sistema");
    await selectLocality(page, "110170001");
    await page.getByRole("button", { name: "Analizar localidad", exact: true }).click();
    await expect(page.locator(".geo-pulse-dialog")).toBeVisible();
    pending.release();
    await expect(page.locator(".geo-pulse-dialog")).toHaveCount(0);
    await expect(page.getByRole("alert")).toContainText("Consulta no disponible");
    await expect(page.locator(".factor-card")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Analizar localidad", exact: true })).toBeEnabled();
  } finally { pending.release(); }
});

test("mapa: pulso sin etapas durante la carga; ocultarlo cancela la espera visual", async ({ page }) => {
  const pending = gate();
  await page.unroute(tileURL);
  await page.route(tileURL, async route => { await pending.promise; await route.fulfill({ contentType: "image/png", body: tile }); });
  try {
    await page.goto("/#/sistema");
    const loading = page.locator(".geo-pulse-map");
    await expect(loading).toBeVisible();
    await expect(loading.locator(".geo-pulse-steps")).toHaveCount(0);
    await expect(loading).toHaveCSS("pointer-events", "none");
    await loading.screenshot({ path: "test-results/geo-pulse-map.png" });
    await page.getByRole("button", { name: "Ocultar mapa base", exact: true }).click();
    await expect(loading).toHaveCount(0);
    await expect(page.locator(".map-note")).toContainText("Mapa base oculto");
    pending.release();
    await page.getByRole("button", { name: "Mostrar mapa base", exact: true }).click();
    await expect(page.locator(".leaflet-host")).toHaveAttribute("aria-busy", "false");
    await expect(loading).toHaveCount(0);
    await selectLocality(page, "110170001");
    await expect(loading).toHaveCount(0);
  } finally { pending.release(); }
});

test("mapa sin respuesta: termina la espera y el catálogo permanece disponible", async ({ page }) => {
  const pending = gate();
  await page.unroute(tileURL);
  await page.route(tileURL, async route => { await pending.promise; await route.fulfill({ contentType: "image/png", body: tile }); });
  try {
    await page.goto("/#/sistema");
    await expect(page.locator(".geo-pulse-map")).toBeVisible();
    await page.clock.install();
    await page.clock.fastForward(12500);
    await expect(page.locator(".geo-pulse-map")).toHaveCount(0);
    await expect(page.locator(".map-note")).toContainText("Sin mapa base");
    await expect(page.getByLabel("Buscar localidad por nombre o clave")).toBeEnabled();
    await expect(page.getByRole("button", { name: "Mostrar mapa base", exact: true })).toBeVisible();
  } finally { pending.release(); }
});
