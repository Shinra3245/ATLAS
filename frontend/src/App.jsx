import React, { useEffect, useRef, useState } from "react";
import { Guide } from "./components/Guide";
import { Header } from "./components/Header";
import { ErrorNotice, Loading, Notice } from "./components/UI";
import { AnalysisPanel, SelectionPanel } from "./components/Analysis";
import { Comparison } from "./components/Comparison";
import { EvidenceDialog } from "./components/EvidenceDialog";
import { TerritoryMap } from "./map/TerritoryMap";
import { Landing } from "./pages/Landing";
import { InformationStates, Methodology, Sources } from "./pages/Information";
import { Report } from "./pages/Report";
import { useCatalog } from "./hooks/useCatalog";
import { api } from "./services/api.mjs";
import { STATUS, asLocation, filterLocations } from "./utils/presentation.mjs";

function currentRoute() {
  return location.hash.startsWith("#/") ? location.hash.slice(1) : "/";
}
function checkAnalysis(result, id) {
  if (
    result.schema_version !== "engine_result/v1" ||
    result.location?.locality_id !== id ||
    ![
      "conditions",
      "territorial_factors",
      "context",
      "sources",
      "limitations",
      "review_items",
    ].every((k) => Array.isArray(result[k]))
  )
    throw new Error(
      "La respuesta no corresponde al contrato o a la localidad seleccionada. No se mostrarán resultados inconsistentes.",
    );
  if (
    ![
      ...result.conditions,
      ...result.territorial_factors,
      ...result.context,
    ].every(
      (f) =>
        STATUS[f.status] &&
        (f.value == null ||
          ["string", "number", "boolean"].includes(typeof f.value)),
    )
  )
    throw new Error(
      "El análisis contiene un estado o un valor no publicado por el contrato.",
    );
  return result;
}
export default function App() {
  const catalog = useCatalog();
  const [route, setRoute] = useState(currentRoute);
  const [phase, setPhase] = useState("selectA");
  const [project, setProject] = useState("housing");
  const [municipality, setMunicipality] = useState("Irapuato");
  const [query, setQuery] = useState("");
  const [selectedA, setSelectedA] = useState(null);
  const [selectedB, setSelectedB] = useState(null);
  const [resultA, setResultA] = useState(null);
  const [resultB, setResultB] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [evidence, setEvidence] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    function update() {
      const next = currentRoute();
      setRoute((old) => {
        if (next !== old) window.scrollTo({ top: 0 });
        return next;
      });
    }
    window.addEventListener("hashchange", update);
    return () => {
      window.removeEventListener("hashchange", update);
      controllerRef.current?.abort();
    };
  }, []);
  useEffect(() => {
    document.title =
      route === "/"
        ? "ATLAS · Evidencia para decidir"
        : "ATLAS · Evaluación territorial preliminar";
  }, [route]);

  function cancelRequest() {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setBusy(false);
    setError(null);
  }
  function newSelection() {
    cancelRequest();
    setPhase("selectA");
    setSelectedA(null);
    setSelectedB(null);
    setResultA(null);
    setResultB(null);
    setComparison(null);
    setQuery("");
  }
  function select(record) {
    if (busy) return;
    setMunicipality(record.municipality);
    if (phase === "selectB") setSelectedB(record);
    else if (phase === "selectA") setSelectedA(record);
  }
  function changeMunicipality(value) {
    setMunicipality(value);
    setQuery("");
    if (phase === "selectB") setSelectedB(null);
    else setSelectedA(null);
  }
  function beginCompare() {
    cancelRequest();
    setPhase("selectB");
    setSelectedB(null);
    setResultB(null);
    setComparison(null);
    setMunicipality("Celaya");
    setQuery("");
  }
  function backToA() {
    cancelRequest();
    setPhase("result");
  }
  function showEvidence(factor, loc = resultA?.location) {
    setEvidence({ factor, location: loc });
  }
  function openReport(side = "a") {
    location.hash = `/ficha/${side}`;
  }

  async function analyze() {
    cancelRequest();
    const controller = new AbortController();
    controllerRef.current = controller;
    setBusy(true);
    try {
      if (phase === "selectB") {
        if (!selectedB || selectedB.id === selectedA?.id)
          throw new Error("Selecciona una localidad distinta de A.");
        const [b, pair] = await Promise.all([
          api.analyze(asLocation(selectedB), project, controller.signal),
          api.compare(
            asLocation(selectedA),
            asLocation(selectedB),
            project,
            controller.signal,
          ),
        ]);
        checkAnalysis(b, selectedB.id);
        if (
          pair.schema_version !== "engine_result/v1" ||
          !Array.isArray(pair.factors) ||
          pair.location_a?.locality_id !== selectedA.id ||
          pair.location_b?.locality_id !== selectedB.id ||
          pair.same_locality
        )
          throw new Error(
            "La comparación no corresponde a las dos localidades seleccionadas.",
          );
        if (controllerRef.current !== controller || controller.signal.aborted)
          return;
        setResultB(b);
        setComparison(pair);
        setPhase("comparison");
      } else {
        const a = checkAnalysis(
          await api.analyze(asLocation(selectedA), project, controller.signal),
          selectedA.id,
        );
        if (controllerRef.current !== controller || controller.signal.aborted)
          return;
        setResultA(a);
        setPhase("result");
      }
      document.querySelector(".workspace-panel")?.scrollTo({ top: 0 });
    } catch (e) {
      if (!controller.signal.aborted && controllerRef.current === controller)
        setError(e.message);
    } finally {
      if (controllerRef.current === controller) {
        controllerRef.current = null;
        setBusy(false);
      }
    }
  }

  const filtered = filterLocations(catalog.locations, municipality, query);
  const isSystem = route !== "/";
  let content;
  if (route === "/") content = <Landing catalog={catalog} />;
  else if (route === "/metodologia") content = <Methodology />;
  else if (route === "/fuentes") content = <Sources catalog={catalog} />;
  else if (route === "/estados") content = <InformationStates />;
  else if (route.startsWith("/ficha/"))
    content = (
      <Report
        result={route.endsWith("/b") ? resultB : resultA}
        sources={catalog.sources}
        onBack={() => {
          location.hash = "/sistema";
        }}
      />
    );
  else if (route === "/sistema")
    content = (
      <main id="main-content" className={`workspace workspace-${phase}`}>
        <section className="workspace-map">
          <TerritoryMap
            locations={catalog.locations}
            selectedA={selectedA}
            selectedB={
              phase === "comparison" || phase === "selectB" ? selectedB : null
            }
            onSelect={
              phase === "selectA" || phase === "selectB" ? select : undefined
            }
            municipality={
              phase === "selectA" || phase === "selectB"
                ? municipality
                : undefined
            }
          />
          <div className="workspace-map-footer">
            <span>
              <span className="status-dot" />
              {catalog.locations.length} localidades publicadas
            </span>
            <a href="#/fuentes">Fuentes y cobertura ↗</a>
          </div>
        </section>
        <section
          className="workspace-panel"
          aria-label="Panel de evaluación territorial"
          aria-busy={busy}
        >
          {catalog.loading ? (
            <Loading text="Cargando localidades y fuentes del nodo…" />
          ) : catalog.error ? (
            <ErrorNotice error={catalog.error} retry={catalog.retry} />
          ) : (
            <>
              {error && <ErrorNotice error={error} retry={analyze} />}
              {busy && (
                <Loading
                  text={
                    phase === "selectB"
                      ? "Analizando B y comparando los mismos criterios…"
                      : "Consultando evidencia para la localidad seleccionada…"
                  }
                />
              )}
              {(phase === "selectA" || phase === "selectB") && (
                <SelectionPanel
                  locations={filtered}
                  project={project}
                  setProject={setProject}
                  municipality={municipality}
                  setMunicipality={changeMunicipality}
                  query={query}
                  setQuery={setQuery}
                  selected={phase === "selectB" ? selectedB : selectedA}
                  onSelect={select}
                  side={phase === "selectB" ? "B" : "A"}
                  resultA={resultA}
                  busy={busy}
                  onAnalyze={analyze}
                  onCancel={backToA}
                />
              )}
              {phase === "result" && resultA && (
                <AnalysisPanel
                  result={resultA}
                  onEvidence={showEvidence}
                  onCompare={beginCompare}
                  onNew={newSelection}
                  onReport={() => openReport("a")}
                />
              )}
              {phase === "comparison" && comparison && (
                <Comparison
                  comparison={comparison}
                  resultA={resultA}
                  resultB={resultB}
                  onBack={backToA}
                  onChangeB={beginCompare}
                  onReport={openReport}
                  onEvidence={showEvidence}
                />
              )}
            </>
          )}
        </section>
      </main>
    );
  else
    content = (
      <main id="main-content" className="information-page container">
        <h1>Esta vista no existe</h1>
        <p>Vuelve a la selección de una localidad.</p>
        <a className="button button-primary" href="#/sistema">
          Abrir ATLAS
        </a>
      </main>
    );
  return (
    <>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          const main = document.getElementById("main-content");
          if (main) {
            main.tabIndex = -1;
            main.focus();
            main.scrollIntoView({ block: "start" });
          }
        }}
      >
        Saltar al contenido
      </a>
      {isSystem && <Header system />}
      {content}
      {evidence && (
        <EvidenceDialog
          evidence={evidence}
          catalogSources={catalog.sources}
          onClose={() => setEvidence(null)}
        />
      )}
      <Guide
        route={route}
        phase={phase}
        busy={busy}
        error={error}
        selected={
          phase === "selectB"
            ? Boolean(selectedB && selectedB.id !== selectedA?.id)
            : Boolean(selectedA)
        }
        catalogLoading={catalog.loading}
        catalogError={catalog.error}
      />
    </>
  );
}
