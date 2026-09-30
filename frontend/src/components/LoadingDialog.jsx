import React, { useEffect, useId, useRef } from "react";
import { GeoPulse } from "./GeoPulse";
import { useDelayedFlag } from "../hooks/useDelayedFlag";

export function LoadingDialog({ active, title, detail, steps, onCancel }) {
  const visible = useDelayedFlag(active, 1200);
  const dialogRef = useRef(null);
  const titleId = useId();

  useEffect(() => {
    if (!visible) return;
    const dialog = dialogRef.current;
    const previous = document.querySelector(".workspace-panel .button[aria-busy='true']") || document.activeElement;
    dialog.showModal();
    return () => {
      if (dialog.open) dialog.close();
      if (previous?.isConnected && !previous.disabled) previous.focus({ preventScroll: true });
      else document.querySelector(".workspace-panel")?.focus({ preventScroll: true });
    };
  }, [visible]);

  if (!visible) return null;
  return (
    <dialog ref={dialogRef} className="geo-pulse-dialog" aria-labelledby={titleId} onCancel={event => { event.preventDefault(); onCancel(); }}>
      <h2 id={titleId} className="geo-pulse-sr">{title}</h2>
      <GeoPulse title={title} detail={detail} variant="modal" steps={steps} />
      <button className="button button-outline geo-pulse-cancel" onClick={onCancel} autoFocus>Cancelar consulta</button>
    </dialog>
  );
}
