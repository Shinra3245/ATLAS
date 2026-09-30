import { test, expect } from "@playwright/test";

async function chooseA(page, projectLabel) {
  await page.goto("/#/sistema");
  if (projectLabel)
    await page
      .locator(".projects")
      .getByRole("button", { name: projectLabel, exact: true })
      .click();
  await page
    .getByLabel("Buscar localidad por nombre o clave")
    .fill("110170001");
  await page
    .locator(".locality-option")
    .filter({ hasText: "110170001" })
    .click();
  await page
    .getByRole("button", { name: "Analizar localidad", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: /Evaluación territorial preliminar/ }),
  ).toBeVisible();
}
test("logo y nombre del mockup aparecen en todas las vistas", async ({
  page,
  request,
}) => {
  for (const route of [
    "/",
    "/#/sistema",
    "/#/metodologia",
    "/#/fuentes",
    "/#/estados",
  ]) {
    await page.goto(route);
    const brand = page.locator(".site-header .brand");
    await expect(brand).toBeVisible();
    await expect(brand.locator(".brand-mark")).toHaveAttribute(
      "src",
      "/atlas-logo.png",
    );
    await expect(brand.locator(".brand-wordmark")).toHaveAttribute(
      "src",
      "/atlas-name.png",
    );
    await expect
      .poll(() =>
        brand.locator("img").evaluateAll((images) =>
          images.every((image) => image.complete && image.naturalWidth > 0),
        ),
      )
      .toBe(true);
  }
  await page.goto("/#/loaders");
  await expect(page.locator(".lp-header .brand-mark")).toBeVisible();
  await expect(page.locator(".lp-header .brand-wordmark")).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator(".lp-header .brand-wordmark")).toHaveCSS(
    "width",
    "145px",
  );
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  ).toBe(true);
  await page.setViewportSize({ width: 1280, height: 720 });
  await chooseA(page);
  await page.getByRole("button", { name: "Ver ficha", exact: true }).click();
  await expect(page.locator(".report-head .brand-mark")).toHaveCount(3);
  await expect(page.locator(".report-head .brand-wordmark")).toHaveCount(3);
  expect((await request.get("/atlas-logo.png")).status()).toBe(200);
  expect((await request.get("/atlas-name.png")).status()).toBe(200);
});
test("landing, navegación y diseño de escritorio sin errores de ejecución", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Evalúa y compara/ }),
  ).toBeVisible();
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({
    path: "test-results/desktop-landing.png",
    fullPage: true,
  });
  await page
    .getByRole("link", { name: "Explorar ATLAS", exact: false })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Nuevo análisis" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Analizar localidad", exact: true }),
  ).toBeDisabled();
  expect(errors).toEqual([]);
  await page.screenshot({
    path: "test-results/desktop-selection.png",
    fullPage: true,
  });
});
test("flujo real A → evidencia → ficha → B → comparación", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await chooseA(page);
  const elevation = page.locator(".factor-card").filter({
    has: page.getByRole("heading", { name: "Altitud censal", exact: true }),
  });
  await expect(elevation).toContainText("1,715 m");
  await elevation
    .getByRole("button", { name: "Ver evidencia y límites" })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await expect(page.getByRole("dialog")).toContainText("Qué no significa");
  await expect(page.getByRole("dialog")).toContainText(
    "resultados por localidad del Censo 2020 de INEGI",
  );
  await expect(page.getByRole("dialog")).not.toContainText(".xlsx");
  await page.screenshot({ path: "test-results/evidence.png", fullPage: true });
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.screenshot({
    path: "test-results/desktop-analysis.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Ver ficha", exact: true }).click();
  await expect(page.locator(".report-page")).toHaveCount(3);
  await expect(page.locator(".report-page").first()).toContainText("110170001");
  await expect(page.locator(".report-document")).not.toContainText(
    "[analysis_id]",
  );
  await expect(page.locator(".report-document")).not.toContainText(".xlsx");
  await expect(page.locator(".report-document")).not.toContainText(
    "core_geospatial",
  );
  await expect(page.locator(".report-document")).not.toContainText(
    "SOURCE_PROVENANCE_PARTIAL",
  );
  await expect(page.locator(".source-report-table")).toContainText(
    "Institución original no documentada",
  );
  await page.screenshot({ path: "test-results/report.png", fullPage: true });
  await page.pdf({
    path: "test-results/ficha-browser.pdf",
    printBackground: true,
    preferCSSPageSize: true,
  });
  await page.getByRole("button", { name: "Volver al análisis" }).click();
  await page.getByRole("button", { name: "Comparar otra localidad" }).click();
  await page
    .getByLabel("Buscar localidad por nombre o clave")
    .fill("110070001");
  await page
    .locator(".locality-option")
    .filter({ hasText: "110070001" })
    .click();
  await page.getByRole("button", { name: "Analizar B y comparar" }).click();
  await expect(
    page.getByRole("heading", { name: /Comparación territorial A\/B/ }),
  ).toBeVisible();
  const slope = page
    .locator(".comparison-table tbody tr")
    .filter({
      has: page.getByRole("rowheader", { name: /Pendiente del terreno/ }),
    })
    .first();
  await expect(slope).toContainText("Pendiente de validación");
  await expect(slope).not.toContainText("1.8");
  await expect(page.locator(".comparison-table").first()).toContainText(
    "1,759 m",
  );
  await page.screenshot({
    path: "test-results/desktop-comparison.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
for (const projectLabel of ["Edificación", "Carretera / vialidad"]) {
  test(`recorrido A/B y ficha para ${projectLabel}`, async ({ page }) => {
    await chooseA(page, projectLabel);
    await expect(page.locator(".location-summary").first()).toContainText(
      projectLabel,
    );
    await page.getByRole("button", { name: "Ver ficha", exact: true }).click();
    await expect(page.locator(".report-identification")).toContainText(
      projectLabel,
    );
    await page.getByRole("button", { name: "Volver al análisis" }).click();
    await page.getByRole("button", { name: "Comparar otra localidad" }).click();
    await page
      .getByLabel("Buscar localidad por nombre o clave")
      .fill("110070001");
    await page
      .locator(".locality-option")
      .filter({ hasText: "110070001" })
      .click();
    await page.getByRole("button", { name: "Analizar B y comparar" }).click();
    await expect(page.locator(".comparison-locations")).toContainText(
      projectLabel,
    );
    await expect(page.locator(".panel-heading")).toContainText(
      "SIN GANADOR AUTOMÁTICO",
    );
  });
}
test("bloqueo de la misma localidad A/B y recuperación de búsqueda vacía", async ({
  page,
}) => {
  await chooseA(page);
  await page.getByRole("button", { name: "Comparar otra localidad" }).click();
  await page.getByRole("button", { name: "Irapuato", exact: true }).click();
  await page
    .getByLabel("Buscar localidad por nombre o clave")
    .fill("110170001");
  await page
    .locator(".locality-option")
    .filter({ hasText: "110170001" })
    .click();
  await expect(
    page.getByRole("button", { name: "Analizar B y comparar" }),
  ).toBeDisabled();
  await expect(page.locator(".notice-warning")).toContainText(
    "misma localidad",
  );
  await page
    .getByLabel("Buscar localidad por nombre o clave")
    .fill("localidad inexistente");
  await expect(page.getByText("No encontramos esa localidad")).toBeVisible();
  await page.getByRole("button", { name: "Cancelar y volver a A" }).click();
  await expect(
    page.getByRole("heading", { name: /Evaluación territorial preliminar/ }),
  ).toBeVisible();
});
test("móvil: landing y análisis sin desbordamiento horizontal", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.locator(".guide-bubble-prompt")).toBeHidden();
  await page.getByRole("button", { name: "Mostrar la explicación" }).click();
  await expect(page.locator(".guide-bubble")).toContainText(
    "Empieza en Explorar ATLAS",
  );
  await page.getByRole("button", { name: "Ocultar la explicación" }).click();
  await expect(page.locator(".guide-bubble-prompt")).toBeHidden();
  await page.screenshot({
    path: "test-results/mobile-landing.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Abrir menú" }).click();
  await expect(
    page.getByRole("navigation", { name: "Navegación principal" }),
  ).toBeVisible();
  await chooseA(page);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/mobile-analysis.png",
    fullPage: true,
  });
});
test("fuentes y seis estados de información", async ({ page }) => {
  await page.goto("/#/fuentes");
  await expect(page.locator(".source-card").first()).toBeVisible();
  await expect(page.locator(".sources-grid")).not.toContainText(".xlsx");
  await expect(page.locator(".sources-grid")).not.toContainText(
    "SOURCE_PROVENANCE_PARTIAL",
  );
  await page.getByLabel("Buscar fuente").fill("core_geospatial");
  await expect(page.locator(".source-card")).toHaveCount(1);
  await page.goto("/#/estados");
  await expect(page.locator(".state-card")).toHaveCount(6);
  await expect(
    page.getByRole("heading", {
      name: "Sin condición registrada",
      exact: true,
    }),
  ).toBeVisible();
});
test("error de API explícito, sin resultados simulados", async ({ page }) => {
  await page.route("**/api/locations", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: "API_UNAVAILABLE",
        message: "API no disponible para esta prueba",
      }),
    }),
  );
  await page.goto("/#/sistema");
  await expect(page.getByRole("alert")).toContainText("API no disponible");
  await expect(page.locator(".factor-card")).toHaveCount(0);
});
test("sin mapa externo el catálogo mantiene operativo el flujo", async ({
  page,
}) => {
  await page.route("https://tile.openstreetmap.org/**", (route) =>
    route.abort(),
  );
  await chooseA(page);
  await expect(
    page.getByText(
      "Sin mapa base. El catálogo y la selección siguen disponibles.",
    ),
  ).toBeVisible();
  await expect(page.locator(".factor-card")).toHaveCount(6);
});

