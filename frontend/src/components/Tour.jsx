import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Blobatar } from "@blobatar/react";
import { happy, idle, thinking, unsure } from "blobatar/expression";
import "blobatar/motion.css";
import { X } from "lucide-react";
import { TOUR_STEPS, markTourDone } from "../guide/tour.mjs";

const EXPRESSIONS = { happy, idle, thinking, unsure };
const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(name, attrs) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

function mountHelmet(bob) {
  const helmet = svgEl("g", { class: "guide-helmet", "aria-hidden": "true" });
  helmet.append(
    svgEl("ellipse", { cx: "54", cy: "28", rx: "26", ry: "5", fill: "#C98406" }),
    svgEl("ellipse", { cx: "54", cy: "26.2", rx: "24.5", ry: "3.8", fill: "#F6C21D" }),
    svgEl("path", {
      d: "M31.5 26.6C32 12 40 3.6 54 3.6C68 3.6 76 12 76.5 26.6Z",
      fill: "#FFD84A",
    }),
    svgEl("path", {
      d: "M54 4.6V25.4",
      fill: "none",
      stroke: "#E2A30A",
      "stroke-width": "1.6",
      "stroke-linecap": "round",
    }),
    svgEl("path", {
      d: "M42 16.2C45.2 12.8 49.6 11.8 53 13.6",
      fill: "none",
      stroke: "#FFF6CC",
      "stroke-width": "1.6",
      "stroke-linecap": "round",
    }),
  );
  bob.appendChild(helmet);
  return helmet;
}
const MARGIN = 12;
const GAP = 14;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function routeFromHash() {
  return location.hash.startsWith("#/") ? location.hash.slice(1) : "/";
}

function fieldValue(id) {
  return document.getElementById(id)?.value ?? "";
}

function gateMessage(step) {
  if (step?.gate === "name") {
    const value = fieldValue("auth-name").trim();
    if (value.length < 2 || value.length > 100) return "Escribe tu nombre completo para continuar.";
  }
  if (step?.gate === "email") {
    if (!EMAIL_PATTERN.test(fieldValue("auth-email").trim())) return "Escribe un correo válido para continuar.";
  }
  if (step?.gate === "institution") {
    const value = fieldValue("auth-institution").trim();
    if (value.length > 0 && (value.length < 2 || value.length > 120)) {
      return "Si indicas una institución, escribe su nombre.";
    }
  }
  if (step?.gate === "password") {
    const value = fieldValue("auth-password");
    if (value.length < 8 || !/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
      return "Escribe la contraseña (mínimo 8 caracteres, con letras y números) para continuar.";
    }
  }
  if (step?.gate === "confirm") {
    const confirm = fieldValue("auth-confirm");
    if (!confirm || confirm !== fieldValue("auth-password")) return "Repite la misma contraseña para continuar.";
  }
  if (step?.gate === "terms" && !document.querySelector(".auth-terms input")?.checked) {
    return "Acepta el alcance preliminar para continuar.";
  }
  return null;
}

function sameRect(a, b) {
  return (
    a &&
    b &&
    Math.abs(a.top - b.top) < 0.5 &&
    Math.abs(a.left - b.left) < 0.5 &&
    Math.abs(a.width - b.width) < 0.5 &&
    Math.abs(a.height - b.height) < 0.5
  );
}

function overlaps(box, rect) {
  return !(
    box.left + box.width <= rect.left - 8 ||
    box.left >= rect.left + rect.width + 8 ||
    box.top + box.height <= rect.top - 8 ||
    box.top >= rect.top + rect.height + 8
  );
}

