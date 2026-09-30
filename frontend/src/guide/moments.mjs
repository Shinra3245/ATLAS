const LOADING = {
  expression: "thinking",
  message: "Cargando localidades y fuentes…",
};
const CATALOG_ERROR = {
  expression: "unsure",
  message: "No se pudo cargar la información. Lee el aviso y vuelve a intentarlo.",
};
const ANALYSIS_ERROR = {
  expression: "unsure",
  message: "No se pudo completar. Lee el aviso y vuelve a intentarlo.",
};

function catalogMoment(catalogLoading, catalogError) {
  if (catalogError) return CATALOG_ERROR;
  if (catalogLoading) return LOADING;
  return null;
}

export function guideMoment({
  route,
  phase,
  busy = false,
  error = null,
  selected = false,
  catalogLoading = false,
  catalogError = null,
}) {
  if (route === "/fuentes") {
    return (
      catalogMoment(catalogLoading, catalogError) ?? {
        expression: "idle",
        prompt: "¿Quieres conocer de dónde viene cada dato?",
        message: "Consulta de dónde viene cada dato, su cobertura y sus límites.",
      }
    );
  }
  if (route === "/") {
    return {
      expression: "happy",
      prompt: "¿Quieres conocer por dónde empezar?",
      message:
        "Empieza en Explorar ATLAS. Elige una localidad de Irapuato o Celaya.",
    };
  }
  if (route === "/metodologia") {
    return {
      expression: "idle",
      prompt: "¿Quieres conocer cómo se lee la evidencia?",
      message:
        "Aquí se explica cómo se lee la evidencia, sin sustituir un estudio técnico.",
    };
  }
  if (route === "/estados") {
    return {
      expression: "idle",
      prompt: "¿Quieres conocer qué significa cada estado?",
      message:
        "Cada estado describe disponibilidad. La falta de datos no es ausencia de riesgo.",
    };
  }
  if (route === "/acceso") {
    return {
      expression: "happy",
      prompt: "¿Quieres conocer cómo entrar?",
      message:
        "Entra con tu correo o crea una cuenta. Al registrarte eliges un plan.",
    };
  }
  if (route === "/registro") {
    return {
      expression: "happy",
      prompt: "¿Quieres ayuda para crear tu cuenta?",
      message: "Completa tus datos, acepta el alcance preliminar y crea tu cuenta. Después podrás elegir un plan.",
    };
  }
  if (route === "/planes") {
    return {
      expression: "happy",
      prompt: "¿Quieres conocer cómo se elige un plan?",
      message:
        "Básico, Profesional o MAX. Esta demostración no cobra; puedes probar los planes.",
    };
  }
  if (route.startsWith("/ficha/")) {
    return {
      expression: "idle",
      prompt: "¿Quieres conocer qué resume esta ficha?",
      message: "Esta ficha resume valores, fuentes y límites de la localidad.",
    };
  }
  if (route !== "/sistema") {
    return {
      expression: "unsure",
      prompt: "¿Quieres conocer cómo volver?",
      message: "Esta vista no existe. Vuelve a la selección de una localidad.",
    };
  }
  const catalog = catalogMoment(catalogLoading, catalogError);
  if (catalog) return catalog;
  if (error) return ANALYSIS_ERROR;
  if (busy) {
    return {
      expression: "thinking",
      message:
        phase === "selectB"
          ? "Analizando B y comparando los mismos criterios…"
          : "Consultando evidencia para la localidad seleccionada…",
    };
  }
  if (phase === "selectA") {
    return selected
        ? {
          expression: "happy",
          prompt: "¿Quieres conocer el siguiente paso?",
          message: "Localidad lista. Pulsa analizar para ver la evidencia.",
        }
      : {
          expression: "idle",
          prompt: "¿Quieres conocer cómo elegir una localidad?",
          message:
            "Elige una localidad en el mapa o en la lista, y un tipo de proyecto.",
        };
  }
  if (phase === "selectB") {
    return selected
      ? {
          expression: "happy",
          prompt: "¿Quieres conocer si ya puedes comparar?",
          message: "Ya puedes comparar con los mismos criterios.",
        }
      : {
          expression: "unsure",
          prompt: "¿Quieres conocer cómo comparar?",
          message: "Elige otra localidad, distinta de A.",
        };
  }
  if (phase === "result") {
    return {
      expression: "happy",
      prompt: "¿Quieres conocer cómo leer este resultado?",
      message:
        "Lee cada factor con su estado. La falta de datos no es ausencia de riesgo.",
    };
  }
  if (phase === "comparison") {
    return {
      expression: "happy",
      prompt: "¿Quieres conocer cómo leer esta comparación?",
      message: "Misma lectura para A y B. No hay un ganador automático.",
    };
  }
  return {
    expression: "unsure",
    prompt: "¿Quieres conocer cómo volver?",
    message: "Esta vista no existe. Vuelve a la selección de una localidad.",
  };
}
