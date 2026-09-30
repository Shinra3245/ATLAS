import React from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Building2,
  Check,
  Database,
  FileSearch,
  FileText,
  HardHat,
  Landmark,
  Layers,
  MapPin,
  Scale,
  Users,
} from "lucide-react";
import { Header } from "../components/Header";
import { Logo, Notice } from "../components/UI";
import { TerritoryMap } from "../map/TerritoryMap";

const features = [
  [
    MapPin,
    "Análisis por localidad",
    "Explora factores territoriales y contexto disponible para localidades de Irapuato y Celaya.",
    "/feature-locality.jpg",
    "IRAPUATO · CELAYA",
  ],
  [
    Scale,
    "Comparación A/B",
    "Contrasta dos localidades bajo el mismo tipo de proyecto y los mismos criterios.",
    "/feature-compare.jpg",
    "MISMOS CRITERIOS",
  ],
  [
    FileText,
    "Ficha y evidencia",
    "Consulta valores, procedencia, temporalidad, información faltante y limitaciones.",
    "/feature-evidence.jpg",
    "FUENTES · COBERTURA · LÍMITES",
  ],
];
const benefits = [
  [
    FileSearch,
    "Evidencia y procedencia visibles",
    "Conoce de dónde viene cada dato, su fecha de referencia y sus límites.",
  ],
  [
    Scale,
    "Los mismos criterios para A y B",
    "Compara información de forma consistente, sin un ganador automático.",
  ],
  [
    Database,
    "Información faltante explícita",
    "Identifica lo que aún necesita validación antes de llegar a una conclusión.",
  ],
];
const audiences = [
  [
    HardHat,
    "Despachos de arquitectura e ingeniería",
    "Identifica condiciones territoriales desde las primeras etapas de diseño.",
  ],
  [
    Building2,
    "Desarrolladores inmobiliarios",
    "Consulta evidencia y compara opciones de localización.",
  ],
  [
    Landmark,
    "Gobiernos y áreas de planeación",
    "Organiza la información territorial para apoyar procesos de planeación.",
  ],
  [
    Users,
    "Profesionales y organizaciones",
    "Explora contexto, fuentes y limitaciones para proyectos urbanos.",
  ],
];
const faqs = [
  [
    "¿Dónde funciona ATLAS?",
    "El MVP cubre exclusivamente las localidades publicadas de Irapuato y Celaya. El resto de Guanajuato es una implementación futura.",
  ],
  [
    "¿Qué tipos de proyecto puedo consultar?",
    "Vivienda, edificación y carretera o vialidad. El tipo de proyecto contextualiza la lectura; no cambia los valores originales del territorio.",
  ],
  [
    "¿Qué ocurre si faltan datos?",
    "La interfaz muestra la información faltante o pendiente de validación. La ausencia de datos no significa ausencia de riesgo.",
  ],
  [
    "¿Sustituye un estudio técnico?",
    "No. ATLAS ofrece una evaluación preliminar, no autoriza construcciones ni sustituye estudios, permisos o dictámenes.",
  ],
];