function placeBubble(rect, width, height, placement) {
  const viewWidth = window.innerWidth;
  const viewHeight = window.innerHeight;
  if (!rect || viewWidth <= 720) {
    return {
      top: Math.round((viewHeight - height) / 2),
      left: Math.round((viewWidth - width) / 2),
    };
  }
  const beside = rect.left + rect.width / 2 > viewWidth / 2
    ? { top: rect.top + rect.height / 2 - height / 2, left: rect.left - GAP - width }
    : { top: rect.top + rect.height / 2 - height / 2, left: rect.left + rect.width + GAP };
  const below = { top: rect.top + rect.height + GAP, left: rect.left + rect.width / 2 - width / 2 };
  const above = { top: rect.top - GAP - height, left: rect.left + rect.width / 2 - width / 2 };
  const candidates = placement === "top" ? [beside, above, below] : [beside, below, above];
  const chosen = candidates.find((spot) => {
    const box = { ...spot, width, height };
    return (
      spot.top >= MARGIN &&
      spot.left >= MARGIN &&
      spot.top + height <= viewHeight - MARGIN &&
      spot.left + width <= viewWidth - MARGIN &&
      !overlaps(box, rect)
    );
  }) || candidates[0];
  return {
    top: Math.round(Math.min(Math.max(chosen.top, MARGIN), viewHeight - height - MARGIN)),
    left: Math.round(Math.min(Math.max(chosen.left, MARGIN), viewWidth - width - MARGIN)),
  };
}

