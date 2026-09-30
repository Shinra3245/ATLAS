// Recorrido de bienvenida guiado por el triangulo.
// Texto 100% estatico: no llama a la API de Claude ni a ningun servicio.
// Cada paso resalta ("hace enfasis en") la seccion de la que habla.

const DONE_KEY = "atlas.tour.done";

// Cada paso define:
//  - id: identificador estable
//  - route: ruta (hash) en la que vive el paso
//  - target: selector CSS del elemento a resaltar (null = globo centrado)
//  - expression: gesto del triangulo (happy | idle | thinking | unsure)
//  - title: encabezado corto del globo
//  - body: explicacion
//  - emphasis: frase corta destacada ("enfasis")
//  - placement: preferencia de posicion del globo (bottom | top | center)
//  - gate: exige el campo del registro antes de Siguiente
//  - autoAdvanceOnLogin: si true, avanza solo cuando aparece la sesion
export const TOUR_STEPS = [
  {
    id: "greeting",
    route: "/",
    target: ".hero-copy h1",
    expression: "happy",
    title: "Hola",
    body: "Soy tu guía. Te acompaño a entrar y a conocer ATLAS.",
    emphasis: "Empecemos",
    placement: "bottom",
  },
  {
    id: "welcome",
    route: "/acceso",
    target: ".auth-intro h1",
    expression: "happy",
    title: "Inicia sesión",
    body: "Desde aquí entras con tu correo o creas una cuenta. Sigue mis pasos, uno a la vez.",
    emphasis: "Este es el acceso",
    placement: "bottom",
  },
  {
    id: "name",
    route: "/registro",
    target: ".auth-field:has(#auth-name)",
    gate: "name",
    expression: "idle",
    title: "Tu nombre",
    body: "Escribe tu nombre completo. Así queda asociada la cuenta.",
    emphasis: "Entre 2 y 100 caracteres",
    placement: "bottom",
  },
  {
    id: "email",
    route: "/registro",
    target: ".auth-field:has(#auth-email)",
    gate: "email",
    expression: "idle",
    title: "Tu correo",
    body: "Escribe un correo válido. Será tu usuario para entrar a ATLAS.",
    emphasis: "Un correo con formato válido",
    placement: "bottom",
  },
  {
    id: "institution",
    route: "/registro",
    target: ".auth-field:has(#auth-institution)",
    gate: "institution",
    expression: "idle",
    title: "Tu institución",
    body: "Si quieres, indica la institución u organización. Este dato es opcional.",
    emphasis: "Puedes dejarlo en blanco",
    placement: "bottom",
  },
  {
    id: "password",
    route: "/registro",
    target: ".auth-field:has(#auth-password)",
    gate: "password",
    expression: "idle",
    title: "Tu contraseña",
    body: "Crea una contraseña de al menos 8 caracteres, con letras y números.",
    emphasis: "Mínimo 8 caracteres",
    placement: "bottom",
  },
  {
    id: "confirm",
    route: "/registro",
    target: ".auth-field:has(#auth-confirm)",
    gate: "confirm",
    expression: "idle",
    title: "Confirma la contraseña",
    body: "Escríbela otra vez, igual que la anterior.",
    emphasis: "Las dos deben coincidir",
    placement: "bottom",
  },
  {
    id: "terms",
    route: "/registro",
    target: ".auth-terms",
    gate: "terms",
    expression: "idle",
    title: "El alcance",
    body: "Lee y acepta que ATLAS es una evaluación preliminar, no un dictamen.",
    emphasis: "Marca la casilla para continuar",
    placement: "top",
  },
  {
    id: "create",
    route: "/registro",
    target: ".auth-submit",
    expression: "happy",
    title: "Crea tu cuenta",
    body: "Pulsa Crear cuenta. Empiezas en el plan Basico y despues eliges como usar ATLAS. En cuanto se cree tu cuenta, continuo el recorrido.",
    emphasis: "Crear cuenta no cobra",
    placement: "top",
    autoAdvanceOnLogin: true,
  },
  {
    id: "plans",
    route: "/planes",
    target: ".plans-grid",
    expression: "happy",
    title: "Selecciona un plan",
    body: "Básico, Profesional o MAX. Elige el que vas a usar.",
    emphasis: "Tres planes",
    placement: "top",
  },
  {
    id: "map",
    route: "/sistema",
    target: ".workspace-map",
    expression: "idle",
    title: "Explora el territorio",
    body: "Este es el mapa. Elige una localidad de Irapuato o Celaya para evaluarla con evidencia.",
    emphasis: "Elige una localidad",
    placement: "bottom",
  },
  {
    id: "panel",
    route: "/sistema",
    target: ".workspace-panel",
    expression: "idle",
    title: "Analiza y compara",
    body: "Aqui eliges el tipo de proyecto y analizas la localidad. Luego puedes comparar dos localidades con los mismos criterios.",
    emphasis: "Mismos criterios para A y B",
    placement: "top",
  },
  {
    id: "sources",
    route: "/sistema",
    target: '.system-header a[href="#/fuentes"]',
    expression: "idle",
    title: "De donde viene el dato",
    body: "En Fuentes y Metodologia consultas de donde viene cada dato, su cobertura y como se lee la evidencia.",
    emphasis: "Toda la evidencia es rastreable",
    placement: "bottom",
  },
  {
    id: "assistant",
    route: "/sistema",
    target: ".guide-toggle",
    expression: "happy",
    title: "Estoy aqui para ayudarte",
    body: "Cuando tengas dudas, escribeme en el chat. Ya puedes empezar a explorar ATLAS.",
    emphasis: "Listo para comenzar",
    placement: "top",
  },
];

export function tourDone() {
  try {
    return localStorage.getItem(DONE_KEY) === "1";
  } catch {
    return false;
  }
}

export function markTourDone() {
  try {
    localStorage.setItem(DONE_KEY, "1");
  } catch {
    // Ignorar entornos sin localStorage.
  }
}

export function resetTour() {
  try {
    localStorage.removeItem(DONE_KEY);
  } catch {
    // Ignorar entornos sin localStorage.
  }
}
