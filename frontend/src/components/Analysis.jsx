import React, { useEffect, useRef } from "react";
import {
  ChevronRight,
  FileText,
  MapPin,
  Plus,
  Scale,
  Search,
  ArrowLeft,
  Info,
} from "lucide-react";
import { Badge, Button, FactorIcon, Notice } from "./UI";
import {
  COVERAGE,
  PROJECTS,
  allFactors,
  coreFactors,
  factorName,
  formatValue,
  isMunicipal,
  metadataText,
  summarize,
  temporalLabel,
} from "../utils/presentation.mjs";

export function LocationSummary({ location, project, side, compact = false }) {
  return (
    <div
      className={`location-summary ${side === "B" ? "location-b" : ""} ${compact ? "location-compact" : ""}`}
    >
      <span className={`location-letter letter-${side?.toLowerCase() || "a"}`}>
        {side || <MapPin size={20} />}
      </span>
      <div>
        <small>LOCALIDAD {side || ""}</small>
        <strong>
          {location.label || location.locality || "Sin selección"}
        </strong>
        <span>Municipio {location.municipality || "No documentado"}</span>
      </div>
      <div>
        <small>CVEGEO</small>
        <strong className="code">
          {location.locality_id || location.id || "—"}
        </strong>
      </div>
      {project && (
        <div>
          <small>PROYECTO</small>
          <strong>{PROJECTS[project] || project}</strong>
        </div>
      )}
    </div>
  );
}
export function CoverageSummary({
  coverage,
  title = "Disponibilidad de información",
  compact = false,
}) {
  return (
    <section className={`coverage-block ${compact ? "coverage-compact" : ""}`}>
      <div className="block-heading">
        <h3>{title}</h3>
        <span>{coverage?.expected ?? 0} elementos</span>
      </div>
      <div className="coverage-counts">
        {COVERAGE.map(([key, label, tone]) => (
          <div key={key} className={`coverage-cell coverage-${tone}`}>
            <strong>{coverage?.[key] ?? 0}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
      <small className="coverage-note">
        Conteos de información, no porcentajes de riesgo o seguridad.
      </small>
    </section>
  );
}
export function FactorCard({ factor, onEvidence }) {
  return (
    <article className="factor-card">
      <div className="factor-heading">
        <span className="factor-icon">
          <FactorIcon code={factor.factor} />
        </span>
        <h3>{factorName(factor)}</h3>
      </div>
      <Badge status={factor.status} />
      <div
        className={`factor-value ${factor.value == null ? "value-missing" : ""}`}
      >
        {formatValue(factor.value, factor.unit, factor.factor)}
      </div>
      <p className="factor-temporal">
        {temporalLabel(factor.temporal_context)}
        {factor.temporal_context === "reference_period" &&
        factor.factor === "elevation"
          ? " · 2020"
          : ""}
      </p>
      <p className="factor-detail">
        {factor.explanation?.meaning || factor.explanation?.found}
      </p>
      <button className="evidence-link" onClick={() => onEvidence(factor)}>
        <FileText size={14} />
        Ver evidencia y límites
        <ChevronRight size={15} />
      </button>
    </article>
  );
}
export function ContextSection({ result, onEvidence }) {
  const local = (result.context || []).filter((f) => !isMunicipal(f));
  const municipal = (result.context || []).filter(isMunicipal);
  return (
    <section className="context-section">
      <div className="block-heading">
        <h3>Contexto territorial</h3>
        <span>No es una clasificación de riesgo</span>
      </div>
      <div className="context-grid">
        {local.map((f) => (
          <button
            key={f.factor}
            className="context-card"
            onClick={() => onEvidence(f)}
          >
            <span className="context-card-icon">
              <FactorIcon code={f.factor} size={18} />
            </span>
            <span>
              <strong>{factorName(f)}</strong>
              <b>{formatValue(f.value, f.unit, f.factor)}</b>
              <small>{temporalLabel(f.temporal_context)}</small>
              <Badge status={f.status} />
            </span>
            <ChevronRight size={16} />
          </button>
        ))}
      </div>
      {municipal.length > 0 && (
        <details className="municipal-details">
          <summary>
            <span>
              Indicadores municipales{" "}
              <small>Contexto, no medición del predio</small>
            </span>
            <span>{municipal.length} indicadores</span>
          </summary>
          <Notice>
            Estos valores corresponden al municipio y se repiten en sus
            localidades. No representan el riesgo o las condiciones particulares
            de un predio.
          </Notice>
          <div className="municipal-grid">
            {municipal.map((f) => (
              <button key={f.factor} onClick={() => onEvidence(f)}>
                <strong>{factorName(f)}</strong>
                <span>{formatValue(f.value, f.unit, f.factor)}</span>
                <Badge status={f.status} />
              </button>
            ))}
          </div>
        </details>
      )}
    </section>
  );
}
export function MachineLearningPanel({ ml, compact = false }) {
  const experiment = ml?.experiment;
  if (!ml?.enabled || !experiment) {
    return (
      <Notice>
        Machine Learning no activo. El análisis funciona con la evidencia y los
        criterios publicados.
      </Notice>
    );
  }
  const features = experiment.features.map((feature) => feature.label).join(", ");
  return (
    <section className="ml-panel" aria-label="Aprendizaje automático">
      <div className="block-heading">
        <h2>Aprendizaje automático</h2>
        <span>Experimento de 2014 · no es riesgo actual</span>
      </div>
      <h3>{experiment.name}</h3>
      <dl>
        <dt>Esta localidad</dt>
        <dd>{experiment.locality.recorded_label}</dd>
        <dt>Lectura del modelo</dt>
        <dd>{experiment.locality.reading}</dd>
      </dl>
      {!compact && (
        <>
          <p>{experiment.target_meaning}</p>
          <p>
            {experiment.validation.strategy} {experiment.validation.baseline}
          </p>
          <ul>
            {experiment.validation.holdouts.map((holdout) => (
              <li key={holdout.held_out}>
                Prueba en {holdout.held_out}: precisión{" "}
                {(holdout.precision * 100).toFixed(1)} %,{" "}
                {holdout.true_positives} aciertos y {holdout.false_positives}{" "}
                marcas sin ese daño.
              </li>
            ))}
          </ul>
          <p>Variables usadas: {features}.</p>
          <ul>
            {experiment.limitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
export function AnalysisPanel({
  result,
  revealed,
  onGenerate,
  onEvidence,
  onCompare,
  onNew,
  onReport,
  onBack,
}) {
  const main = coreFactors(result);
  const revealRef = useRef(null);
  useEffect(() => {
    if (!revealed) return;
    revealRef.current?.focus();
  }, [revealed]);
  return (
    <>
      <div className="panel-heading">
        <span className="eyebrow">RESULTADO DEL ANÁLISIS</span>
        <h1>
          Evaluación territorial
          <br />
          <em>preliminar</em>
        </h1>
        <span className="unit-chip">
          <MapPin size={12} />
          Unidad: localidad censal
        </span>
      </div>
      <LocationSummary
        location={result.location}
        project={result.project_type}
      />
      <div className="block-heading">
        <h2>Factores núcleo</h2>
        <span>{main.length} factores · fuente y límites visibles</span>
      </div>
      <div className="factor-grid">
        {main.map((f) => (
          <FactorCard key={f.factor} factor={f} onEvidence={onEvidence} />
        ))}
      </div>
      <CoverageSummary
        coverage={summarize(main)}
        title="Información de los factores núcleo"
        compact
      />
      <div className="predictive-slot">
        {revealed ? (
          <div ref={revealRef} tabIndex={-1} aria-live="polite">
            <MachineLearningPanel ml={result.ml} />
          </div>
        ) : (
          <>
            <p>
              El análisis territorial ya está listo. Genera la lectura
              predictiva solo si quieres verla.
            </p>
            <Button onClick={onGenerate}>Generar predicción</Button>
          </>
        )}
      </div>
      <ContextSection result={result} onEvidence={onEvidence} />
      <details className="more-details">
        <summary>Cobertura total y aspectos a revisar</summary>
        <CoverageSummary
          coverage={result.coverage}
          title="Total de elementos publicados por el motor"
        />
        <h3>Aspectos a revisar</h3>
        <ul>
          {result.review_items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </details>
      <Notice tone="warning">{result.disclaimer}</Notice>
      <div className="panel-actions">
        <Button icon={FileText} variant="outline" onClick={onReport}>
          Ver ficha
        </Button>
        <Button icon={Scale} onClick={onCompare}>
          Comparar otra localidad
        </Button>
        <Button icon={Plus} variant="subtle" onClick={onNew}>
          Nueva selección
        </Button>
      </div>
    </>
  );
}
export function SelectionPanel({
  locations,
  project,
  setProject,
  municipality,
  setMunicipality,
  query,
  setQuery,
  selected,
  onSelect,
  side,
  resultA,
  busy,
  onAnalyze,
  onCancel,
}) {
  const duplicate =
    side === "B" && selected?.id === resultA?.location.locality_id;
  return (
    <>
      <div className="panel-heading">
        <span className="eyebrow">
          {side === "B"
            ? "COMPARACIÓN BAJO LOS MISMOS CRITERIOS"
            : "EXPLORA EL TERRITORIO"}
        </span>
        <h1>{side === "B" ? "Seleccionar ubicación B" : "Nuevo análisis"}</h1>
        <p>
          {side === "B"
            ? "Selecciona otra localidad y contrasta su evidencia con A."
            : "Empieza con una localidad. Conoce lo disponible y lo que falta por validar."}
        </p>
        <span className="unit-chip">
          <MapPin size={12} />
          Unidad de análisis: localidad censal
        </span>
      </div>
      {resultA && side === "B" && (
        <LocationSummary
          location={resultA.location}
          project={project}
          side="A"
          compact
        />
      )}
      {side === "A" && (
        <fieldset className="form-fieldset">
          <legend>Tipo de proyecto</legend>
          <div className="segmented projects">
            {Object.entries(PROJECTS).map(([key, label]) => (
              <button
                key={key}
                className={project === key ? "selected" : ""}
                onClick={() => setProject(key)}
                aria-pressed={project === key}
                disabled={busy}
              >
                <FactorIcon
                  code={key === "road" ? "road_proximity" : "population"}
                  size={17}
                />
                {label}
              </button>
            ))}
          </div>
        </fieldset>
      )}
      <fieldset className="form-fieldset">
        <legend>Municipio</legend>
        <div className="segmented">
          {["Irapuato", "Celaya"].map((m) => (
            <button
              key={m}
              className={municipality === m ? "selected" : ""}
              aria-pressed={municipality === m}
              disabled={busy}
              onClick={() => setMunicipality(m)}
            >
              <MapPin size={16} />
              {m}
            </button>
          ))}
        </div>
      </fieldset>
      <label className="field-label" htmlFor={`search-${side}`}>
        Buscar localidad por nombre o clave
      </label>
      <div className="search-field">
        <Search size={18} />
        <input
          id={`search-${side}`}
          type="search"
          placeholder="Nombre de localidad o CVEGEO"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={busy}
          autoComplete="off"
        />
      </div>
      <div className="results-heading">
        <span>{locations.length} coincidencias</span>
        <small>Nombre · municipio · CVEGEO</small>
      </div>
      <div
        className="locality-list"
        role="group"
        aria-label={`Localidades de ${municipality}`}
      >
        {locations.length ? (
          locations.slice(0, 80).map((r) => (
            <button
              key={r.id}
              disabled={busy}
              className={`locality-option ${selected?.id === r.id ? "is-selected" : ""}`}
              onClick={() => onSelect(r)}
            >
              <MapPin size={16} />
              <span>
                <strong>{r.locality}</strong>
                <small>{r.municipality}</small>
              </span>
              <span className="code">{r.id}</span>
              <ChevronRight size={15} />
            </button>
          ))
        ) : (
          <div className="empty-state">
            <Search size={24} />
            <strong>No encontramos esa localidad</strong>
            <p>
              Prueba otro nombre o su clave CVEGEO. El catálogo solo incluye
              Irapuato y Celaya.
            </p>
          </div>
        )}
      </div>
      {locations.length > 80 && (
        <small className="list-hint">
          Se muestran las primeras 80. Escribe un nombre para acotar la
          búsqueda.
        </small>
      )}
      <div className="map-select-hint">
        <MapPin size={20} />
        <span>
          También puedes elegir un marcador del mapa
          <small>Solo se seleccionan localidades del catálogo publicado.</small>
        </span>
      </div>
      <section className="selected-location">
        <h3>
          {side === "B" ? "Localidad B seleccionada" : "Localidad seleccionada"}
        </h3>
        {selected ? (
          <>
            <LocationSummary location={selected} side={side} compact />
            <div className="coordinates">
              <span>
                Latitud <b>{selected.latitude.toFixed(6)}</b>
              </span>
              <span>
                Longitud <b>{selected.longitude.toFixed(6)}</b>
              </span>
            </div>
          </>
        ) : (
          <p>Selecciona una localidad para continuar.</p>
        )}
      </section>
      {duplicate && (
        <Notice tone="warning">
          A y B corresponden a la misma localidad. Selecciona otra para obtener
          una comparación distinta.
        </Notice>
      )}
      <Button
        className="full-width"
        icon={side === "B" ? Scale : Search}
        loading={busy}
        disabled={!selected || busy || duplicate}
        onClick={onAnalyze}
      >
        {busy
          ? side === "B" ? "Comparando localidades…" : "Analizando localidad…"
          : side === "B"
            ? "Analizar B y comparar"
            : "Analizar localidad"}
      </Button>
      {side === "B" && (
        <Button
          className="full-width"
          variant="outline"
          icon={ArrowLeft}
          onClick={onCancel}
        >
          Cancelar y volver a A
        </Button>
      )}
      <Notice>
        Seleccionar una localidad no convierte sus datos en información del
        predio. Coordenadas recibidas: CRS_UNKNOWN.
      </Notice>
    </>
  );
}
