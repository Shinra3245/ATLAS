import React, { useState } from "react";
import { ArrowLeft, FileText, Printer, Info } from "lucide-react";
import { Badge, Button, Logo, Notice } from "../components/UI";
import { CoverageSummary } from "../components/Analysis";
import {
  PROJECTS,
  coreFactors,
  factorName,
  formatValue,
  isMunicipal,
  publicTechnicalText,
  sourceCoverageText,
  sourceDateText,
  sourceDisplayName,
  sourceInstitutionText,
  sourceVerificationText,
  temporalLabel,
  validExternalUrl,
} from "../utils/presentation.mjs";

function ReportHead() {
  return (
    <>
      <header className="report-head">
        <Logo />
        <div>
          <strong>REPORTE PRELIMINAR</strong>
          <small>RESULTADOS CON EVIDENCIA Y LIMITACIONES</small>
        </div>
      </header>
    </>
  );
}
function ReportFooter({ page }) {
  return (
    <footer className="report-page-footer">
      <Info size={13} />
      <span>
        Evaluación preliminar; no sustituye estudios técnicos, permisos ni
        dictámenes.
      </span>
      <strong>{String(page).padStart(2, "0")}</strong>
    </footer>
  );
}
export function Report({ result, sources, onBack }) {
  const [issuedAt] = useState(() =>
    new Date().toLocaleString("es-MX", {
      dateStyle: "medium",
      timeStyle: "short",
    }),
  );
  if (!result)
    return (
      <main id="main-content" className="information-page container">
        <h1>Primero consulta una localidad</h1>
        <p>
          La ficha se genera a partir de un análisis real. No se utilizarán
          resultados simulados.
        </p>
        <a href="#/sistema" className="button button-primary">
          Abrir el sistema
        </a>
      </main>
    );
  const core = coreFactors(result);
  const context = result.context.filter((f) =>
    [
      "population",
      "road_proximity",
      "hydrography_proximity",
      "services_coverage",
    ].includes(f.factor),
  );
  const municipal = result.context.filter(isMunicipal);
  const location = result.location;
  return (
    <main id="main-content" className="report-view">
      <div className="report-toolbar">
        <Button icon={ArrowLeft} variant="outline" onClick={onBack}>
          Volver al análisis
        </Button>
        <div>
          <span>Ficha preliminar · {location.label}</span>
          <Button icon={Printer} onClick={() => window.print()}>
            Imprimir / guardar PDF
          </Button>
        </div>
      </div>
      <div className="report-document">
        <article className="report-page report-page-1">
          <ReportHead />
          <span className="eyebrow">RESULTADO DEL ANÁLISIS</span>
          <h1>
            Ficha de evaluación
            <br />
            <em>territorial preliminar</em>
          </h1>
          <p className="report-subtitle">
            Localidad {location.label} · Municipio {location.municipality},
            Guanajuato
          </p>
          <span className="unit-chip">
            Unidad de análisis: localidad censal
          </span>
          <section className="report-section">
            <h2>Identificación de la localidad y del análisis</h2>
            <dl className="report-identification">
              <dt>Tipo de proyecto</dt>
              <dd>{PROJECTS[result.project_type]}</dd>
              <dt>CVEGEO</dt>
              <dd>{location.locality_id}</dd>
              <dt>Coordenadas de referencia</dt>
              <dd>
                {location.lat.toFixed(6)}, {location.lon.toFixed(6)}
              </dd>
              <dt>Referencia espacial</dt>
              <dd>Sistema de coordenadas pendiente de verificación</dd>
              <dt>Identificador del análisis</dt>
              <dd>{result.analysis_id}</dd>
              <dt>Versión del motor</dt>
              <dd>{result.engine_version}</dd>
              <dt>Versión del esquema</dt>
              <dd>{result.schema_version}</dd>
              <dt>Fecha de emisión de esta ficha</dt>
              <dd>{issuedAt}</dd>
            </dl>
            <p className="report-small-note">
              La fecha de emisión no es la fecha de los datos. Las coordenadas
              son referencias recibidas, no una medición del predio.
            </p>
          </section>
          <section className="report-executive">
            <FileText size={26} />
            <div>
              <h2>Resumen ejecutivo</h2>
              <p>
                Esta ficha presenta los datos disponibles, sus limitaciones y
                los aspectos que requieren revisión para la localidad
                seleccionada. No determina la viabilidad definitiva del proyecto
                ni declara una ubicación como segura.
              </p>
            </div>
          </section>
          <section className="report-section">
            <h2>Síntesis de los factores núcleo</h2>
            <div className="report-synthesis">
              {core.map((f) => (
                <div key={f.factor}>
                  <strong>{factorName(f)}</strong>
                  <span>{formatValue(f.value, f.unit, f.factor)}</span>
                  <Badge status={f.status} />
                </div>
              ))}
            </div>
          </section>
          <Notice>{result.disclaimer}</Notice>
          <ReportFooter page={1} />
        </article>
        <article className="report-page report-page-detail">
          <ReportHead />
          <span className="eyebrow">DETALLE DEL RESULTADO</span>
          <h1>
            Factores, antecedentes
            <br /> <em>y contexto</em>
          </h1>
          <p className="report-subtitle">
            {location.label} · CVEGEO {location.locality_id} ·{" "}
            {PROJECTS[result.project_type]}
          </p>
          <section className="report-section">
            <h2>1. Factores núcleo</h2>
            <table className="report-table report-core-table">
              <thead>
                <tr>
                  <th>Factor</th>
                  <th>Valor, estado y temporalidad</th>
                  <th>Fuente y limitación</th>
                </tr>
              </thead>
              <tbody>
                {core.map((f) => (
                  <tr key={f.factor}>
                    <th scope="row">{factorName(f)}</th>
                    <td>
                      {formatValue(f.value, f.unit, f.factor)}
                      <Badge status={f.status} />
                      <small>{temporalLabel(f.temporal_context)}</small>
                    </td>
                    <td>
                      {sourceDisplayName(f.source)}
                      <small>{f.explanation.limitation}</small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <section className="report-section">
            <h2>2. Contexto territorial disponible</h2>
            <table className="report-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th>Valor y estado</th>
                  <th>Temporalidad</th>
                </tr>
              </thead>
              <tbody>
                {context.map((f) => (
                  <tr key={f.factor}>
                    <th scope="row">{factorName(f)}</th>
                    <td>
                      {formatValue(f.value, f.unit, f.factor)}
                      <Badge status={f.status} />
                    </td>
                    <td>{temporalLabel(f.temporal_context)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="report-small-note">
              Esta ficha incluye una selección del contexto; el detalle completo
              se consulta en el sistema. Las proximidades son distancias
              precalculadas. No certifican accesibilidad, rutas transitables ni
              capacidad de servicios. Los datos censales describen un período de
              referencia, no una observación actual.
            </p>
          </section>
          {municipal.length > 0 && (
            <Notice>
              El análisis también incluye {municipal.length} indicadores de
              contexto municipal, consultables en el sistema. No son mediciones
              de la localidad ni del predio y no se interpretan como un riesgo
              local.
            </Notice>
          )}
          <ReportFooter page={2} />
        </article>
        <article className="report-page report-page-detail">
          <ReportHead />
          <span className="eyebrow">RESPALDO Y PRÓXIMOS PASOS</span>
          <h1>
            Cobertura, fuentes
            <br /> <em>y aspectos a revisar</em>
          </h1>
          <p className="report-subtitle">
            Localidad {location.label} · {PROJECTS[result.project_type]}
          </p>
          <CoverageSummary
            coverage={result.coverage}
            title="1. Disponibilidad total de información"
          />
          <section className="report-section">
            <h2>2. Aspectos a revisar</h2>
            <ul className="report-review">
              {result.review_items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>
          <section className="report-section">
            <h2>3. Fuentes utilizadas y trazabilidad</h2>
            <table className="report-table source-report-table">
              <thead>
                <tr>
                  <th>Información consultada</th>
                  <th>Institución declarada y fecha</th>
                  <th>Cobertura y procedencia</th>
                </tr>
              </thead>
              <tbody>
                {result.sources.map((source) => {
                  const catalog = sources.find((s) => s.id === source.id);
                  const url = validExternalUrl(catalog?.original_url);
                  return (
                    <tr key={source.id}>
                      <td>
                        <strong>{sourceDisplayName(source)}</strong>
                      </td>
                      <td>
                        {sourceInstitutionText(source)}
                        <small>{sourceDateText(source)}</small>
                      </td>
                      <td>
                        {sourceCoverageText(source)}
                        <small>
                          {sourceVerificationText(catalog || source)}
                        </small>
                        {url && <a href={url}>Fuente original</a>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>
          <section className="report-section">
            <h2>4. Limitaciones</h2>
            <ul>
              {[
                ...new Set([
                  "Coordenadas recibidas: CRS_UNKNOWN. No reproyectadas.",
                  "Machine Learning no activo.",
                  ...result.limitations,
                ]),
              ].map((item, i) => (
                <li key={i}>{publicTechnicalText(item)}</li>
              ))}
            </ul>
          </section>
          <Notice tone="warning">
            La información faltante debe resolverse antes de formular
            conclusiones técnicas.
          </Notice>
          <ReportFooter page={3} />
        </article>
      </div>
    </main>
  );
}
