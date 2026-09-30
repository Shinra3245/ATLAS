import React, { useEffect, useState } from "react";
import { ArrowLeft, Check, Pause, Play, RotateCcw, ArrowRight } from "lucide-react";
import { Logo } from "../components/UI";
import "./loader-showcase.css";

const PROPOSALS = [
  { id: "radar", number: "01", title: "Radar geoespacial", label: "Precisión territorial", description: "Un punto de referencia y tres pulsos concéntricos. Sobrio, técnico y fácil de reconocer." },
  { id: "topographic", number: "02", title: "ATLAS Geo Pulse", label: "Identidad topográfica", description: "El símbolo de ATLAS entre curvas de nivel que se expanden. Una firma visual propia del sistema.", recommended: true },
  { id: "pin", number: "03", title: "Pin con ondas", label: "Ubicación en proceso", description: "Un marcador sobre ondas suaves. Una conexión directa con la localidad que se está consultando." },
];
const STAGES = [
  { title: "Identificando localidad", detail: "Ubicando el punto de referencia…" },
  { title: "Consultando factores", detail: "Consultando información territorial…" },
  { title: "Revisando evidencia", detail: "Revisando evidencia disponible…" },
  { title: "Preparando resultados", detail: "Preparando evaluación preliminar…" },
];
const CONTOUR = "M120 57C140 52 141 68 159 69C180 71 169 88 184 100C199 115 183 130 183 145C181 162 159 155 149 168C135 183 119 169 102 174C83 178 81 158 64 155C44 152 56 132 46 118C36 100 56 91 62 76C69 60 88 68 99 59C106 53 113 59 120 57Z";

function AtlasMark() {
  return <g className="lp-mark"><path d="M120 96L140 132H130L120 113L110 132H100Z" fill="#0B3C5D" /><path d="M120 120L127 132H113Z" fill="#0891B2" /></g>;
}

export function GeoLoader({ variant, compact = false }) {
  return (
    <span className={`lp-visual lp-visual-${variant}${compact ? " lp-visual-compact" : ""}`} aria-hidden="true">
      <svg viewBox="0 0 240 240" fill="none">
        {variant === "radar" && <>
          <g className="lp-radar-reference" stroke="#0E7490" strokeWidth="1">
            <circle cx="120" cy="120" r="74" /><circle cx="120" cy="120" r="49" />
            <path d="M120 35V58M120 182V205M35 120H58M182 120H205" />
            <path d="M68 68L74 74M166 166L172 172M68 172L74 166M166 74L172 68" />
          </g>
          {[0, 1, 2].map(i => <circle key={i} className="lp-wave lp-radar-wave" style={{ "--wave-index": i }} cx="120" cy="120" r="64" stroke={i === 0 ? "#0E7490" : "#0891B2"} strokeWidth="1.6" />)}
          <circle cx="120" cy="120" r="17" fill="#F8FAFC" /><circle cx="120" cy="120" r="6" fill="#0B3C5D" />
          <path d="M120 136V153M116 148L120 153L124 148" stroke="#0B3C5D" strokeWidth="1.5" />
        </>}
        {variant === "topographic" && <>
          <path d={CONTOUR} transform="translate(120 120) scale(1.13) translate(-120 -120)" stroke="#0891B2" opacity=".13" />
          {[0, 1, 2].map(i => <path key={i} className="lp-wave lp-topographic-wave" style={{ "--wave-index": i }} d={CONTOUR} stroke={i === 0 ? "#0E7490" : "#0891B2"} strokeWidth="1.5" />)}
          <AtlasMark /><text x="120" y="150" textAnchor="middle" fill="#0B3C5D" fontSize="10" fontWeight="800" letterSpacing="3">ATLAS</text>
        </>}
        {variant === "pin" && <>
          <ellipse cx="120" cy="156" rx="72" ry="24" stroke="#0891B2" opacity=".12" />
          {[0, 1, 2].map(i => <ellipse key={i} className="lp-wave lp-pin-wave" style={{ "--wave-index": i }} cx="120" cy="156" rx="60" ry="20" stroke={i === 0 ? "#0E7490" : "#0891B2"} strokeWidth="1.7" />)}
          <g className="lp-pin-mark"><path d="M120 65C99 65 84 80 84 100C84 123 120 151 120 151C120 151 156 123 156 100C156 80 141 65 120 65Z" fill="#0B3C5D" /><circle cx="120" cy="100" r="13" fill="#F8FAFC" /><circle cx="120" cy="100" r="5" fill="#0891B2" /></g>
        </>}
      </svg>
    </span>
  );
}