for (const width of [320, 768, 1024, 1920]) {
  test(`responsive ${width}px: landing, sistema y ficha`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /Evalúa y compara/ }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    ).toBe(true);
    await chooseA(page);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    ).toBe(true);
    await page.getByRole("button", { name: "Ver ficha", exact: true }).click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    ).toBe(true);
    await expect(page.locator(".report-page-footer")).toHaveCount(3);
  });
}

test("preview: no expone archivos privados ni acepta operaciones ajenas", async ({
  request,
}) => {
  expect((await request.get("/.env")).status()).toBe(403);
  expect((await request.get("/src/App.jsx")).status()).toBe(404);
  expect((await request.get("/api/private")).status()).toBe(404);
  expect((await request.post("/api/health", { data: {} })).status()).toBe(405);
  expect(
    (
      await request.post("/api/analyze", {
        headers: { Origin: "http://example.invalid" },
        data: {},
      })
    ).status(),
  ).toBe(403);
});

test("navegación por teclado: saltar al contenido no cambia la vista", async ({
  page,
}) => {
  await page.goto("/#/sistema");
  await expect(
    page.getByRole("heading", { name: "Nuevo análisis" }),
  ).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Saltar al contenido" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
  await expect(page).toHaveURL(/#\/sistema$/);
});
