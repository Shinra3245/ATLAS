import React, { useEffect, useRef, useState } from "react";
import { Blobatar } from "@blobatar/react";
import { useGaze } from "@blobatar/react/gaze";
import { happy, idle, thinking, unsure } from "blobatar/expression";
import "blobatar/motion.css";
import "blobatar/gaze.css";
import { guideMoment } from "../guide/moments.mjs";
import { guideChoice, saveGuideChoice, tourDone } from "../guide/tour.mjs";
import { api } from "../services/api.mjs";
import {
  PROJECTS,
  STATUS,
  allFactors,
  factorName,
  formatValue,
  isMunicipal,
} from "../utils/presentation.mjs";

const EXPRESSIONS = { happy, idle, thinking, unsure };
const CHAT_GREETING = "¿Quieres que te explique el funcionamiento de ATLAS?";
const CHAT_POPUP = "¡Hola! ¿Buscas ayuda?";
const TOUR_OFFER = "¡Hola! Soy Geo, tu guía, ¿necesitas ayuda?";
const TOUR_QUESTION = "Soy tu guía en el sistema de ATLAS, ¿gustas que te muestre cómo funciona?";
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

function factorBrief(result) {
  if (!result) return [];
  return allFactors(result)
    .filter((factor) => !isMunicipal(factor))
    .slice(0, 16)
    .map((factor) => ({
      name: String(factorName(factor) || "Factor").slice(0, 80),
      status: String(STATUS[factor.status]?.label || factor.status || "Sin estado").slice(0, 40),
      value: String(formatValue(factor.value, factor.unit, factor.factor)).slice(0, 80),
    }))
    .filter((item) => item.name && item.status);
}

function bubbleText(text) {
  return String(text).replace(/\*\*/g, "");
}

function screenContext(state, note) {
  return {
    route: state.route || "",
    phase: state.phase || "",
    municipality: state.municipality || "",
    project: PROJECTS[state.project] || state.project || "",
    locality_a: state.localityA || "",
    locality_b: state.localityB || "",
    note: note || "",
    factors_a: factorBrief(state.resultA),
    factors_b: factorBrief(state.resultB),
  };
}