export function Landing({ catalog }) {
  const previewLocations = catalog.locations.filter((r) =>
    ["110170001", "110070001"].includes(r.id),
  );
  return (
    <>
      <Header />
      <main id="main-content" className="landing">
        <section className="hero topo-background">
          <div className="hero-photograph" aria-hidden="true" />
          <div className="container hero-grid">
            <div className="hero-copy">
              <span className="eyebrow">
                <span />
                INFORMACIÓN TERRITORIAL, DECISIONES CON EVIDENCIA
              </span>
              <h1>
                Evalúa y compara
                <br />
                información territorial
                <br />
                <em>antes de construir.</em>
              </h1>
              <p>
                Consulta condiciones territoriales, evidencia disponible y
                limitaciones para proyectos de vivienda, edificación y vialidad.
              </p>
              <div className="hero-actions">
                <a className="button button-primary" href="#/sistema">
                  Explorar ATLAS <ArrowUpRight size={19} />
                </a>
                <a className="button button-white" href="#/metodologia">
                  <BookOpen size={18} />
                  Conocer la metodología
                </a>
              </div>
            </div>
            <div className="hero-preview">
              <div className="preview-window">
                <div className="preview-top">
                  <Logo light />
                  <span>
                    <MapPin size={12} />
                    Mapa
                  </span>
                  <span>
                    <Layers size={12} />
                    Evidencia
                  </span>
                  <span>A / B</span>
                </div>
                <div className="preview-body">
                  <aside>
                    <small>NUEVO ANÁLISIS</small>
                    <strong>Selecciona una localidad</strong>
                    <div className="preview-input">
                      Irapuato <span>⌄</span>
                    </div>
                    <small>TIPO DE PROYECTO</small>
                    <div className="preview-type">
                      <Building2 size={15} />
                      Edificación
                      <Check size={12} />
                    </div>
                    <div className="preview-type">
                      <HardHat size={15} />
                      Vivienda
                    </div>
                    <div className="preview-type">
                      <Layers size={15} />
                      Vialidad
                    </div>
                    <div className="preview-tip">
                      <MapPin size={18} />
                      Unidad de análisis:
                      <br />
                      localidad censal
                    </div>
                  </aside>
                  <div className="preview-map">
                    <TerritoryMap locations={previewLocations} mini />
                    <span className="preview-map-caption">
                      MAPA DE REFERENCIA
                    </span>
                  </div>
                </div>
                <div className="preview-bottom">
                  <span>
                    <span className="status-dot" /> Evidencia y cobertura
                    visibles
                  </span>
                  <a href="#/sistema" aria-label="Abrir el sistema ATLAS">
                    <ArrowRight size={17} />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>
        <div className="container">
          <div className="benefits-row">
            {benefits.map(([Icon, title, body]) => (
              <article className="benefit" key={title}>
                <span className="icon-disc">
                  <Icon size={24} />
                </span>
                <div>
                  <h3>{title}</h3>
                  <p>{body}</p>
                </div>
              </article>
            ))}
          </div>
          <Notice />
        </div>
        <section className="section container" id="capacidades">
          <div className="section-heading">
            <span className="eyebrow">FUNCIONALIDADES PRINCIPALES</span>
            <h2>
              Qué puedes <em>consultar</em>
            </h2>
            <p>
              El contexto que necesitas, con la evidencia y las limitaciones a
              la vista.
            </p>
          </div>
          <div className="feature-grid">
            {features.map(([Icon, title, body, image, caption]) => (
              <a className="feature-card" href="#/sistema" key={title}>
                <div className="feature-card-head">
                  <span className="icon-disc">
                    <Icon size={27} />
                  </span>
                  <ArrowUpRight size={20} />
                </div>
                <h3>{title}</h3>
                <p>{body}</p>
                <div className="feature-illustration">
                  <img src={image} alt="" />
                  <small>{caption}</small>
                </div>
              </a>
            ))}
          </div>
        </section>
        <section className="steps-section topo-background" id="como-funciona">
          <div className="container section">
            <div className="section-heading">
              <span className="eyebrow">DE LA UBICACIÓN A LA EVIDENCIA</span>
              <h2>
                Así <em>funciona</em>
              </h2>
              <p>Un recorrido claro, sin saltar las preguntas importantes.</p>
            </div>
            <div className="steps-grid">
              {[
                [
                  "Elige tu proyecto",
                  "Vivienda, edificación o carretera / vialidad.",
                ],
                [
                  "Selecciona la localidad A",
                  "Busca por nombre o clave, o elige su marcador.",
                ],
                [
                  "Consulta el análisis",
                  "Revisa factores, contexto, ficha y evidencia.",
                ],
                [
                  "Compara con B",
                  "Contrasta otra localidad bajo los mismos criterios.",
                ],
              ].map(([title, body], i) => (
                <article className="step-card" key={title}>
                  <span className="step-number">0{i + 1}</span>
                  <h3>{title}</h3>
                  <p>{body}</p>
                  {i < 3 && <ArrowRight className="step-arrow" size={19} />}
                </article>
              ))}
            </div>
            <Notice>
              La comparación presenta diferencias observables. ATLAS no elige un
              ganador.
            </Notice>
          </div>
        </section>
        <section className="section container" id="usuarios">
          <div className="section-heading">
            <span className="eyebrow">USUARIOS DE ATLAS</span>
            <h2>
              Para quién está <em>pensado</em>
            </h2>
            <p>
              Apoyo preliminar para quienes analizan, planean y desarrollan
              proyectos urbanos.
            </p>
          </div>
          <div className="audience-grid">
            {audiences.map(([Icon, title, body]) => (
              <article className="audience-card" key={title}>
                <Icon size={31} />
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="section container faq-section" id="preguntas">
          <div className="section-heading">
            <span className="eyebrow">DUDAS COMUNES</span>
            <h2>
              Preguntas <em>frecuentes</em>
            </h2>
          </div>
          <div className="faq-grid">
            {faqs.map(([title, body]) => (
              <details key={title}>
                <summary>{title}</summary>
                <p>{body}</p>
              </details>
            ))}
          </div>
        </section>
        <section className="container closing-cta topo-background">
          <div>
            <span className="eyebrow">TOMA DECISIONES INFORMADAS</span>
            <h2>
              Consulta la evidencia
              <br />
              <em>antes de decidir.</em>
            </h2>
            <p>Conoce lo disponible y lo que falta por validar.</p>
          </div>
          <a className="button button-primary" href="#/sistema">
            Explorar ATLAS <ArrowUpRight size={20} />
          </a>
        </section>
      </main>
      <footer className="site-footer container">
        <div>
          <Logo />
          <small>MVP: Irapuato y Celaya · HackaTec / InnovaTecNM 2026</small>
        </div>
        <nav aria-label="Información del proyecto">
          <a href="#/metodologia">Metodología</a>
          <a href="#/fuentes">Fuentes</a>
          <a href="#/estados">Alcance y limitaciones</a>
        </nav>
        <p className="photo-credit">
          Fotografía de Irapuato:{" "}
          <a
            href="https://commons.wikimedia.org/wiki/File:Irapuato,_Guanajuato,_Mx.jpg"
            target="_blank"
            rel="noopener noreferrer"
          >
            Juan Carlos Fonseca Mata
          </a>{" "}
          ·{" "}
          <a
            href="https://creativecommons.org/licenses/by-sa/4.0/"
            target="_blank"
            rel="noopener noreferrer"
          >
            CC BY-SA 4.0
          </a>
          . Presentación con recorte visual y superposición de color.
        </p>
      </footer>
    </>
  );
}