export function Tour({ route, account }) {
  const [active, setActive] = useState(false);
  const [index, setIndex] = useState(0);
  const [rect, setRect] = useState(null);
  const [pos, setPos] = useState(null);
  const [gateError, setGateError] = useState(null);
  const bubbleRef = useRef(null);
  const faceRef = useRef(null);
  const startedRef = useRef(false);
  const scrolledRef = useRef(-1);
  const rectRef = useRef(null);

  const step = TOUR_STEPS[index] || null;
  const total = TOUR_STEPS.length;
  const isLast = index >= total - 1;
  const expression = gateError ? "unsure" : step?.expression;

  function finish() {
    setActive(false);
    setRect(null);
    setPos(null);
    setGateError(null);
    rectRef.current = null;
    markTourDone();
    window.dispatchEvent(new Event("atlas:tour-done"));
  }

  function goBack() {
    setGateError(null);
    setIndex((current) => Math.max(current - 1, 0));
  }

  function advance() {
    if (isLast) {
      finish();
      return;
    }
    const problem = gateMessage(step);
    if (problem) {
      setGateError(problem);
      return;
    }
    setGateError(null);
    setIndex((current) => Math.min(current + 1, total - 1));
  }

  useEffect(() => {
    const bob = faceRef.current?.querySelector(".mo-bob");
    if (!bob || bob.querySelector(":scope > .guide-helmet")) return undefined;
    const helmet = mountHelmet(bob);
    return () => helmet.remove();
  }, [expression, active, index]);

  // El globo de Geo dispara el recorrido; no arranca solo.
  useEffect(() => {
    function onStart() {
      startedRef.current = true;
      setIndex(0);
      setActive(true);
    }
    window.addEventListener("atlas:tour-start", onStart);
    return () => window.removeEventListener("atlas:tour-start", onStart);
  }, []);

  useEffect(() => {
    if (active) document.body.dataset.tour = "on";
    else delete document.body.dataset.tour;
    return () => delete document.body.dataset.tour;
  }, [active]);

  // Avance automatico cuando aparece la sesion durante el paso de registro.
  useEffect(() => {
    if (!active || !step) return;
    if (step.autoAdvanceOnLogin && account?.user) {
      setIndex((i) => Math.min(i + 1, total - 1));
    }
  }, [active, step, account?.user, total]);

  // Navegacion de ruta + medicion del objetivo a resaltar.
  useEffect(() => {
    if (!active || !step) return undefined;
    if (step.route && routeFromHash() !== step.route) {
      location.hash = step.route;
      return undefined; // el cambio de ruta re-ejecuta este efecto
    }
    let timer = 0;
    let frame = 0;
    let tries = 0;
    let stopped = false;
    let observer = null;
    let targetEl = null;
    rectRef.current = null;
    setGateError(null);

    function publish(next) {
      if (sameRect(rectRef.current, next)) return;
      rectRef.current = next;
      setRect(next);
    }
    function measure(allowScroll) {
      const el = step.target ? document.querySelector(step.target) : null;
      if (!el) return null;
      const bounds = el.getBoundingClientRect();
      if (!(bounds.width || bounds.height)) return null;
      if (allowScroll && scrolledRef.current !== index) {
        scrolledRef.current = index;
        const pad = 88;
        if (bounds.top < pad || bounds.bottom > window.innerHeight - pad) {
          el.scrollIntoView({ block: "center", behavior: "smooth" });
        }
        if (step.gate) el.querySelector("input")?.focus({ preventScroll: true });
      }
      publish({ top: bounds.top, left: bounds.left, width: bounds.width, height: bounds.height });
      return el;
    }
    function follow(el) {
      const started = performance.now();
      function frameTick() {
        if (stopped) return;
        measure(false);
        if (performance.now() - started < 700) frame = requestAnimationFrame(frameTick);
      }
      frame = requestAnimationFrame(frameTick);
      observer = new ResizeObserver(() => measure(false));
      observer.observe(el);
      document.querySelector(".auth-card")?.addEventListener("animationend", onMove);
    }
    function onMove() {
      measure(false);
    }
    function onInput() {
      setGateError((current) => (current && !gateMessage(step) ? null : current));
    }
    function tick() {
      if (stopped) return;
      const el = measure(true);
      if (el) {
        targetEl = el;
        follow(el);
        el.addEventListener("input", onInput);
        return;
      }
      tries += 1;
      if (tries > 30) {
        rectRef.current = null;
        setRect(null);
        return;
      }
      timer = window.setTimeout(tick, 100);
    }

    setRect(null);
    tick();
    window.addEventListener("scroll", onMove, true);
    window.addEventListener("resize", onMove);
    return () => {
      stopped = true;
      window.clearTimeout(timer);
      cancelAnimationFrame(frame);
      observer?.disconnect();
      document.querySelector(".auth-card")?.removeEventListener("animationend", onMove);
      targetEl?.removeEventListener("input", onInput);
      window.removeEventListener("scroll", onMove, true);
      window.removeEventListener("resize", onMove);
    };
  }, [active, step, index, route]);

  // Posiciona el globo junto al objetivo, sin taparlo.
  useLayoutEffect(() => {
    if (!active) return;
    const node = bubbleRef.current;
    if (!node) return;
    setPos(placeBubble(rect, node.offsetWidth, node.offsetHeight, step?.placement));
  }, [rect, index, active, step?.placement, gateError]);

  if (!active || !step) return null;

  return (
    <div className="tour-layer" role="dialog" aria-modal="false" aria-label="Recorrido de bienvenida">
      {rect ? (
        <div
          className="tour-spotlight"
          aria-hidden="true"
          style={{
            top: rect.top - 6,
            left: rect.left - 6,
            width: rect.width + 12,
            height: rect.height + 12,
          }}
        />
      ) : (
        <div className="tour-overlay" aria-hidden="true" />
      )}
      <section
        className="tour-bubble"
        ref={bubbleRef}
        style={pos ? { top: pos.top, left: pos.left } : { visibility: "hidden" }}
      >
        <button
          type="button"
          className="tour-close"
          aria-label="Omitir el recorrido"
          onClick={finish}
        >
          <X size={16} aria-hidden="true" />
        </button>
        <div className="tour-avatar" ref={faceRef} aria-hidden="true">
          <Blobatar
            name="manu99"
            traits={{ shape: 0.99 }}
            hue={225}
            palette={{ head: "#3DE5F2", eye: "#061116" }}
            animate="always"
            size={72}
            expression={EXPRESSIONS[expression] ?? idle}
            title="Guía de ATLAS"
          />
        </div>
        <div className="tour-body">
          <p className="tour-progress">
            Paso {index + 1} de {total}
          </p>
          <h2 className="tour-title">{step.title}</h2>
          <p className="tour-text">{step.body}</p>
          {step.emphasis && <p className="tour-emphasis">{step.emphasis}</p>}
          {gateError && <p className="tour-gate" role="alert">{gateError}</p>}
          <div className="tour-actions">
            <button
              type="button"
              className="tour-skip"
              onClick={finish}
            >
              {isLast ? "Cerrar" : "Omitir"}
            </button>
            <div className="tour-actions-main">
              <button
                type="button"
                className="button button-outline tour-back"
                onClick={goBack}
                disabled={index === 0}
              >
                Atrás
              </button>
              <button
                type="button"
                className="button button-primary tour-next"
                onClick={advance}
              >
                {isLast ? "Terminar" : "Siguiente"}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
