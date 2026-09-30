import React, { useEffect, useRef } from "react";

export function PlanGate({ reason, onClose }) {
  const ref = useRef(null);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;

  useEffect(() => {
    const node = ref.current;
    if (!node) return undefined;
    if (!node.open) node.showModal();
    function cancel(event) {
      event.preventDefault();
      closeRef.current();
    }
    node.addEventListener("cancel", cancel);
    return () => {
      node.removeEventListener("cancel", cancel);
      if (node.open) node.close();
    };
  }, []);

  return (
    <dialog className="plan-gate" ref={ref} aria-labelledby="plan-gate-title">
      <h2 id="plan-gate-title">
        Para acceder a esta función, consulta nuestros planes de pago.
      </h2>
      {reason === "quota" && <p>Tu plan llegó al número de análisis de este mes.</p>}
      <div className="plans-actions">
        <a className="button button-primary" href="#/planes" onClick={onClose}>
          Ver planes
        </a>
        <button type="button" className="button button-outline" onClick={onClose}>
          Seguir consultando
        </button>
      </div>
    </dialog>
  );
}
