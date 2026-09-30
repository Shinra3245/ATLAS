import React, { useEffect, useRef, useState } from "react";
import { Guide } from "./components/Guide";
import { Tour } from "./components/Tour";
import { Header } from "./components/Header";
import { ErrorNotice, Loading, Notice } from "./components/UI";
import { AnalysisPanel, SelectionPanel } from "./components/Analysis";
import { Comparison } from "./components/Comparison";
import { EvidenceDialog } from "./components/EvidenceDialog";
import { LoadingDialog } from "./components/LoadingDialog";
import { PlanGate } from "./components/PlanGate";
import { TerritoryMap } from "./map/TerritoryMap";
import { Landing } from "./pages/Landing";
import { Access } from "./pages/Access";
import { Plans } from "./pages/Plans";
import { useAccount } from "./hooks/useAccount";
import { InformationStates, Methodology, Sources } from "./pages/Information";
import { Report } from "./pages/Report";
import { useCatalog } from "./hooks/useCatalog";
import { api } from "./services/api.mjs";
import { STATUS, asLocation, filterLocations } from "./utils/presentation.mjs";
import { analysisLimit, canAnalyze, canCompare } from "./plans.mjs";

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
  const account = useAccount();
  const [route, setRoute] = useState(currentRoute);
  const [phase, setPhase] = useState("selectA");
  const [project, setProject] = useState("housing");
  const [municipality, setMunicipality] = useState("Irapuato");
  const [mapZone, setMapZone] = useState(null);
  const [query, setQuery] = useState("");
  const [selectedA, setSelectedA] = useState(null);
  const [selectedB, setSelectedB] = useState(null);
  const [resultA, setResultA] = useState(null);
  const [resultB, setResultB] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [busy, setBusy] = useState(false);
  const [completedQueries, setCompletedQueries] = useState({ analysis: false, comparison: false });
  const [error, setError] = useState(null);
  const [evidence, setEvidence] = useState(null);
  const [predictive, setPredictive] = useState(false);
  const [planGate, setPlanGate] = useState(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    function update() {
      const next = currentRoute();
      if (next !== "/sistema") {
        controllerRef.current?.abort();
        controllerRef.current = null;
        setBusy(false);
      }
      setRoute((old) => {
        if (next !== old && location.hash.startsWith("#/"))
          window.scrollTo({ top: 0, behavior: "instant" });
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
    if (route === "/sistema" && account.authReady && !account.user) {
      location.hash = "/acceso";
    }
    if (route !== "/sistema") setPlanGate(null);
  }, [route, account.authReady, account.user]);
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
    setPredictive(false);
    setQuery("");
    setMapZone(null);
  }
  function select(record) {
    if (busy) return;
    setMunicipality(record.municipality);
    setMapZone(record.municipality);
    if (phase === "selectB") setSelectedB(record);
    else if (phase === "selectA") setSelectedA(record);
  }
  function changeMunicipality(value) {
    setMunicipality(value);
    setMapZone(value);
    setQuery("");
    if (phase === "selectB") setSelectedB(null);
    else setSelectedA(null);
  }
  function beginCompare() {
    if (!canCompare(account.role)) {
      setPlanGate("compare");
      return;
    }
    cancelRequest();
    setPhase("selectB");
    setSelectedB(null);
    setResultB(null);
    setComparison(null);
    setMunicipality("Celaya");
    setMapZone("Celaya");
    setQuery("");
  }
  function chooseZone(name) {
    if (!name) {
      setMapZone(null);
      return;
    }
    if (phase === "selectA" || phase === "selectB") {
      if (!busy) changeMunicipality(name);
      return;
    }
    setMapZone(name);
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
    if (phase !== "selectB" && !canAnalyze(account.role, account.usage)) {
      setPlanGate("quota");
      return;
    }
    cancelRequest();
    const controller = new AbortController();
    controllerRef.current = controller;
    setCompletedQueries({ analysis: false, comparison: false });
    setBusy(true);
    function markComplete(key) {
      if (controllerRef.current === controller && !controller.signal.aborted)
        setCompletedQueries(previous => ({ ...previous, [key]: true }));
    }
    try {
      if (phase === "selectB") {
        if (!selectedB || selectedB.id === selectedA?.id)
          throw new Error("Selecciona una localidad distinta de A.");
        const [b, pair] = await Promise.all([
          api.analyze(asLocation(selectedB), project, controller.signal).then(result => {
            const valid = checkAnalysis(result, selectedB.id);
            markComplete("analysis");
            return valid;
          }),
          api.compare(
            asLocation(selectedA),
            asLocation(selectedB),
            project,
            controller.signal,
          ).then(pair => {
            if (
              pair.schema_version !== "engine_result/v1" ||
              !Array.isArray(pair.factors) ||
              pair.location_a?.locality_id !== selectedA.id ||
              pair.location_b?.locality_id !== selectedB.id ||
              pair.same_locality
            )
              throw new Error("La comparación no corresponde a las dos localidades seleccionadas.");
            markComplete("comparison");
            return pair;
          }),
        ]);
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
        markComplete("analysis");
        if (controllerRef.current !== controller || controller.signal.aborted)
          return;
        setResultA(a);
        setPredictive(false);
        setPhase("result");
        if (analysisLimit(account.role) != null) await account.consume();
      }
      document.querySelector(".workspace-panel")?.scrollTo({ top: 0 });
    } catch (e) {
      if (!controller.signal.aborted && controllerRef.current === controller) {
        setError(e.message);
        controller.abort();
      }
    } finally {
      if (controllerRef.current === controller) {
        controllerRef.current = null;
        setBusy(false);
      }
    }
  }

  const filtered = filterLocations(catalog.locations, municipality, query);
  const isSystem = route !== "/";
  const comparing = phase === "selectB";
  const querySteps = [
    { id: "locality", label: comparing ? "Localidad B seleccionada" : "Localidad seleccionada", status: "complete" },
    { id: "analysis", label: comparing ? "Consultando factores y evidencia de B" : "Consultando factores y evidencia", status: completedQueries.analysis ? "complete" : "active" },
    ...(comparing ? [{ id: "comparison", label: "Comparando localidades A y B", status: completedQueries.comparison ? "complete" : "active" }] : []),
    { id: "presentation", label: comparing ? "Preparando comparación" : "Preparando evaluación preliminar", status: "pending" },
  ];
  let content;
  if (route === "/") content = <Landing catalog={catalog} />;
  else if (route === "/metodologia") content = <Methodology />;
  else if (route === "/fuentes") content = <Sources catalog={catalog} />;
  else if (route === "/estados") content = <InformationStates />;
  else if (route === "/acceso" || route === "/registro")
    content = <Access key={route} mode={route === "/registro" ? "register" : "login"} />;
  else if (route === "/planes") content = <Plans />;
  else if (route.startsWith("/ficha/"))
    content = (
      <Report
        result={route.endsWith("/b") ? resultB : resultA}
        sources={catalog.sources}
        showPredictive={predictive}
        onBack={() => {
          location.hash = "/sistema";
        }}
      />
    );
  else if (route === "/sistema" && (!account.authReady || !account.user))
    content = (
      <main id="main-content" className="information-page container">
        <p>Revisando la cuenta…</p>
      </main>
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
            focusedMunicipality={
              phase === "result" || phase === "comparison"
                ? mapZone || selectedA?.municipality || null
                : mapZone
            }
            onChooseZone={chooseZone}
          />
          <div className="workspace-map-footer">
            <span>
              <span className="status-dot" />
              {catalog.loading ? "Consultando catálogo…" : `${catalog.locations.length} localidades publicadas`}
            </span>
            <a href="#/fuentes">Fuentes y cobertura ↗</a>
          </div>
        </section>
        <section
          className="workspace-panel"
          aria-label="Panel de evaluación territorial"
          aria-busy={busy || catalog.loading}
          tabIndex={-1}
        >
          {catalog.loading ? (
            <Loading text="Cargando localidades…" detail="Consultando localidades y fuentes disponibles." />
          ) : catalog.error ? (
            <ErrorNotice error={catalog.error} retry={catalog.retry} />
          ) : (
            <>
              {error && <ErrorNotice error={error} retry={analyze} />}
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
                  revealed={predictive}
                  onGenerate={() => setPredictive(true)}
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
                  revealed={predictive}
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
      {isSystem && (
        <Header
          context={route === "/sistema" ? "workspace" : route === "/acceso" || route === "/registro" ? "auth" : "inner"}
        />
      )}
      {content}
      {planGate && <PlanGate reason={planGate} onClose={() => setPlanGate(null)} />}
      <LoadingDialog
        active={busy && route === "/sistema"}
        title={comparing ? "Comparando localidades…" : "Analizando localidad…"}
        detail={comparing && completedQueries.analysis ? "Contrastando los mismos criterios entre A y B…" : "Consultando información territorial y evidencia disponible…"}
        steps={querySteps}
        onCancel={cancelRequest}
      />
      {evidence && (
        <EvidenceDialog
          evidence={evidence}
          catalogSources={catalog.sources}
          onClose={() => setEvidence(null)}
        />
      )}
      {route !== "/acceso" && route !== "/registro" && <Guide
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
        municipality={municipality}
        project={project}
        localityA={selectedA?.label || ""}
        localityB={selectedB?.label || ""}
        resultA={resultA}
        resultB={resultB}
      />}
      <Tour route={route} account={account} />
    </>
  );
}