function StageList({ stage }) {
  return <ol className="lp-stage-list" aria-label="Etapas de ejemplo">
    {STAGES.map((item, index) => <li key={item.title} className={index < stage ? "is-done" : index === stage ? "is-current" : ""} aria-current={index === stage ? "step" : undefined}>
      <span className="lp-stage-icon" aria-hidden="true">{index < stage ? <Check size={12} /> : index === stage ? <span /> : null}</span>
      {item.title}
    </li>)}
  </ol>;
}

function MapIllustration() {
  return <svg className="lp-map-art" viewBox="0 0 1000 390" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <rect width="1000" height="390" fill="#edf3f5" />
    <g fill="#e3ecef" stroke="#d5e3e8" strokeWidth="1.5">
      <path d="M0 20L195 0L310 112L242 205L0 190Z" /><path d="M379 0H683L721 94L525 136Z" /><path d="M783 0H1000V189L840 175L738 96Z" />
      <path d="M0 229L218 245L289 390H0Z" /><path d="M627 235L799 204L1000 250V390H668Z" />
    </g>
    <g stroke="#fff" strokeWidth="10" strokeLinejoin="round"><path d="M-20 209L246 223L348 133L557 188L781 141L1020 223" /><path d="M226 -20L337 124L410 250L407 410" /><path d="M755 -20L708 126L585 229L597 410" /></g>
    <g stroke="#c8dde6" strokeWidth="2"><path d="M-20 209L246 223L348 133L557 188L781 141L1020 223" /><path d="M226 -20L337 124L410 250L407 410" /><path d="M755 -20L708 126L585 229L597 410" /></g>
    <path d="M85 -20C107 86 165 94 138 183S212 299 258 420" stroke="#b8dee8" strokeWidth="12" />
    <g fill="none" stroke="#cfdee4"><path d="M860 250C890 190 964 211 1002 253M820 270C871 166 981 174 1033 251M791 282C858 141 1003 148 1067 251" /><path d="M-15 53C49 14 115 36 123 88S37 143 -17 120M-20 37C61 -15 146 20 146 84S33 169 -20 137" /></g>
  </svg>;
}

