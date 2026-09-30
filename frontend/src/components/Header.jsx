import React, { useState } from "react";
import { Menu, X, ArrowUpRight } from "lucide-react";
import { Logo } from "./UI";

export function Header({ system = false }) {
  const [open, setOpen] = useState(false);
  const links = system
    ? [
        ["Inicio", "#/"],
        ["Metodología", "#/metodologia"],
        ["Fuentes", "#/fuentes"],
        ["Ayuda", "#/estados"],
      ]
    : [
        ["Inicio", "#/"],
        ["Cómo funciona", "#como-funciona"],
        ["Capacidades", "#capacidades"],
        ["Usuarios", "#usuarios"],
        ["Metodología", "#/metodologia"],
        ["Preguntas frecuentes", "#preguntas"],
      ];
  return (
    <header className={`site-header ${system ? "system-header" : ""}`}>
      <div className="header-inner">
        <Logo light={system} />
        <button
          className="icon-button menu-toggle"
          aria-label={open ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        <nav
          aria-label="Navegación principal"
          className={open ? "navigation navigation-open" : "navigation"}
        >
          {links.map(([label, href]) => (
            <a key={label} href={href} onClick={() => setOpen(false)}>
              {label}
            </a>
          ))}
          {!system && (
            <a className="button button-primary header-cta" href="#/sistema">
              Explorar ATLAS <ArrowUpRight size={17} />
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}
