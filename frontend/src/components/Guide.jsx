import React, { useEffect, useRef, useState } from "react";
import { Blobatar } from "@blobatar/react";
import { useGaze } from "@blobatar/react/gaze";
import { happy, idle, thinking, unsure } from "blobatar/expression";
import "blobatar/motion.css";
import "blobatar/gaze.css";
import { guideMoment } from "../guide/moments.mjs";

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

export function Guide(state) {
  const [open, setOpen] = useState(false);
  const faceRef = useRef(null);
  const { ref: gazeRef } = useGaze({ travel: 3, lookAt: "pointer" });
  const { expression, message, prompt } = guideMoment(state);
  const revealed = open || !prompt;
  useEffect(() => {
    setOpen(false);
  }, [message]);
  useEffect(() => {
    const bob = faceRef.current?.querySelector(".mo-bob");
    if (!bob || bob.querySelector(":scope > .guide-helmet")) return;
    const helmet = mountHelmet(bob);
    return () => helmet.remove();
  }, [expression]);
  return (
    <aside className="guide" aria-label="Guía de ATLAS">
      {revealed ? (
        <div className="guide-bubble">
          <p className="guide-message" aria-live="polite">
            {message}
          </p>
        </div>
      ) : (
        <button
          type="button"
          key={prompt}
          className="guide-bubble guide-bubble-prompt"
          onClick={() => setOpen(true)}
        >
          <span className="guide-message">{prompt}</span>
        </button>
      )}
      <button
        type="button"
        ref={faceRef}
        className="guide-toggle"
        aria-expanded={revealed}
        aria-label={revealed ? "Ocultar la explicación" : "Mostrar la explicación"}
        onClick={() => {
          if (prompt) setOpen((value) => !value);
        }}
      >
        <Blobatar
          name="manu99"
          traits={{ shape: 0.99 }}
          hue={225}
          palette={{ head: "#3DE5F2", eye: "#061116" }}
          ref={gazeRef}
          animate="always"
          size={112}
          expression={EXPRESSIONS[expression] ?? unsure}
          title="Guía de ATLAS"
        />
      </button>
    </aside>
  );
}
