import React from "react";
import { Check } from "lucide-react";
import { useDelayedFlag } from "../hooks/useDelayedFlag";
import "./geo-pulse.css";

const CONTOUR = "M120 57C140 52 141 68 159 69C180 71 169 88 184 100C199 115 183 130 183 145C181 162 159 155 149 168C135 183 119 169 102 174C83 178 81 158 64 155C44 152 56 132 46 118C36 100 56 91 62 76C69 60 88 68 99 59C106 53 113 59 120 57Z";

export function GeoPulseIcon({ compact = false }) {
  const size = compact ? 88 : 64;
  return (
    <span className={`geo-pulse-icon${compact ? " geo-pulse-icon-compact" : ""}`} aria-hidden="true">
      <svg viewBox="0 0 240 240" fill="none">
        <path d={CONTOUR} transform="translate(120 120) scale(1.13) translate(-120 -120)" stroke="#0891B2" opacity=".13" />
        {[0, 1, 2].map(index => (
          <path key={index} className="geo-pulse-wave" style={{ "--wave-index": index }} d={CONTOUR} stroke={index === 0 ? "#0E7490" : "#0891B2"} strokeWidth="1.5" />
        ))}
        <image className="geo-pulse-mark" href="/atlas-logo.png" x={(240 - size) / 2} y={compact ? (240 - size) / 2 : 84} width={size} height={size} preserveAspectRatio="xMidYMid meet" />
        {!compact && <text x="120" y="150" textAnchor="middle" fill="#0B3C5D" fontSize="10" fontWeight="800" letterSpacing="3">ATLAS</text>}
      </svg>
    </span>
  );
}

export function GeoPulse({ title = "Consultando información territorial…", detail, variant = "panel", steps = [], delay = 0 }) {
  const visible = useDelayedFlag(true, delay);
  if (!visible) return null;
  return (
    <div className={`geo-pulse geo-pulse-${variant}`} role="status" aria-live="polite">
      <GeoPulseIcon />
      <div className="geo-pulse-copy">
        <strong className="geo-pulse-title">{title}</strong>
        {detail && <p className="geo-pulse-detail">{detail}</p>}
      </div>
      {steps.length > 0 && (
        <ol className="geo-pulse-steps" aria-label="Estado de la consulta">
          {steps.map(step => (
            <li key={step.id} className={`geo-pulse-step-${step.status}`} aria-current={step.status === "active" ? "step" : undefined}>
              <span className="geo-pulse-step-icon" aria-hidden="true">
                {step.status === "complete" ? <Check size={12} /> : step.status === "active" ? <span /> : null}
              </span>
              <span>{step.label}<span className="geo-pulse-sr">{step.status === "complete" ? ": completado" : step.status === "active" ? ": en curso" : ": pendiente"}</span></span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
