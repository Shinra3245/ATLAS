import React, { useEffect, useRef } from "react";
import { X, ExternalLink, MapPin, FileSearch } from "lucide-react";
import { Badge, Notice } from "./UI";
import {
  factorName,
  formatValue,
  publicTechnicalText,
  sourceCoverageText,
  sourceDateText,
  sourceDisplayName,
  sourceInstitutionText,
  sourceOriginText,
  sourceVerificationText,
  temporalLabel,
  validExternalUrl,
} from "../utils/presentation.mjs";

export function EvidenceDialog({ evidence, catalogSources, onClose }) {
  const dialog = useRef(null);
  useEffect(() => {
    dialog.current.showModal();
  }, []);
  const { factor, location } = evidence;
  const catalog = catalogSources.find((s) => s.id === factor.source?.id);
  const source = factor.source;
  const url = validExternalUrl(catalog?.original_url);
  const explanation = factor.explanation || {};
  const sections = [
    ["Qué se encontró", explanation.found],
    ["De dónde proviene", sourceOriginText(factor)],
    ["Cómo se obtuvo", explanation.operation],
    ["Qué significa", explanation.meaning],
    ["Qué no significa", explanation.not_meaning],
    ["Qué limitación tiene", explanation.limitation],
  ];
  return (
    <dialog
      ref={dialog}
      className="evidence-dialog"
      aria-labelledby="evidence-title"
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === dialog.current) onClose();
      }}
    >
      <div className="evidence-content">
        <div className="dialog-header">
          <div>
            <span className="eyebrow">EVIDENCIA Y TRAZABILIDAD</span>
            <h2 id="evidence-title">{factorName(factor)}</h2>
          </div>
          <button
            className="icon-button"
            aria-label="Cerrar evidencia"
            onClick={onClose}
          >
            <X />
          </button>
        </div>
        <div className="dialog-badges">
          <Badge status={factor.status} />
          <span className="unit-chip">
            {source
              ? sourceVerificationText(catalog || source)
              : "Sin fuente utilizable para esta unidad"}
          </span>
        </div>
        <div className="evidence-value">
          <strong>
            {formatValue(factor.value, factor.unit, factor.factor)}
          </strong>
          <span>
            <MapPin size={15} />
            {location.label || "Localidad"} · {location.municipality}
            <small>
              CVEGEO {location.locality_id} ·{" "}
              {temporalLabel(factor.temporal_context)}
            </small>
          </span>
        </div>
        <div className="explanation-grid">
          {sections.map(([label, body], i) => (
            <section
              key={label}
              className={`explanation-card explanation-${i}`}
            >
              <h3>
                <span>{i + 1}</span>
                {label}
              </h3>
              <p>{body || "No documentado para este resultado."}</p>
            </section>
          ))}
        </div>
        <section className="source-details">
          <h3>
            <FileSearch size={19} />
            Procedencia del dato
          </h3>
          <dl>
            <dt>Información consultada</dt>
            <dd>{sourceDisplayName(source)}</dd>
            <dt>Institución declarada</dt>
            <dd>{sourceInstitutionText(source)}</dd>
            <dt>Fecha o período</dt>
            <dd>{sourceDateText(source)}</dd>
            <dt>Cobertura</dt>
            <dd>{sourceCoverageText(source)}</dd>
            <dt>Licencia / condiciones</dt>
            <dd>{publicTechnicalText(catalog?.license_or_terms)}</dd>
            <dt>URL original</dt>
            <dd>
              {url ? (
                <a href={url} target="_blank" rel="noopener noreferrer">
                  Consultar fuente original <ExternalLink size={13} />
                </a>
              ) : (
                "No documentada"
              )}
            </dd>
          </dl>
        </section>
        {factor.limitations?.length > 0 && (
          <section className="limitations-box">
            <h3>Limitaciones específicas</h3>
            <ul>
              {factor.limitations.map((v, i) => (
                <li key={i}>{publicTechnicalText(v)}</li>
              ))}
            </ul>
          </section>
        )}
        <Notice>
          Esta evidencia describe la unidad y la temporalidad publicadas. No
          acredita condiciones del predio ni sustituye verificación técnica.
        </Notice>
      </div>
    </dialog>
  );
}