export function LoaderShowcase() {
  const [selected, setSelected] = useState("topographic");
  const [paused, setPaused] = useState(false);
  const [stages, setStages] = useState(true);
  const [stage, setStage] = useState(0);
  const [revision, setRevision] = useState(0);
  const [context, setContext] = useState("map");
  const [reducedMotion, setReducedMotion] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  const proposal = PROPOSALS.find(item => item.id === selected);

  useEffect(() => {
    document.title = "ATLAS · Laboratorio de loaders";
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    if (paused || !stages || reducedMotion) return;
    const timer = window.setInterval(() => setStage(current => (current + 1) % STAGES.length), 2800);
    return () => window.clearInterval(timer);
  }, [paused, stages, reducedMotion, revision]);

  function restart() {
    setStage(0);
    setRevision(current => current + 1);
    setPaused(false);
  }

  const details = stages ? STAGES[stage].detail : "Consultando información territorial…";
  return <div className={`lp-page${paused ? " lp-paused" : ""}`}>
    <header className="lp-header">
      <Logo />
      <span className="lp-header-label">LABORATORIO VISUAL</span>
      <a className="lp-back" href="#/sistema"><ArrowLeft size={15} aria-hidden="true" /> Volver al sistema</a>
    </header>
    <main className="lp-main" id="main-content">
      <section className="lp-intro">
        <span className="lp-kicker"><span /> MOVIMIENTO CON IDENTIDAD</span>
        <h1>Tres formas de explorar<br /><span>el territorio mientras carga.</span></h1>
        <p>Compara las propuestas de carga de ATLAS y prueba cómo se sienten en cada espacio.</p>
      </section>

      <div className="lp-toolbar" aria-label="Controles de la demostración">
        <div className="lp-demo-label"><span className="lp-live-dot" /> Vista de prueba <span>· sin consultas reales</span></div>
        <div className="lp-controls">
          <label className="lp-toggle"><input type="checkbox" checked={stages} onChange={event => setStages(event.target.checked)} /><span className="lp-toggle-track" aria-hidden="true" /> Mostrar etapas</label>
          <span className="lp-control-divider" />
          <button onClick={() => setPaused(current => !current)} aria-pressed={paused}>{paused ? <Play size={14} /> : <Pause size={14} />}{paused ? "Reanudar" : "Pausar"}</button>
          <button onClick={restart}><RotateCcw size={14} /> Reiniciar</button>
        </div>
      </div>
      {reducedMotion && <p className="lp-motion-note">Movimiento reducido activado. Las propuestas se muestran estáticas; puedes recorrer las etapas con «Siguiente etapa».</p>}

      <section className="lp-grid" aria-label="Tres propuestas de loaders">
        {PROPOSALS.map(item => <article key={item.id} className={`lp-card${selected === item.id ? " lp-card-selected" : ""}`}>
          <div className="lp-card-top"><span className="lp-number">{item.number}</span>{item.recommended && <span className="lp-recommended">Propuesta recomendada</span>}</div>
          <div className="lp-card-preview">
            <GeoLoader key={`${item.id}-${revision}`} variant={item.id} />
            <h2>Analizando localidad<span className="lp-dots" aria-hidden="true">…</span></h2>
            <p className="lp-loading-detail">{details}</p>
            {stages && <StageList stage={stage} />}
          </div>
          <div className="lp-card-info">
            <span className="lp-card-label">{item.label}</span><h3>{item.title}</h3><p>{item.description}</p>
            <button className="lp-select" aria-pressed={selected === item.id} onClick={() => setSelected(item.id)}>{selected === item.id ? <><Check size={15} /> En vista previa</> : <>Probar esta propuesta <ArrowRight size={15} /></>}</button>
          </div>
        </article>)}
      </section>

      <section className="lp-context" aria-labelledby="lp-context-title">
        <div className="lp-context-heading"><div><span className="lp-kicker">EN CONTEXTO</span><h2 id="lp-context-title">Así se vería {proposal.title}.</h2></div>
          <div className="lp-context-controls" role="group" aria-label="Espacio de la vista previa">
            {[ ["map", "Sobre el mapa"], ["modal", "En un modal"], ["button", "En un botón"] ].map(([id, title]) => <button key={id} aria-pressed={context === id} onClick={() => setContext(id)}>{title}</button>)}
          </div>
        </div>
        <div className={`lp-context-preview lp-context-${context}`}>
          {context !== "button" && <><MapIllustration /><span className="lp-map-label">MAPA ILUSTRATIVO · VISTA DE PRUEBA</span></>}
          {context === "map" && <div className="lp-map-loader"><GeoLoader key={`map-${selected}-${revision}`} variant={selected} /><div><strong>Analizando localidad…</strong><p>{details}</p></div></div>}
          {context === "modal" && <><div className="lp-modal-backdrop" /><div className="lp-modal-preview"><GeoLoader key={`modal-${selected}-${revision}`} variant={selected} /><strong>Analizando localidad…</strong><p>{details}</p>{stages && <StageList stage={stage} />}</div></>}
          {context === "button" && <div className="lp-button-preview"><span className="lp-card-label">UNA ESPERA BREVE</span><button className="lp-analyze-button" disabled><GeoLoader key={`button-${selected}-${revision}`} variant={selected} compact /> Analizando localidad…</button><p>La misma identidad, en un espacio más pequeño.</p></div>}
        </div>
        <div className="lp-context-footer"><span>Etapas de demostración. Sin porcentajes ni progreso real.</span>{stages && <button onClick={() => { setPaused(true); setStage(current => (current + 1) % STAGES.length); }}>Siguiente etapa <ArrowRight size={14} /></button>}</div>
      </section>
      <footer className="lp-footer"><span>ATLAS <span>/</span> Exploración de loaders</span><span>Azul marino · Turquesa · Cyan</span></footer>
    </main>
  </div>;
}
