import React, { useEffect, useRef, useState } from "react";
import { Menu, X, ArrowUpRight, BookOpen, ChevronDown, CircleHelp, CreditCard, Database, LogIn, MapPin } from "lucide-react";
import { Blobatar } from "@blobatar/react";
import { happy } from "blobatar/expression";
import "blobatar/motion.css";
import { Logo } from "./UI";
import { useAccount } from "../hooks/useAccount";
import { planById } from "../plans.mjs";

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

export function Header({ context = "landing" }) {
  const [open, setOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef(null);
  const faceRef = useRef(null);
  const account = useAccount();
  const current = planById(account.role);
  const signedIn = Boolean(account.ready && account.user);
  const accountLabel = signedIn ? current?.name || "Cuenta" : "Iniciar sesión";
  const publicView = context === "landing" || context === "inner";
  const auth = context === "auth";

  useEffect(() => {
    if (!auth) return undefined;
    const bob = faceRef.current?.querySelector(".mo-bob");
    if (!bob || bob.querySelector(":scope > .guide-helmet")) return undefined;
    const helmet = mountHelmet(bob);
    return () => helmet.remove();
  }, [auth]);
  const currentHash = window.location.hash;
  const publicLinks = [
    ["Inicio", "#/"],
    ["Cómo funciona", "#como-funciona"],
    ["Capacidades", "#capacidades"],
    ["Usuarios", "#usuarios"],
    ["Preguntas", "#preguntas"],
  ];
  const publicPages = [
    ["Metodología", "#/metodologia", BookOpen, "Criterios y límites del análisis"],
    ["Fuentes", "#/fuentes", Database, "Datos, cobertura y procedencia"],
    ["Planes", "#/planes", CreditCard, "Opciones para usar ATLAS"],
    ["Ayuda", "#/estados", CircleHelp, "Estados de información y orientación"],
  ];
  const links = auth
    ? [["Inicio", "#/"], ["Metodología", "#/metodologia"], ["Planes", "#/planes"], ["Ayuda", "#/estados"]]
    : [["Inicio", "#/"], ["Cómo funciona", "#como-funciona"], ["Capacidades", "#capacidades"], ["Metodología", "#/metodologia"], ["Fuentes", "#/fuentes"], ["Planes", "#/planes"], ["Ayuda", "#/estados"]];

  useEffect(() => {
    if (!moreOpen) return undefined;
    function closeOnOutside(event) {
      if (!moreRef.current?.contains(event.target)) setMoreOpen(false);
    }
    function closeOnEscape(event) {
      if (event.key === "Escape") {
        setMoreOpen(false);
        moreRef.current?.querySelector("button")?.focus();
      }
    }
    document.addEventListener("pointerdown", closeOnOutside);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [moreOpen]);

  function closeMenus() {
    setOpen(false);
    setMoreOpen(false);
  }

  return (
    <header className={`site-header system-header ${publicView ? "public-header" : ""} ${auth ? "auth-header" : ""} ${context === "workspace" ? "workspace-header" : ""}`}>
      <div className="header-inner">
        <Logo light />
        <span className="header-location"><MapPin size={16} aria-hidden="true" /> MVP Irapuato + Celaya</span>
        <button
          className="icon-button menu-toggle"
          aria-label={open ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={open}
          onClick={() => { setOpen(!open); setMoreOpen(false); }}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav
          aria-label="Navegación principal"
          className={`navigation ${publicView ? "public-navigation" : ""} ${open ? "navigation-open" : ""}`}
        >
          {publicView && (
            <>
              <div className="public-primary-links">
                {publicLinks.map(([label, href]) => (
                  <a key={label} href={href} onClick={closeMenus} aria-current={currentHash === href || (href === "#/" && !currentHash) ? "page" : undefined}>
                    {label}
                  </a>
                ))}
              </div>
              <div className={`public-pages ${moreOpen ? "is-open" : ""} ${publicPages.some(([, href]) => href === currentHash) ? "has-current" : ""}`} ref={moreRef}>
                <button
                  type="button"
                  className="public-pages-trigger"
                  aria-label="Abrir vistas de ATLAS"
                  aria-controls="public-pages-panel"
                  aria-expanded={moreOpen}
                  onClick={() => setMoreOpen((value) => !value)}
                >
                  <Menu size={19} aria-hidden="true" />
                  <span>Más</span>
                  <ChevronDown size={15} aria-hidden="true" />
                </button>
                <div className="public-pages-panel" id="public-pages-panel" aria-label="Vistas de ATLAS">
                  <span className="public-pages-heading">VISTAS DE ATLAS</span>
                  {publicPages.map(([label, href, Icon, detail]) => (
                    <a key={label} href={href} onClick={closeMenus} aria-current={currentHash === href ? "page" : undefined}>
                      <span className="public-pages-icon"><Icon size={18} aria-hidden="true" /></span>
                      <span className="public-pages-copy"><strong>{label}</strong><small>{detail}</small></span>
                      <ArrowUpRight size={16} aria-hidden="true" />
                    </a>
                  ))}
                </div>
              </div>
            </>
          )}
          {auth && (
            <button
              type="button"
              ref={faceRef}
              className="header-help"
              aria-label="Ver recorrido guiado"
              title="Ver recorrido guiado"
              onClick={() => {
                closeMenus();
                window.dispatchEvent(new Event("atlas:tour-start"));
              }}
            >
              <Blobatar
                name="manu99"
                traits={{ shape: 0.99 }}
                hue={225}
                palette={{ head: "#3DE5F2", eye: "#061116" }}
                animate="always"
                size={40}
                expression={happy}
                title="Geo"
              />
            </button>
          )}
          {!publicView && links.map(([label, href]) => (
            <a key={label} href={href} onClick={closeMenus}>
              {label}
            </a>
          ))}
          <a
            className="button button-outline header-signin"
            href={signedIn ? "#/planes" : "#/acceso"}
            onClick={closeMenus}
            aria-label={signedIn ? `Tu cuenta, plan ${accountLabel}` : "Iniciar sesión"}
          >
            <LogIn size={17} aria-hidden="true" />
            {accountLabel}
          </a>
          {publicView && (
            <a className="button button-primary header-cta" href="#/sistema" onClick={closeMenus}>
              Explorar ATLAS <ArrowUpRight size={17} />
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}
