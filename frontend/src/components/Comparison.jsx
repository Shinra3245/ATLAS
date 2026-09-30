import React from "react";
import { ArrowLeft, FileText, RefreshCw, Scale } from "lucide-react";
import { Badge, Button, Notice } from "./UI";
import { CoverageSummary, LocationSummary, MachineLearningPanel } from "./Analysis";
import {
  CORE,
  allFactors,
  factorName,
  formatValue,
  isMunicipal,
  plainDifference,
  summarize,
} from "../utils/presentation.mjs";

export function Comparison({
  comparison,
  resultA,
  resultB,
  revealed,
  onBack,
  onChangeB,
  onReport,
  onEvidence,
}) {
  const core = CORE.map((code) =>
    comparison.factors.find((f) => f.factor === code),
  ).filter(Boolean);
  const other = comparison.factors.filter((f) => !CORE.includes(f.factor));
  function evidence(factor, side) {
    const result = side === "A" ? resultA : resultB;
    const original = allFactors(result).find((f) => f.factor === factor.factor);
    if (original) onEvidence(original, result.location);
  }
  function Table({ factors }) {
    return (
      <div
        className="table-scroll"
        tabIndex={0}
        aria-label="Tabla comparativa desplazable"
      >
        <table className="comparison-table">
          <thead>
            <tr>
              <th>Factor</th>
              <th>Ubicación A</th>
              <th>Ubicación B</th>
              <th>Diferencia observable</th>
            </tr>
          </thead>
          <tbody>
            {factors.map((f) => (
              <tr key={f.factor}>
                <th scope="row">
                  {factorName(f)}
                  <small>
                    {f.category === "context"
                      ? "Contexto territorial"
                      : f.category === "hazard_history"
                        ? "Antecedente histórico"
                        : "Factor territorial"}
                  </small>
                </th>
                {["A", "B"].map((side) => (
                  <td key={side}>
                    <strong>
                      {formatValue(
                        f[side === "A" ? "value_a" : "value_b"],
                        f.unit,
                        f.factor,
                      )}
                    </strong>
                    <Badge status={f[side === "A" ? "status_a" : "status_b"]} />
                    <button
                      className="evidence-link"
                      onClick={() => evidence(f, side)}
                    >
                      <FileText size={12} />
                      Ver evidencia {side}
                    </button>
                  </td>
                ))}
                <td>
                  <p>{plainDifference(f)}</p>
                  {f.limitations.length > 0 && (
                    <details>
                      <summary>Limitaciones</summary>
                      <ul>
                        {f.limitations.map((x, i) => (
                          <li key={i}>{x}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  const allA = allFactors(resultA),
    allB = allFactors(resultB);
  return (
    <>
      <div className="panel-heading">
        <span className="eyebrow">MISMA MATRIZ · SIN GANADOR AUTOMÁTICO</span>
        <h1>
          Comparación territorial <em>A/B</em>
        </h1>
        <p>Contrasta evidencia, no puntuaciones de seguridad.</p>
      </div>
      <div className="comparison-locations">
        <LocationSummary
          location={comparison.location_a}
          project={comparison.project_type}
          side="A"
          compact
        />
        <LocationSummary
          location={comparison.location_b}
          project={comparison.project_type}
          side="B"
          compact
        />
      </div>
      <div className="block-heading">
        <h2>Comparación de factores núcleo</h2>
        <span>Valores y estados reales del motor</span>
      </div>
      <Table factors={core} />
      <div className="comparison-coverage">
        <CoverageSummary
          coverage={summarize(allA.filter((f) => CORE.includes(f.factor)))}
          title="Información de factores núcleo A"
          compact
        />
        <CoverageSummary
          coverage={summarize(allB.filter((f) => CORE.includes(f.factor)))}
          title="Información de factores núcleo B"
          compact
        />
      </div>
      {revealed && (
        <div className="ml-pair">
          <MachineLearningPanel ml={resultA?.ml} compact />
          <MachineLearningPanel ml={resultB?.ml} compact />
        </div>
      )}
      <details className="more-details">
        <summary>
          Contexto territorial y municipal ({other.length} indicadores)
        </summary>
        <Notice>
          El contexto no es una amenaza. Los indicadores municipales no son
          mediciones de la localidad o del predio.
        </Notice>
        <Table factors={other} />
      </details>
      <details className="more-details">
        <summary>Fuentes, cobertura total y limitaciones</summary>
        <div className="comparison-coverage">
          <CoverageSummary
            coverage={comparison.coverage_a}
            title="Cobertura total A"
          />
          <CoverageSummary
            coverage={comparison.coverage_b}
            title="Cobertura total B"
          />
        </div>
        <ul>
          {[...new Set([...comparison.notes, ...comparison.limitations])].map(
            (item, i) => (
              <li key={i}>{item}</li>
            ),
          )}
        </ul>
      </details>
      <Notice tone="warning">{comparison.disclaimer}</Notice>
      <div className="panel-actions">
        <Button icon={ArrowLeft} variant="outline" onClick={onBack}>
          Volver a A
        </Button>
        <Button icon={RefreshCw} variant="outline" onClick={onChangeB}>
          Cambiar B
        </Button>
        <Button icon={FileText} onClick={() => onReport("a")}>
          Ver ficha A
        </Button>
        <Button icon={FileText} variant="outline" onClick={() => onReport("b")}>
          Ver ficha B
        </Button>
      </div>
    </>
  );
}
