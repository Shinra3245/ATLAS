import { useEffect, useState } from "react";

// Avoid flashing a loader for operations that finish before the delay.
export function useDelayedFlag(active, delay = 300) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    setVisible(false);
    if (!active || delay === 0) return;
    const timer = window.setTimeout(() => setVisible(true), delay);
    return () => window.clearTimeout(timer);
  }, [active, delay]);
  return active && (delay === 0 || visible);
}
