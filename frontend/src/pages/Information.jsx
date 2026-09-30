import React, { useState } from "react";
import {
  BookOpen,
  Database,
  FileSearch,
  MapPin,
  Search,
  Scale,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { Button, ErrorNotice, Loading, Notice } from "../components/UI";
import {
  STATUS,
  publicTechnicalText,
  sourceCoverageText,
  sourceDateText,
  sourceDisplayName,
  sourceInstitutionText,
  sourceVerificationText,
  validExternalUrl,
} from "../utils/presentation.mjs";

export function Methodology() {
  return (
    <main id="main-content" className="information-page container">
      <span className="eyebrow">CONOCE EL ALCANCE</span>
      <h1>
        La evidencia primero.
        <br />
        <em>Las conclusiones, con límites.</em>
      </h1>
      <p className="page-lead">
        ATLAS integra información publicada para localidades de Irapuato y
        Celaya. Hace explícito qué se conoce, de dónde proviene y qué falta
        validar.
      </p>
      <div className="method-grid">
        {[
          [
            MapPin,
            "01 · Selección territorial",
            "La unidad actual es la localidad censal, identificada por CVEGEO. Los datos no se interpolan a predios ni a coordenadas arbitrarias.",
          ],
          [
            FileSearch,
            "02 · Lectura explicable",
            "Cada factor conserva valor, unidad, estado, temporalidad, fuente y limitación. Los antecedentes de 2014 no representan riesgo actual.",
          ],
          [
            Scale,
            "03 · Comparación consistente",
            "A y B se consultan con el mismo tipo de proyecto y la misma matriz. Las diferencias observables no producen un ganador ni un score global.",
          ],
          [
            Database,
            "04 · Procedencia y faltantes",
            "La disponibilidad y la verificación de la fuente se muestran separadas. La altitud censal no sustituye un DEM y los indicadores municipales no son mediciones locales.",
          ],
        ].map(([Icon, title, body]) => (
          <section className="method-card" key={title}>
            <Icon size={27} />
            <h2>{title}</h2>
            <p>{body}</p>
          </section>
        ))}
      </div>
      <Notice tone="warning">
        El sistema de referencia de las coordenadas recibidas no está
        verificado. El mapa es una referencia visual, no una acreditación de
        precisión geográfica del predio.
      </Notice>
      <section className="method-note">
        <h2>Machine Learning: experimento histórico</h2>
        <p>
          El análisis de una localidad muestra un experimento sobre daño por
          inundación reportado en 2014. No estima el riesgo de hoy y no publica
          una probabilidad: la prueba por municipio no separa ese daño con
          utilidad. Los factores con fuente siguen siendo la lectura principal.
        </p>
      </section>
      <Notice />
      <a className="button button-primary" href="#/sistema">
        Explorar ATLAS <ArrowRight size={18} />
      </a>
    </main>
  );
}
export function Sources({ catalog }) {
  const [query, setQuery] = useState("");
  const filtered = catalog.sources.filter((s) =>
    `${s.name} ${s.id} ${s.institution}`
      .toLocaleLowerCase("es")
      .includes(query.toLocaleLowerCase("es")),
  );
  return (
    <main id="main-content" className="information-page container">
      <span className="eyebrow">DATOS CON PROCEDENCIA VISIBLE</span>
      <h1>
        Fuentes y <em>trazabilidad</em>
      </h1>
      <p className="page-lead">
        Catálogo publicado por el motor. Que un archivo esté recibido no
        significa que tenga geometría utilizable ni procedencia plenamente
        verificada.
      </p>
      <Notice>
        Este catálogo no declara todas las fuentes como oficiales verificadas.
        Las instituciones son atribuciones declaradas en los archivos; se
        conservan las limitaciones de origen, licencia y temporalidad.
      </Notice>
      <label className="field-label" htmlFor="source-search">
        Buscar fuente
      </label>
      <div className="search-field source-search">
        <Search size={18} />
        <input
          id="source-search"
          placeholder="Nombre, identificador o institución"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {catalog.loading ? (
        <Loading text="Cargando fuentes…" detail="Consultando el catálogo de información disponible." />
      ) : catalog.error ? (
        <ErrorNotice error={catalog.error} retry={catalog.retry} />
      ) : (
        <>
          <p className="catalog-counter">
            {filtered.length} fuentes publicadas
          </p>
          <div className="sources-grid">
            {filtered.map((s) => {
              const url = validExternalUrl(s.original_url);
              return (
                <article className="source-card" key={s.id}>
                  <div className="source-card-top">
                    <Database size={24} />
                    <span className="provenance-tag">
                      {sourceVerificationText(s)}
                    </span>
                  </div>
                  <h2>{sourceDisplayName(s)}</h2>
                  <dl>
                    <dt>Institución declarada</dt>
                    <dd>{sourceInstitutionText(s)}</dd>
                    <dt>Año / versión</dt>
                    <dd>{sourceDateText(s)}</dd>
                    <dt>Cobertura</dt>
                    <dd>{sourceCoverageText(s)}</dd>
                    <dt>Licencia</dt>
                    <dd>{publicTechnicalText(s.license_or_terms)}</dd>
                  </dl>
                  <details>
                    <summary>Limitaciones de uso</summary>
                    <p>{publicTechnicalText(s.limitations || s.usage)}</p>
                    {s.sha256 && (
                      <p className="hash-value">SHA256: {s.sha256}</p>
                    )}
                  </details>
                  {url ? (
                    <a
                      className="evidence-link"
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Fuente original <ExternalLink size={14} />
                    </a>
                  ) : (
                    <small className="source-no-url">
                      URL original no documentada
                    </small>
                  )}
                </article>
              );
            })}
          </div>
          {!filtered.length && (
            <p className="empty-state">
              No hay fuentes que coincidan con esa búsqueda.
            </p>
          )}
        </>
      )}
    </main>
  );
}
export function InformationStates() {
  return (
    <main id="main-content" className="information-page container">
      <span className="eyebrow">INTERPRETA LOS RESULTADOS</span>
      <h1>
        Estados de <em>información</em>
      </h1>
      <p className="page-lead">
        Los estados describen la evidencia disponible para cada factor y unidad.
        No son una clasificación de peligro o seguridad.
      </p>
      <div className="states-grid">
        {Object.entries(STATUS).map(([key, s], i) => (
          <article key={key} className={`state-card state-${s.tone}`}>
            <span className="state-number">0{i + 1}</span>
            <h2>{s.label}</h2>
            <p>{s.description}</p>
            <code>{key}</code>
          </article>
        ))}
      </div>
      <Notice tone="warning">
        Sin información no significa sin riesgo. Sin condición registrada no
        significa seguro. Una fuente parcialmente verificada requiere revisar
        sus limitaciones.
      </Notice>
      <section className="method-note">
        <h2>Más datos no significa menor riesgo</h2>
        <p>
          La cobertura muestra cantidades de información disponible, parcial o
          faltante. Comparar esos conteos no permite decidir automáticamente
          dónde construir.
        </p>
      </section>
      <a className="button button-primary" href="#/sistema">
        Consultar una localidad <ArrowRight size={18} />
      </a>
    </main>
  );
}
