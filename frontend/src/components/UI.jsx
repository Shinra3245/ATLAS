import React from "react";
import {
  AlertCircle,
  ArrowRight,
  Building2,
  Check,
  ChevronRight,
  Clock3,
  Database,
  FileText,
  Home,
  Info,
  Landmark,
  Layers,
  MapPin,
  Mountain,
  Route,
  Search,
  ShieldCheck,
  Trees,
  TriangleAlert,
  Waves,
  Zap,
  X,
} from "lucide-react";
import { STATUS, DISCLAIMER } from "../utils/presentation.mjs";

export function Logo({ light = false }) {
  return (
    <a
      className={`brand ${light ? "brand-light" : ""}`}
      href="#/"
      aria-label="ATLAS, inicio"
    >
      <img
        className="brand-mark"
        src="/atlas-logo.png"
        alt=""
        width="43"
        height="43"
      />
      <img
        className="brand-wordmark"
        src="/atlas-name.png"
        alt=""
        width="175"
        height="58"
      />
    </a>
  );
}
export function Button({
  children,
  icon: Icon,
  variant = "primary",
  className = "",
  ...props
}) {
  return (
    <button className={`button button-${variant} ${className}`} {...props}>
      {Icon && <Icon size={18} aria-hidden="true" />}
      {children}
    </button>
  );
}
export function Badge({ status, children }) {
  const s = STATUS[status] || {
    tone: "partial",
    label: "Estado no documentado",
  };
  return (
    <span className={`badge badge-${s.tone}`}>
      <span className="status-dot" aria-hidden="true" />
      {children || s.label}
    </span>
  );
}
export function Notice({
  children = DISCLAIMER,
  tone = "info",
  className = "",
}) {
  return (
    <div className={`notice notice-${tone} ${className}`}>
      <Info size={18} aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}
export function ErrorNotice({ error, retry }) {
  return (
    <div className="error-box" role="alert">
      <AlertCircle size={24} />
      <div>
        <strong>No pudimos completar la consulta</strong>
        <p>{error}</p>
        {retry && (
          <Button variant="outline" onClick={retry}>
            Intentar nuevamente
          </Button>
        )}
      </div>
    </div>
  );
}
export function Loading({ text = "Consultando información real…" }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" />
      {text}
    </div>
  );
}
export function FactorIcon({ code, size = 22, ...props }) {
  const Icon =
    {
      flood_history: Waves,
      faults: Zap,
      slope: TriangleAlert,
      landslide_susceptibility: Mountain,
      land_use: Trees,
      elevation: Mountain,
      population: Home,
      services_coverage: Zap,
      road_proximity: Route,
      hydrography_proximity: Waves,
      rail_proximity: Route,
      industry_proximity: Building2,
      power_infrastructure_proximity: Zap,
    }[code] || Database;
  return <Icon size={size} aria-hidden="true" {...props} />;
}
export const Icons = {
  ArrowRight,
  Building2,
  Check,
  ChevronRight,
  Clock3,
  Database,
  FileText,
  Home,
  Info,
  Landmark,
  Layers,
  MapPin,
  Mountain,
  Route,
  Search,
  ShieldCheck,
  Trees,
  TriangleAlert,
  Waves,
  X,
};