export function Guide(state) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState(null);
  const faceRef = useRef(null);
  const threadRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const generation = useRef(0);
  const { ref: gazeRef } = useGaze({ travel: 3, lookAt: "pointer" });
  const [tourFinished, setTourFinished] = useState(() => tourDone());
  const [choice, setChoice] = useState(() => guideChoice());
  const [asking, setAsking] = useState(false);
  const { expression, message, prompt } = guideMoment(state);
  const onLanding = state.route === "/";
  const asked = Boolean(choice) || tourFinished;
  const showHello = onLanding && !asked && !asking;
  const showQuestion = onLanding && !asked && asking;
  const revealed = !showHello && !showQuestion && asked && (open || !prompt);
  const popup = asked ? CHAT_POPUP : TOUR_OFFER;

  useEffect(() => {
    function markFinished() {
      setTourFinished(true);
    }
    window.addEventListener("atlas:tour-done", markFinished);
    return () => window.removeEventListener("atlas:tour-done", markFinished);
  }, []);

  function openGuide() {
    if (onLanding && !asked) {
      setAsking(true);
      return;
    }
    if (!asked) {
      window.dispatchEvent(new Event("atlas:tour-start"));
      return;
    }
    setOpen(true);
  }

  function acceptTour() {
    saveGuideChoice("tour");
    setChoice("tour");
    setAsking(false);
    window.dispatchEvent(new Event("atlas:tour-start"));
  }

  function declineTour() {
    saveGuideChoice("chat");
    setChoice("chat");
    setAsking(false);
    setOpen(true);
  }
  const liveExpression = sending ? "thinking" : chatError ? "unsure" : expression;

  useEffect(() => {
    setOpen(false);
  }, [message]);
  useEffect(() => {
    generation.current += 1;
    abortRef.current?.abort();
    abortRef.current = null;
    setSending(false);
    setMessages([]);
    setChatError(null);
  }, [state.route, state.phase]);
  useEffect(() => {
    const node = threadRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messages, sending, chatError, revealed]);
  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);
  useEffect(() => () => abortRef.current?.abort(), []);
  useEffect(() => {
    const bob = faceRef.current?.querySelector(".mo-bob");
    if (!bob || bob.querySelector(":scope > .guide-helmet")) return;
    const helmet = mountHelmet(bob);
    return () => helmet.remove();
  }, [liveExpression]);

  async function send(event) {
    event.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;
    const next = [...messages, { role: "user", content }];
    const stamp = generation.current;
    setMessages(next);
    setDraft("");
    setChatError(null);
    setSending(true);
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const data = await api.assistant(next, screenContext(state, message), controller.signal);
      if (controller.signal.aborted || stamp !== generation.current) return;
      setMessages((current) => [...current, { role: "assistant", content: data.reply }]);
    } catch (error) {
      if (controller.signal.aborted || stamp !== generation.current) return;
      // Un intento fallido no debe dejar dos turnos de usuario seguidos al reintentar.
      setMessages((current) => current.slice(0, -1));
      setDraft(content);
      setChatError(error.message || "No pude responder. Intenta de nuevo.");
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null;
        setSending(false);
      }
    }
  }

  return (
    <aside className="guide" aria-label="Guía de ATLAS">
      {revealed ? (
        <div className="guide-bubble atlas-chat">
          <div className="atlas-chat-frame">
            <div className="atlas-chat-header">
              <h2>Asistente</h2>
              <div className="atlas-chat-status">En línea</div>
            </div>
            <div
              className="atlas-chat-display"
              id="chatDisplay"
              ref={threadRef}
              aria-live="polite"
            >
              <div className="chat-message chat-message-assistant">
                {bubbleText(prompt ? CHAT_GREETING : message)}
              </div>
              {messages.map((turn, index) => (
                <div
                  key={`${turn.role}-${index}`}
                  className={`chat-message chat-message-${turn.role === "user" ? "user" : "assistant"}`}
                >
                  {bubbleText(turn.content)}
                </div>
              ))}
              {sending && <div className="chat-message chat-message-assistant">Estoy pensando…</div>}
              {chatError && <p className="atlas-chat-error">{chatError}</p>}
            </div>
            <form className="atlas-chat-footer" onSubmit={send}>
              <input
                ref={inputRef}
                id="chatInput"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Escribe tu mensaje…"
                aria-label="Mensaje para la guía"
                maxLength={1500}
                disabled={sending}
              />
              <button id="sendButton" type="submit" disabled={sending || !draft.trim()}>
                Enviar
              </button>
            </form>
          </div>
        </div>
      ) : showQuestion ? (
        <div className="guide-bubble guide-offer" role="group" aria-label="Oferta del recorrido">
          <p className="guide-message">{TOUR_QUESTION}</p>
          <div className="guide-offer-actions">
            <button type="button" className="button button-primary" onClick={acceptTour}>
              Sí
            </button>
            <button type="button" className="button button-outline" onClick={declineTour}>
              No
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          key={prompt}
          className="guide-bubble guide-bubble-prompt"
          onClick={openGuide}
        >
          <span className="guide-message">{popup}</span>
        </button>
      )}
      <button
        type="button"
        ref={faceRef}
        className="guide-toggle"
        aria-expanded={revealed}
        aria-label={asked ? (revealed ? "Ocultar la explicación" : "Mostrar la explicación") : "Hablar con Geo"}
        onClick={() => {
          if (!asked || showHello) {
            openGuide();
            return;
          }
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
          expression={EXPRESSIONS[liveExpression] ?? unsure}
          title="Guía de ATLAS"
        />
      </button>
    </aside>
  );
}
